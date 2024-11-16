import argparse
import os
import sys
from zipfile import ZIP_DEFLATED, ZipFile

# - NOTE -
# This generates a PythonSDK-X.Y.Z.zip package for release. Embedding all required and some optional
# files but which are still useful.
#

__version__: str = "1.0.0"
__author__: str = "bl1sdk"
__zip_file__: str = f"PythonSDK-{__version__}.zip"
__exclude_paths__: list[str] = ["unrealsdk", "pyunrealsdk"]


################################################################################
# | UTILITY |
################################################################################

def is_valid_file(path):
    if not os.path.isfile(os.path.abspath(path)):
        raise argparse.ArgumentTypeError(f"File '{path}' doesn't exist")
    return os.path.abspath(path)


def is_valid_dir(path):
    if not os.path.isdir(os.path.abspath(path)):
        raise argparse.ArgumentTypeError(f"Directory '{path}' doesn't exist")
    return os.path.abspath(path)


################################################################################
# | PACKAGING RELEASE |
################################################################################

def package_release(args: argparse.Namespace):
    file_dir = os.path.dirname(__file__)
    zip_out_path = os.path.join(file_dir, "build", __zip_file__)

    sdk_build_dir = args.sdk_build_dir
    plugin_native_dll = args.plugins_native_dll

    PLUGINS_DIR = os.path.join("Binaries", "Plugins")
    MODS_DIR = os.path.join("Mods")

    with ZipFile(str(zip_out_path), "w", ZIP_DEFLATED, compresslevel=9) as zip_file:

        # Copy src directory
        for root, _, files in os.walk("./src"):
            root_path_parts = os.path.normpath(root).split(os.sep)
            if not args.include_hidden and any(p in root_path_parts for p in __exclude_paths__):
                continue

            for file in files:
                abs_file_path = os.path.join(root, file)
                src_rel_file_path = os.path.relpath(abs_file_path, file_dir)
                mods_rel_path = os.path.join("Mods", os.path.relpath(src_rel_file_path, "src"))
                zip_file.write(abs_file_path, arcname=mods_rel_path)

        # Copy SDK Build Files (Mirrors input directory)
        for root, _, files in os.walk(sdk_build_dir):
            for file in files:
                abs_file_path = os.path.join(root, file)
                rel_file_path = os.path.relpath(str(abs_file_path), sdk_build_dir)
                plugin_rel_path = os.path.join(PLUGINS_DIR, str(rel_file_path))
                zip_file.write(str(abs_file_path), arcname=plugin_rel_path)

        # https://github.com/Ry0511/plugin_loader (apple1417's doesn't work here)
        native_out_path = os.path.join("Binaries", os.path.basename(plugin_native_dll))
        zip_file.write(plugin_native_dll, arcname=native_out_path)

        # Environment File (optional)
        ENV_FILE_NAME = "unrealsdk.env"
        env_file = os.path.join(file_dir, ENV_FILE_NAME)
        if os.path.isfile(env_file):
            zip_file.write(env_file, arcname=os.path.join(PLUGINS_DIR, ENV_FILE_NAME))


################################################################################
# | ENTRY |
################################################################################

if __name__ == "__main__":
    import traceback
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Prepares a .zip release")

    # SDK Build Directory (best to use the install directory)
    parser.add_argument(
        "sdk_build_dir",
        type=is_valid_dir,
        help="pyunreal sdk build/install directory; "
             "Installed in ./Binaries/Plugins"
    )

    # Usually just dsound.dll but others do exist
    parser.add_argument(
        "plugins_native_dll",
        type=is_valid_file,
        help="pyunreal sdk build/install directory; "
             "Installed in ./Binaries"
    )

    # Skips over __exclude_paths__ when packaging ./src
    parser.add_argument(
        "--include-hidden",
        help="Whether or not to include 'unrealsdk' "
             "and 'pyunrealsdk' in the packaged mod "
             "directory",
        action="store_true",
        default=False,
    )
    args: argparse.Namespace = parser.parse_args()

    try:
        package_release(args)
    except Exception as err:
        print("Error: ", err, "\n")
        traceback.print_exc()
        sys.exit(1)
