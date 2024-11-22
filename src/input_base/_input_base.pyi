
from collections.abc import Callable
from typing import NewType
from mods_base import EInputEvent

__all__: tuple[str, ...] = (
    "register_keybind"
    "deregister_keybind"
)

_KeybindHandle = NewType("_KeybindHandle", object)

def register_keybind(
        key: str,
        filter: EInputEvent,
        callback: Callable[[EInputEvent]]
) -> _KeybindHandle: ...

def deregister_keybind(handle: _KeybindHandle) -> None: ...

def deregister_by_key(key: str) -> None: ...
def deregister_all() -> None: ...