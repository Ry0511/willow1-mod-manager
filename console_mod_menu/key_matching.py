from collections.abc import Iterable
from difflib import get_close_matches

from mods_base import Game

# region Known Keys

KNOWN_UE3_CONTROLLER_KEYS: set[str] = {
    "Gamepad_LeftStick_Down",
    "Gamepad_LeftStick_Left",
    "Gamepad_LeftStick_Right",
    "Gamepad_LeftStick_Up",
    "Gamepad_RightStick_Down",
    "Gamepad_RightStick_Left",
    "Gamepad_RightStick_Right",
    "Gamepad_RightStick_Up",
    "XboxTypeS_A",
    "XboxTypeS_B",
    "XboxTypeS_Back",
    "XboxTypeS_DPad_Down",
    "XboxTypeS_DPad_Left",
    "XboxTypeS_DPad_Right",
    "XboxTypeS_DPad_Up",
    "XboxTypeS_LeftShoulder",
    "XboxTypeS_LeftThumbStick",
    "XboxTypeS_LeftTrigger",
    "XboxTypeS_LeftTriggerAxis",
    "XboxTypeS_LeftX",
    "XboxTypeS_LeftY",
    "XboxTypeS_RightShoulder",
    "XboxTypeS_RightThumbStick",
    "XboxTypeS_RightTrigger",
    "XboxTypeS_RightTriggerAxis",
    "XboxTypeS_RightX",
    "XboxTypeS_RightY",
    "XboxTypeS_Start",
    "XboxTypeS_X",
    "XboxTypeS_Y",
}

KNOWN_UE4_CONTROLLER_KEYS: set[str] = {
    "Gamepad_DPad_Down",
    "Gamepad_DPad_Left",
    "Gamepad_DPad_Right",
    "Gamepad_DPad_Up",
    "Gamepad_FaceButton_Bottom",
    "Gamepad_FaceButton_Left",
    "Gamepad_FaceButton_Right",
    "Gamepad_FaceButton_Top",
    "Gamepad_LeftShoulder",
    "Gamepad_LeftThumbstick",
    "Gamepad_LeftTrigger",
    "Gamepad_LeftTriggerAxis",
    "Gamepad_LeftX",
    "Gamepad_LeftY",
    "Gamepad_RightShoulder",
    "Gamepad_RightThumbstick",
    "Gamepad_RightTrigger",
    "Gamepad_RightTriggerAxis",
    "Gamepad_RightX",
    "Gamepad_RightY",
    "Gamepad_Special_Left",
    "Gamepad_Special_Right",
}

KNOWN_KEYS: set[str] = {
    "A",
    "Add",
    "Apostrophe",
    "Asterix",
    "B",
    "BackSpace",
    "Backslash",
    "C",
    "CapsLock",
    "Comma",
    "D",
    "Decimal",
    "Delete",
    "Divide",
    "Down",
    "E",
    "Eight",
    "End",
    "Enter",
    "Equals",
    "Escape",
    "F",
    "F1",
    "F10",
    "F11",
    "F12",
    "F2",
    "F3",
    "F4",
    "F5",
    "F6",
    "F7",
    "F8",
    "F9",
    "Five",
    "Four",
    "G",
    "H",
    "Home",
    "Hyphen",
    "I",
    "Insert",
    "J",
    "K",
    "L",
    "Left",
    "LeftAlt",
    "LeftBracket",
    "LeftControl",
    "LeftMouseButton",
    "LeftShift",
    "M",
    "MiddleMouseButton",
    "MouseScrollDown",
    "MouseScrollUp",
    "MouseWheelAxis",
    "Multiply",
    "N",
    "Nine",
    "NumLock",
    "NumPadEight",
    "NumPadFive",
    "NumPadFour",
    "NumPadNine",
    "NumPadOne",
    "NumPadSeven",
    "NumPadSix",
    "NumPadThree",
    "NumPadTwo",
    "NumPadZero",
    "O",
    "One",
    "P",
    "PageDown",
    "PageUp",
    "Pause",
    "Period",
    "Q",
    "R",
    "Right",
    "RightAlt",
    "RightBracket",
    "RightControl",
    "RightMouseButton",
    "RightShift",
    "S",
    "ScrollLock",
    "Semicolon",
    "Seven",
    "Six",
    "Slash",
    "SpaceBar",
    "Subtract",
    "T",
    "Tab",
    "Three",
    "ThumbMouseButton",
    "ThumbMouseButton2",
    "Tilde",
    "Two",
    "U",
    "Up",
    "V",
    "W",
    "X",
    "Y",
    "Z",
    "Zero",
    *(KNOWN_UE3_CONTROLLER_KEYS if Game.get_tree() == Game.Willow2 else KNOWN_UE4_CONTROLLER_KEYS),
}

# endregion
# region Misspellings


def suggest_misspelt_key(invalid_key: str) -> Iterable[str]:
    """
    Given an invalid key name, suggest a misspelling.

    Args:
        invalid_key: The invalid key name.
    Returns:
        A list of possible misspellings (which may be empty).
    """
    return get_close_matches(invalid_key, KNOWN_KEYS)


# endregion
# region Symbols

SYMBOL_NAMES: dict[str, tuple[str, ...]] = {
    # Ignoring the symbols which require shift
    "-": ("Hyphen", "Subtract"),
    ",": ("Comma",),
    ";": ("Semicolon",),
    ".": ("Decimal", "Period"),
    "'": ("Apostrophe",),
    "[": ("LeftBracket",),
    "]": ("RightBracket",),
    "*": ("Asterix", "Multiply"),
    "/": ("Divide", "Slash"),
    "\\": ("Backslash",),
    "+": ("Add",),
    "=": ("Equals",),
    "~": ("Tilde",),
    "0": ("Zero", "NumPadZero"),
    "1": ("One", "NumPadOne"),
    "2": ("Two", "NumPadTwo"),
    "3": ("Three", "NumPadThree"),
    "4": ("Four", "NumPadFour"),
    "5": ("Five", "NumPadFive"),
    "6": ("Six", "NumPadSix"),
    "7": ("Seven", "NumPadSeven"),
    "8": ("Eight", "NumPadEight"),
    "9": ("Nine", "NumPadNine"),
}


def suggest_symbol_name(invalid_key: str) -> Iterable[str]:
    """
    Given an invalid key name, check if it's referencing to a symbol instead of its name.

    Args:
        invalid_key: The invalid key name.
    Returns:
        A list of possible names (which may be empty).
    """
    return SYMBOL_NAMES.get(invalid_key, ())


# endregion


def suggest_keys(invalid_key: str) -> Iterable[str]:
    """
    Given an invalid key name, suggest what the user might have intended.

    Args:
        invalid_key: The invalid key name.
    """
    return (
        *suggest_misspelt_key(invalid_key),
        *suggest_symbol_name(invalid_key),
    )
