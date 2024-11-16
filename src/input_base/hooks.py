from unrealsdk.unreal import (
    UObject,
    UProperty,
    WrappedStruct,
    BoundFunction,
    UNameProperty
)
from unrealsdk.unreal import WrappedArray
from typing import List

from mods_base import hook
from mods_base import EInputEvent

from .core_input import dispatch_input_for_key
from threading import RLock
from .core_input import _lock


# - NOTE -
# This is not the most ideal solution and doesn't work for menu input. However,
# as a temporary solution this should work. Will likely want to make this
# native though since performance is a concern.
#

# These lists are very small so a linear search is fine
_keys_pressed_last_frame: List[str] = list()
_keys_pressed_this_frame: List[str] = list()
_pressed_keys_prop: UProperty | None = None


@hook(hook_func="Engine.PlayerInput:PlayerInput")
def on_player_input(
        obj: UObject,
        __args: WrappedStruct,
        __ret: any,
        __func: BoundFunction,
):
    global _keys_pressed_last_frame
    global _keys_pressed_this_frame
    global _pressed_keys_prop

    _keys_pressed_this_frame.clear()

    if _pressed_keys_prop is None:
        _pressed_keys_prop = obj.Class._find_prop("PressedKeys")

    keys: WrappedArray[UNameProperty] = obj._get_field(_pressed_keys_prop)
    if keys is None or len(keys) <= 0:
        _keys_pressed_last_frame.clear()  # Forgot this
        return

    for i in range(0, len(keys)):
        _keys_pressed_this_frame.append(keys[i].__str__())

    dispatch_events(_keys_pressed_this_frame)
    _keys_pressed_last_frame[:] = _keys_pressed_this_frame[:]


def dispatch_events(keys_this_frame: List[str]):
    global _keys_pressed_last_frame
    global _lock

    with _lock:
        # Keys Pressed this frame
        for key in keys_this_frame:
            if key in _keys_pressed_last_frame:
                continue
            key_name: str = str(key)
            dispatch_input_for_key(key_name, EInputEvent.IE_Pressed)

        # Keys Pressed last frame but not this frame
        for key in _keys_pressed_last_frame:
            if key in keys_this_frame:
                continue
            key_name: str = str(key)
            dispatch_input_for_key(key_name, EInputEvent.IE_Released)
