from unrealsdk.unreal import UObject, WrappedStruct, BoundFunction, UNameProperty
from typing import List

from mods_base import hook
from mods_base import EInputEvent

from .core_input import dispatch_input_for_key

# - NOTE -
# This is not the most ideal solution and doesn't work for menu input. However,
# as a temporary solution this should work. Will likely want to make this
# native though since performance is a concern.
#

_keys_pressed_last_frame: List[str] = list()


@hook(hook_func="Engine.PlayerInput:PlayerInput")
def on_player_input(
    obj: UObject,
    __args: WrappedStruct,
    __ret: any,
    __func: BoundFunction,
):
    global _keys_pressed_last_frame
    keys_pressed_this_frame: List[str] = list(map(str, obj.PressedKeys))
    dispatch_events(keys_pressed_this_frame)
    _keys_pressed_last_frame = keys_pressed_this_frame


def dispatch_events(keys_this_frame: List[str]):
    global _keys_pressed_last_frame

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
