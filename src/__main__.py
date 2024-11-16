import importlib
import sys
import os
import traceback

from unrealsdk import logging

# Get the ./Mods directory assuming we are in ./Borderlands/Binaries
mods_dir = os.path.abspath(os.path.dirname(__file__))

logging.info(f"Mods directory: '{mods_dir}'")

# Ensure that ./Mods/ is included in the module search path
if mods_dir not in sys.path:
    sys.path.insert(0, mods_dir)

# This needs to be imported after updating the search path probably a better way though...
import mods_base
import input_base

_full_traceback = False

for name in os.listdir(mods_dir):
    absolute_path = os.path.abspath(os.path.join(mods_dir, name))

    # Silently skip these
    if name.startswith(".") or name in (
        "__pycache__",
        "mods_base",
        "input_base",
        "unrealsdk",
        "pyunrealsdk",
    ):
        continue

    # Load directories containing __init__.py
    if not os.path.isdir(absolute_path) or "__init__.py" not in os.listdir(
        absolute_path
    ):
        continue

    try:
        importlib.import_module(f"{name}")
    except Exception:
        logging.error(f"Failed to import mod: {name}; {absolute_path}")
        tb = traceback.format_exc().split("\n")
        if _full_traceback:
            for line in tb:
                logging.error(line)
        else:
            logging.error(f"    {tb[-4].strip()}")
            logging.error(f"    {tb[-3].strip()}")
            logging.error(f"    {tb[-2].strip()}")


mods_base.mod_list.register_base_mod()