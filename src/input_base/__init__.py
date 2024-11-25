from functools import wraps
from typing import cast

from mods_base import KeybindType
from mods_base.keybinds import KeybindCallback_Event, KeybindCallback_NoArgs
from mods_base.mod_list import base_mod
from ._input_base import register_keybind, deregister_keybind

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
    self.is_enabled = True

    if self.key is None or self.callback is None:
        return

    if self.event_filter is None:
        handle = register_keybind(
            self.key,
            self.event_filter,
            True,
            cast(KeybindCallback_Event, self.callback)
        )
    else:
        handle = register_keybind(
            self.key,
            self.event_filter,
            True,
            cast(KeybindCallback_NoArgs, self.callback)
        )

    self._native_handle = handle


KeybindType.enable = enable_keybind


@wraps(KeybindType.disable)
def disable_keybind(self: KeybindType) -> None:
    self.is_enabled = False  # Always disable

    handle = getattr(self, "_native_handle", None)
    if handle is None:
        return

    deregister_keybind(handle)
    self._native_handle_ = None


KeybindType.disable = disable_keybind


@wraps(KeybindType._rebind)
def rebind_keybind(self: KeybindType, new_key: str | None) -> None:
    handle = getattr(self, "_native_handle", None)
    if handle is not None:
        deregister_keybind(handle)

    if self.is_enabled:
        self.key = new_key
        enable_keybind(self)


KeybindType._rebind = rebind_keybind

base_mod.components.append(base_mod.ComponentInfo("Input Base", __version__))
