# BL1 PythonSDK Mod Manager

#### PythonSDK Mod manager for Borderlands 1.

- - -

# Preface

## This will not work for the Enhanced version of the game

The SDK may be flagged as a virus by some antivirus programs. If this happens, you will need to 
add an exception to prevent it from being blocked or removed.

- - -

# Installation

1. Download the latest `PythonSDK-Release-X-Y-Z.zip` from [releases](https://github.com/Ry0511/willow1-mod-manager/releases)
2. Extract the contents of the zip file to your games directory `C:\Program Files (x86)\Steam\steamapps\common\Borderlands`
   - Replace files if needed
3. Run your Borderlands game
4. Once in the main menu type `mods` into the console (Tilde by default will open the console)
   - If you see `>>> mods <<<` it means the SDK is not running/working
   - If you see something like `ModMenu | ...` then the SDK is running and working
5. You can find mods [here](https://github.com/Ry0511/bl1-sdk-mods)
   - Installation is to copy the contents of the `the_mods_name.zip` to your `sdk_mods` directory or any of your `additional_mod_dirs`

## Linux; aka I use arch btw

When launching with wine ensure these environment variables are set:
`WINEDLLOVERRIDES="dsound=n,b" %command% -nosplash`

## Configuring

The file `Borderlands/Binaries/Plugins/unrealsdk.toml` contains a variety of useful things for both 
mod developers and mod users. The primary thing is the `additional_mod_dirs` which lets you specify 
external places to load mods from. This is a comma separated list of directories to load mods from.

```toml
[modloader]
# ...
additional_mod_dirs = [
    # "G:/Games/BL1_Modding/bl1_sdk_mods/src/py",  # / or \\ can be used \ alone can not.
   "Path/To/Folder/WithMods",
   "Another/Path/To/Folder",
]
```

- - -

# Changelog

## v1.1.0

### Changes
- Changed where the PythonSDK is downloaded from (you are here dumb dumb)

### Fixes
- Hooking some functions would cause a crash due to not synchronising `CallFunction` (don't copy code kids even if its in the same repo lol)
- Main mods directory has been renamed from `Mods` to `sdk_mods`
- Mod loader would log `Invalid Mod Path` excessively

- - -

## v1.0.0

### Changes
- Change by apple1417; `unrealsdk.env` became `unrealsdk.toml`
- Main mods directory is `/Borderlands/Mods/`
- The input system `input_base` is now native C/C++ module

- - -

## v0.0.0

Initial release; didn't even have a repo for the mod manager :sadge:

- - -