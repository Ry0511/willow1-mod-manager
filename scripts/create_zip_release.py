import os
import argparse
from enum import Enum
from os import path
from typing import AnyStr
from typing import overload
from types import SimpleNamespace
from zipfile import ZipFile, ZIP_DEFLATED, ZIP_STORED


class BuildType(Enum):
    Empty = ""
    Debug = "Debug"
    Release = "Release"
    RelWithDebInfo = "RelWithDebInfo"
    Unknown = "Custom"


    def file_prefix(self):
        if self is BuildType.Empty:
            return ""
        else:
            return f"-{self.name}"


################################################################################
# | UTILITY |
################################################################################


def init_args_from_cmake() -> argparse.Namespace | None:
    from argparse import ArgumentParser

    def is_valid_file(in_path: AnyStr) -> AnyStr:
        if not path.isfile(path.abspath(in_path)):
            raise argparse.ArgumentTypeError(f"File '{in_path}' doesn't exist")
        return path.abspath(in_path)


    def dir_exists(in_path: AnyStr) -> AnyStr:
        if not path.isdir(path.abspath(in_path)):
            raise argparse.ArgumentTypeError(f"Directory '{in_path}' doesn't exist")
        return path.abspath(in_path)


    def dir_not_empty(in_path: AnyStr) -> AnyStr:
        abs_path = dir_exists(in_path)
        contents = os.listdir(abs_path)
        if not contents or len(contents) == 0:
            raise argparse.ArgumentTypeError(f"Directory '{abs_path}' is empty")
        return abs_path


    def parse_build_type(build_type: str) -> BuildType:
        try:
            return BuildType(build_type.strip())
        except KeyError:
            return BuildType.Unknown


    parser = ArgumentParser(description="Prepares a .zip release")
    parser.add_argument("--version", required=True)
    parser.add_argument("--install-dir", type=dir_not_empty, required=True)
    parser.add_argument("--build-type", type=parse_build_type, required=True)
    parser.add_argument("--output-dir", type=dir_exists, required=True)

    try:
        args: argparse.Namespace = parser.parse_args()
        return args
    except Exception as e:
        print("[ERROR] ~ ", e)
        return None


def parse_args_from_cmake(args: argparse.Namespace | None = None) -> SimpleNamespace:
    if args is None:
        args = init_args_from_cmake()
        if args is None:
            exit(1)

    zip_file_name = f"PythonSDK{args.build_type.file_prefix()}-{args.version}.zip"

    cfg = SimpleNamespace()
    cfg.version = args.version
    cfg.build_type = args.build_type
    cfg.output_dir = args.output_dir
    cfg.install_dir = args.install_dir
    cfg.zip_file_name = zip_file_name
    cfg.zip_file_out = path.join(args.output_dir, zip_file_name)
    return cfg


################################################################################
# | PACKAGING RELEASE |
################################################################################

def package_dir_into_zip(
        dir_path: str,
        zip_file: ZipFile,
        base_path: str = "",
) -> None:
    """
    Packages the provided directory into the provided zip file whilst mirroring the input
    directory structure.
    :param dir_path: Input directory
    :param zip_file: Output zip file
    :param base_path: Prefix path to prepend to output files
    """
    for root, _, files in os.walk(dir_path):
        for file in files:
            abs_path = path.join(root, file)
            rel_path = path.relpath(abs_path, dir_path)
            out_path = path.join(base_path, rel_path)
            zip_file.write(abs_path, arcname=out_path)


def package_release(cfg: SimpleNamespace):
    compression = ZIP_DEFLATED if cfg.build_type is not BuildType.Debug else ZIP_STORED
    with ZipFile(cfg.zip_file_out, "w", compression, compresslevel=9) as zip_file:
        package_dir_into_zip(cfg.install_dir, zip_file)


################################################################################
# | ENTRY |
################################################################################

if __name__ == "__main__":

    cfg: SimpleNamespace = parse_args_from_cmake()

    print("\n[CONFIGURATION]")
    print(f"VERSION        : {cfg.version}")
    print(f"BUILD_TYPE     : {cfg.build_type}")
    print(f"OUTPUT_DIR     : {cfg.output_dir}")
    print(f"SDK_INSTALL_DIR: {cfg.install_dir}")
    print(f"ZIP_FILE_NAME  : {cfg.zip_file_name}")
    print(f"ZIP_FILE_OUT   : {cfg.zip_file_out}")

    package_release(cfg)
    zip_stats = os.stat(cfg.zip_file_out)
    zip_size = zip_stats.st_size / (1024 * 1024)
    print(f"Packaged zip release ({zip_size:.2f}mb)")
