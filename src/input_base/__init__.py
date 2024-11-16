from mods_base import KeybindType
from mods_base.mod_list import base_mod

from .hooks import on_player_input
from .core_input import add_keybind, remove_keybind

from functools import wraps

################################################################################
# | MODS METADATA |
################################################################################

__all__: tuple[str, ...] = (
    "__author__",
    "__version__",
    "__version_info__",
)

__version_info__: tuple[int, int] = (1, 1)
__version__: str = f"{__version_info__[0]}.{__version_info__[1]}"
__author__: str = "-Ry"

################################################################################
# | WRAPPING |
################################################################################


@wraps(KeybindType.enable)
def enable_keybind(self: KeybindType) -> None:
    # logging.info(f"Keybind Enable: {self.key}")

    if self.key is None or self.callback is None:
        return

    self.is_enabled = True  # Only enable if valid key & callback
    add_keybind(self)


KeybindType.enable = enable_keybind


@wraps(KeybindType.disable)
def disable_keybind(self: KeybindType) -> None:
    # logging.info(f"Keybind Disable: {self.key}")
    self.is_enabled = False  # Always disable

    if self.key is None or self.callback is None:
        return

    remove_keybind(self)


KeybindType.disable = disable_keybind

# Enable input hook
on_player_input.enable()

base_mod.components.append(base_mod.ComponentInfo("Input Base", __version__))
