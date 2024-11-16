import inspect

from mods_base.keybinds import (
    EInputEvent,
    KeybindType,
    KeybindCallback_Event,
    KeybindCallback_NoArgs,
)

from typing import List, Dict
from threading import RLock

type CallbackType = KeybindCallback_Event | KeybindCallback_NoArgs

_lock: RLock = RLock()
_callback_map: Dict[str, List[KeybindType]] = {}


def add_keybind(bind: KeybindType) -> None:
    global _lock
    global _callback_map

    key = bind.key

    with _lock:
        if key not in _callback_map:
            _callback_map[key] = [bind]
        else:
            _callback_map[key].append(bind)


def remove_keybind(bind: KeybindType) -> None:
    global _lock
    global _callback_map
    key = bind.key

    with _lock:
        if key in _callback_map:
            _callback_map[key].remove(bind)


def dispatch_event(callback: CallbackType, event_type: EInputEvent) -> None:

    meta = inspect.signature(callback)

    match len(meta.parameters):
        case 0:
            callback()
        case 1:
            callback(event_type)
        case _:
            raise ValueError(f"Input callback type is unknown...")


def dispatch_input_for_key(key: str, event_type: EInputEvent) -> None:
    global _lock
    global _callback_map

    with _lock:
        if key not in _callback_map:
            return

        for bind in _callback_map[key]:
            if not bind.is_enabled:
                continue

            if bind.event_filter is None or bind.event_filter is event_type:
                dispatch_event(bind.callback, event_type)
                continue
