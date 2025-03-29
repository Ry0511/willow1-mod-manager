import os
import shutil
import sys
import tomllib
from os import path
from types import SimpleNamespace
import zipfile

from create_zip_release import parse_args_from_cmake


def validate_files(cfg: SimpleNamespace) -> bool:
    valid_files = True


    def is_valid_dir(p, msg="Directory doesn't exist") -> bool:
        if not path.isdir(p):
            print(msg, f"; '{p}'")
            return False
        return True


    if (  # Just ensure we have the right borderlands directory
            not is_valid_dir(cfg.bl_root_dir, "Borderlands directory doesn't exist;")
            or not is_valid_dir(path.join(cfg.bl_root_dir, "Binaries"))
            or not is_valid_dir(path.join(cfg.bl_root_dir, "WillowGame"))
    ):
        valid_files = False

    if not path.isfile(cfg.zip_file_out):
        print(f"Zip file doesn't exist; '{cfg.zip_file_out}'")

    # These don't need to exist
    for p in cfg.bl_delete_list:
        print(f"[WARNING] Path is on delete list; '{p}'")

    # For sanity reasons enforce absolute & existence
    for p in cfg.bl_install_mods:
        if not path.isabs(p) or not path.isdir(p):
            print(f"[WARNING] Install mods directory not absolute or doesn't exist; 'p'")
            valid_files = False
        else:
            print(f"[INFO] Install Mod: '{p}'")

    return valid_files


def parse_toml(cfg: SimpleNamespace, toml_file) -> None:
    with open(toml_file, 'rb') as f:
        toml = tomllib.load(f)
        cfg.bl_root_dir = path.abspath(toml['borderlands']['root_dir'])
        cfg.bl_delete_list = list(map(lambda p: path.join(cfg.bl_root_dir, path.normpath(p)),
                                      toml['borderlands']['delete_list']))
        cfg.bl_dry_run = bool(toml['borderlands']['dry_run'])
        cfg.bl_install_mods = toml['borderlands']['install_mods']


if __name__ == "__main__":

    cur_dir = path.dirname(__file__)
    toml_file = path.join(cur_dir, str(path.basename(__file__)).replace('.py', '.toml'))

    if not path.isfile(toml_file):
        print(f"Toml file: '{toml_file}' doesn't exist skipping post package.")
        exit(0)

    cfg: SimpleNamespace = parse_args_from_cmake()
    parse_toml(cfg, toml_file)
    print(cfg)

    if not validate_files(cfg) or bool(cfg.bl_dry_run):
        print("[DRY_RUN] Exiting...")
        sys.exit(0)

    # Delete files and or directories
    print("\nDeleting files and directories in delete list...")
    for p in cfg.bl_delete_list:
        try:
            if path.isdir(p):
                shutil.rmtree(p)
                print(f"Deleted directory; '{p}'")

            elif path.isfile(p):
                os.remove(p)
                print(f"Deleted file; '{p}'")

        except Exception as err:
            print(f"Error deleting path; '{p}'")
            print(err)

    # Will replace existing.
    print("\nExtracting zip file...")
    print(cfg.zip_file_out)
    print(cfg.bl_root_dir)
    with zipfile.ZipFile(cfg.zip_file_out) as zip_file:
        zip_file.extractall(cfg.bl_root_dir)

    # NOTE: this assumes `Mods` is a direct child of bl_root_dir
    # mods_dir = path.join(cfg.bl_root_dir, 'sdk_mods')
    # if not path.isdir(mods_dir):
    #     print(f"Mods directory doesn't exist after extracting; '{mods_dir}'")
    #     exit(1)

    # for p in cfg.bl_install_mods:
    #
    #     dest = mods_dir
    #     if not p.endswith('/') and not p.endswith('\\'):
    #         dest = path.join(dest, path.basename(p))
    #
    #     print(f"[INFO] ~ Installing Mod; '{p}' into '{dest}'")
    #     shutil.copytree(p, dest, dirs_exist_ok=True)
