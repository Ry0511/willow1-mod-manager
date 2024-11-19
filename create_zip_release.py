import argparse
from enum import Enum
import os
from os import path
from typing import AnyStr
from zipfile import ZipFile, ZIP_DEFLATED


class BuildType(Enum):
    Empty = ""
    Debug = "Debug"
    Release = "Release"
    Unknown = "Custom"

    def file_prefix(self):
        if self is BuildType.Empty:
            return ""
        else:
            return f"-{self.name}"


################################################################################
# | UTILITY |
################################################################################

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


################################################################################
# | PACKAGING RELEASE |
################################################################################

VERSION: str
BUILD_TYPE: BuildType
OUTPUT_DIR: str
MODS_DIR: str
SDK_INSTALL_DIR: str
ZIP_FILE_NAME: str
ZIP_FILE_OUT: str


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


def package_release():
    with ZipFile(ZIP_FILE_OUT, "w", ZIP_DEFLATED, compresslevel=9) as zip_file:
        package_dir_into_zip(MODS_DIR, zip_file, base_path="Mods")
        package_dir_into_zip(SDK_INSTALL_DIR, zip_file)


################################################################################
# | ENTRY |
################################################################################

if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Prepares a .zip release")
    parser.add_argument("--version", required=True)
    parser.add_argument("--sdk-install-dir", type=dir_not_empty, required=True)
    parser.add_argument("--mods-dir", type=dir_not_empty, required=True)
    parser.add_argument("--build-type", type=parse_build_type, required=True)
    parser.add_argument("--output-dir", type=dir_exists, required=True)

    try:
        args: argparse.Namespace = parser.parse_args()
    except Exception as e:
        print("ERROR PARSING ARGS: ", e)
        exit(1)

    VERSION = args.version
    BUILD_TYPE = args.build_type
    OUTPUT_DIR = args.output_dir
    MODS_DIR = args.mods_dir
    SDK_INSTALL_DIR = args.sdk_install_dir
    ZIP_FILE_NAME = f"PythonSDK{BUILD_TYPE.file_prefix()}-{VERSION}.zip"
    ZIP_FILE_OUT = path.join(OUTPUT_DIR, ZIP_FILE_NAME)

    print("\n[CONFIGURATION]")
    print(f"VERSION        : {VERSION}")
    print(f"BUILD_TYPE     : {BUILD_TYPE}")
    print(f"OUTPUT_DIR     : {OUTPUT_DIR}")
    print(f"MODS_DIR       : {MODS_DIR}")
    print(f"SDK_INSTALL_DIR: {SDK_INSTALL_DIR}")
    print(f"ZIP_FILE_NAME  : {ZIP_FILE_NAME}")
    print(f"ZIP_FILE_OUT   : {ZIP_FILE_OUT}")

    package_release()
    zip_stats = os.stat(ZIP_FILE_OUT)
    zip_size = zip_stats.st_size / (1024 * 1024)
    print(f"Packaged zip release ({zip_size:.2f}mb)")
