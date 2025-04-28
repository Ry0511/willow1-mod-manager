# - NOTE - #####################################################################
#
# This file follows closely but not strictly to the Oak Mod Manager `__main__.py` file.
# You can find that here: https://github.com/bl-sdk/oak-mod-manager/blob/master/src/__main__.py
# the Oak Mod Manager is licensed under LGPL3 and so is the Willow1 Mod Manager; Willow1 Mod Manager
# also uses the name Willow Mod Manager. The project can be found at: https://github.com/Ry0511/willow1-mod-manager
# However, this link may become stale at somepoint depending on future developments.
#
# You should have received a copy of the LGPL3 along with the Willow1 Mod Manager.
# If not you can find it here: <https://www.gnu.org/licenses/>.
################################################################################

import traceback
import importlib
import sys

from typing import cast, Any, Union, Iterable, Mapping
from pathlib import Path

import unrealsdk  # noqa
from unrealsdk import logging, config


# TODO: Currently debugpy is not setup/available to use.

def get_cfg(key: str, default: Any | None = None) -> Any:
    node: Mapping[str, Any] = config
    for part in key.split("."):
        if part not in node:
            return default
        else:
            node = node[part]
    return node


# If true logs the entire trace; when false only the most recent call is logged.
FULL_TRACEBACKS: bool = get_cfg("modloader.full_trace", False)


################################################################################
# | UTILITIES |
################################################################################

def get_mod_directories() -> list[Path]:
    root_mods_dir = Path(__file__).parent.absolute()
    all_dirs = [root_mods_dir]

    extra_dirs = get_cfg("modloader.additional_mod_dirs")
    if extra_dirs is None or len(extra_dirs) == 0:
        return all_dirs

    for mod_dir in extra_dirs:

        p = Path(mod_dir)
        resolved: Union[Path, None] = None

        try:
            resolved = p.resolve()
        except Exception as ex:  # noqa
            logging.warning(f"Failed to resolve path '{p}': {ex}")

        if resolved is None:
            continue

        if not p.is_absolute():
            logging.warning(
                f"Path '{str(p)}' is not an absolute path;"
                f" Resolves to '{str(resolved)}'")

        if not resolved.is_dir():
            logging.warning(f"Additional mod directory is not a directory; '{str(resolved)}'")
            continue
        all_dirs.append(resolved)

    return all_dirs


def is_valid_mod_path(p: Path) -> bool:
    if not p.is_dir():
        return False

    name = p.name
    # Skip these directories
    if name.startswith(".") or name in (
            "__pycache__",
            "mods_base",
            "input_base",
            "keybinds",
            "pyunrealsdk",
            "unrealsdk"
    ):
        return False

    content: list[Path] = list(map(lambda x: x.name, p.iterdir()))
    if ".sdk_skip" in content or "__init__.py" not in content:
        return False

    return True


def load_mods_from_dir(mod_dir: Path) -> (int, int):
    mods_loaded = 0
    mods_failed = 0
    for p in cast(Iterable[Path], mod_dir.iterdir()):

        if p.name.lower() == "input_base":
            logging.info(f"Skipping input base '{p.name}' this directory can be"
                         f" deleted since it was renamed to 'keybinds'")
            continue

        if not is_valid_mod_path(p):
            continue

        module = p.name
        try:
            importlib.import_module(module)
            mods_loaded += 1

        except Exception as err:
            mods_failed += 1
            logging.error(f"Failed to load python module: '{module}'")
            tb = traceback.extract_tb(err.__traceback__)

            if not FULL_TRACEBACKS:
                tb = tb[-1:]

            logging.error("".join(traceback.format_exception_only(err)))
            logging.error("".join(traceback.format_list(tb)))

    return mods_loaded, mods_failed


def get_launch_args() -> list[str]:
    # Bit more complex than it needs to be tbh

    try:
        import ctypes
        from ctypes import wintypes

        # https://learn.microsoft.com/en-us/windows/win32/api/processenv/nf-processenv-getcommandlinew
        k32 = ctypes.windll.kernel32
        get_cmd_line_w = k32.GetCommandLineW
        get_cmd_line_w.restype = wintypes.LPWSTR

        # https://learn.microsoft.com/en-us/windows/win32/api/shellapi/nf-shellapi-commandlinetoargvw
        shell32 = ctypes.windll.shell32
        command_line_to_argv_w = shell32.CommandLineToArgvW
        command_line_to_argv_w.argtypes = [wintypes.LPCWSTR, ctypes.POINTER(ctypes.c_int)]
        command_line_to_argv_w.restype = ctypes.POINTER(wintypes.LPWSTR)

        # Parse args
        cmd_line = get_cmd_line_w()
        argc = ctypes.c_int(0)
        argv = command_line_to_argv_w(cmd_line, argc)
        args: list[str] = [argv[i] for i in range(argc.value)]

        # https://learn.microsoft.com/en-us/windows/win32/api/shellapi/nf-shellapi-commandlinetoargvw
        local_free = k32.LocalFree
        local_free.argtypes = [wintypes.HLOCAL]
        local_free.restype = wintypes.HLOCAL
        local_free(argv)

        return args

    except ImportError as ex:
        logging.error("Failed to import 'ctypes' module; Skipping checking args...")
        logging.error(ex)
        return []


################################################################################
# | MAIN CODE BLOCK |
################################################################################

args = list(map(lambda arg: arg.lower(), get_launch_args()[1:]))

if "-editor" not in args:
    logging.info("Loading mods normally...")

    # Might feel odd to iterate over this twice but importing a mod from one directory that relies on
    # another will cause issues. So before we do any importing we ensure all possible imports can
    # resolve.
    all_mod_directories = get_mod_directories()
    for p in all_mod_directories:
        if p not in sys.path:
            logging.info(f"Adding directory to search path: '{p}'")
            sys.path.append(str(p))

    import keybinds  # noqa
    from mods_base.mod_list import register_base_mod

    failed: int = 0
    succeeded: int = 0

    # Load all user mods
    for p in all_mod_directories:
        good, bad = load_mods_from_dir(p)
        succeeded += good
        failed += bad

    register_base_mod()
    logging.info(f"Loaded {succeeded} mods successfully, {failed} failed.")
else:
    logging.info("Editor launch argument provided; Not loading mods.")
