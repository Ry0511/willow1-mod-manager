from collections.abc import Callable
from typing import NewType, overload

from unrealsdk.hooks import Block
from mods_base import EInputEvent

__all__: tuple[str, ...] = (
    "register_keybind"
    "deregister_keybind"
)

_KeybindHandle = NewType("_KeybindHandle", object)
type _BlockSignal = None | Block | type[Block]


################################################################################
# | REGISTER KEYBINDS |
################################################################################

@overload
def register_keybind(
        key: str,
        filter: None,
        is_gameplay_bind: bool,
        callback: Callable[[EInputEvent], _BlockSignal]
) -> _KeybindHandle: ...
@overload
def register_keybind(
        key: str,
        filter: EInputEvent,
        is_gameplay_bind: bool,
        callback: Callable[[], _BlockSignal]
) -> _KeybindHandle: ...
@overload
def register_keybind(
        key: None,
        filter: EInputEvent,
        is_gameplay_bind: bool,
        callback: Callable[[str], _BlockSignal]
) -> _KeybindHandle: ...
@overload
def register_keybind(
        key: None,
        filter: None,
        is_gameplay_bind: bool,
        callback: Callable[[EInputEvent, str], _BlockSignal]
) -> _KeybindHandle: ...
def register_keybind(
        key: str | None,
        filter: EInputEvent | None,
        is_gameplay_bind: bool,
        callback: Callable[[...], _BlockSignal]
) -> _KeybindHandle: ...


################################################################################
# | DEREGISTER KEYBINDS |
################################################################################

def deregister_keybind(handle: _KeybindHandle) -> None: ...


def deregister_by_key(key: str) -> None: ...


def deregister_all() -> None: ...
