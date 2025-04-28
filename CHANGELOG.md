
# v1.2.0

- input_base has been renamed to keybinds to keep things inline with other games
- Mods Base
  - URL's have now been setup for so you should be prompted when new releases are available... 
     You can also just look in the discord.
- Console Mod Menu
  - You can now bind a button via a button press
- Fixed WeakPointers not working due to incorrect UObject layout
- ui_utils is now directly apart of the mod manager thanks to RedxYeti
- Known Issue: Hooking network functions can cause a crash; This is being looked into.

# v1.1.0

- Changed where the PythonSDK is downloaded from [willow1-mod-manager](https://github.com/Ry0511/willow1-mod-manager/releases)
- Fixed a bug where CallFunction was not being synchronised which caused crashes
- Fixed main mod directory name to `sdk_mods` was `Mods`
- Fixed excessive logging from mod loader leading to confusion

# v1.0.0

- Environment files `.env` have been replaced with `.toml` files
- Main mod directory is now at `.../Borderlands` instead of `.../Borderlands/Binaries`
- unrealsdk.toml file contains `additional_mod_dirs` property for loading mods from any directory
- `input_base` is now a native python module
- Other stuff I forgot about

# v0.0.0

- Base SDK Release