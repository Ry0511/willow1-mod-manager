# - NOTE - #####################################################################
#
# This file follows closely but not strictly to the Oak Mod Manager `__main__.py` file.
# You can find that here: https://github.com/bl-sdk/oak-mod-manager/blob/master/src/__main__.py
# the Oak Mod Manager is licensed under LGPL3 and so is the Willow1 Mod Manager; Willow1 Mod Manager
# also uses the name Willow Mod Manager. The project can be found at: https://github.com/Ry0511/willow1-mod-manager
# However, this link may become stale at somepoint depending on future developments.
#
# You should have received a copy of the GNU General Public License along with the
# Willow1 Mod Manager; If not, see <https://www.gnu.org/licenses/>.
################################################################################

import traceback
import importlib
import sys
from pathlib import Path

import unrealsdk  # noqa
from unrealsdk import logging, config


# TODO: Currently debugpy is not setup/available to use.

def get_cfg(key: str, default: any) -> any:
    node = config
    for part in key.split("."):
        try:
            node = node[part]
        except KeyError:
            return default
    return node


# If true logs the entire trace; when false only the most recent call is logged.
FULL_TRACEBACKS: bool = get_cfg("modloader.full_trace", False)
FULL_LOGGING: bool = get_cfg("modloader.full_logging", False)


def log(msg: str, fn: callable = logging.info):
    if not FULL_LOGGING:
        return
    fn(msg)


################################################################################
# | UTILITIES |
################################################################################

def get_mod_directories() -> list[Path]:
    root_mods_dir = Path(__file__).parent.absolute()
    all_dirs = [root_mods_dir]

    for p in map(Path, get_cfg("modloader.additional_mod_dirs", [])):
        if not p.is_dir():
            log(f"Invalid directory: '{p}'")
        all_dirs.append(p)

    return all_dirs


def is_valid_mod_path(p: Path) -> bool:
    if not p.is_dir():
        return False

    # Skip these directories
    if p.name in (".", "__pycache__", "mods_base", "input_base", "pyunrealsdk", "unrealsdk"):
        return False

    content: list[Path] = list(map(lambda x: x.name, p.iterdir()))
    if ".pysdk_exclude" in content or "__init__.py" not in content:
        return False

    return True


def load_mods_from_dir(mod_dir: Path) -> None:
    for p in mod_dir.iterdir():
        if not is_valid_mod_path(p):
            logging.info(f"Invalid Mod Path: '{p}'")
            continue

        module = p.name
        try:
            importlib.import_module(module)
        except Exception as err:
            logging.error(f"Failed to load python module: '{module}'")
            tb = traceback.extract_tb(err.__traceback__)

            if not FULL_TRACEBACKS:
                tb = tb[-1:]

            logging.error("".join(traceback.format_exception_only(err)))
            logging.error("".join(traceback.format_list(tb)))


################################################################################
# | MAIN CODE BLOCK |
################################################################################

# Might feel odd to iterate over this twice but importing a mod from one directory that relies on
# another will cause issues. So before we do any importing we ensure all possible imports can
# resolve.
all_mod_directories = get_mod_directories()
for p in all_mod_directories:
    if p not in sys.path:
        log(f"Adding directory to search path: '{p}'")
        sys.path.append(str(p))

import input_base  # noqa
from mods_base import mod_list

for p in all_mod_directories:
    load_mods_from_dir(p)

mod_list.register_base_mod()

# Explicitly remove these, not entirely required but might as well.
del all_mod_directories
del FULL_LOGGING
del FULL_TRACEBACKS
del log
del get_cfg
