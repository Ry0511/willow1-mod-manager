cmake_minimum_required(VERSION 3.25)
project(
        willow_mod_manager
        VERSION 1.2.0
        DESCRIPTION "BL1 PythonSDK Mod Manager"
)

add_custom_target(${PROJECT_NAME})

################################################################################
# | DEPENDENCIES |
################################################################################

# Base install directory is */Binaries/Plugins however we need to place things above this for a
#  correct directory layout
get_filename_component(WMM_INSTALL_ROOT "${CMAKE_INSTALL_PREFIX}/../../" ABSOLUTE)
set(WMM_INSTALL_DIR_MODS "${WMM_INSTALL_ROOT}/sdk_mods")
set(WMM_INSTALL_DIR_BINARIES "${WMM_INSTALL_ROOT}/Binaries")
set(WMM_INSTALL_DIR_PLUGINS "${WMM_INSTALL_ROOT}/Binaries/Plugins")

# Vendor dependencies
add_subdirectory(./vendor/pyunrealsdk)
add_subdirectory(./vendor/plugin_loader EXCLUDE_FROM_ALL)

add_dependencies(${PROJECT_NAME} proxy_dsound pyunrealsdk)

# Probably should make this process a function
pyunrealsdk_add_module(keybinds src/keybinds/keybinds.cpp)
install(TARGETS keybinds DESTINATION ${WMM_INSTALL_DIR_MODS}/keybinds)
add_dependencies(${PROJECT_NAME} keybinds)

################################################################################
# | PACKAGING MOD MANAGER |
################################################################################

install(TARGETS proxy_dsound RUNTIME DESTINATION ${WMM_INSTALL_DIR_BINARIES})
install(DIRECTORY "./vendor/pyunrealsdk/stubs/"
        DESTINATION "${CMAKE_CURRENT_SOURCE_DIR}/src"
        PATTERN Readme.md EXCLUDE)
install(FILES "unrealsdk.toml" DESTINATION ${WMM_INSTALL_DIR_PLUGINS})
install(FILES "LICENSE" DESTINATION ${WMM_INSTALL_DIR_MODS})

set( # When installing a mod some files are just not needed.
        WMM_MOD_INSTALL_EXCLUDE_LIST
        PATTERN ".idea" EXCLUDE
        PATTERN ".git" EXCLUDE
        PATTERN ".gitignore" EXCLUDE
        PATTERN ".github" EXCLUDE
)

install( # Install contents excluding some file types since
        DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/src/"
        DESTINATION ${WMM_INSTALL_DIR_MODS}
        ${WMM_MOD_INSTALL_EXCLUDE_LIST}
        PATTERN "example_mod" EXCLUDE
)

################################################################################
# | OPTIONAL INSTALL ARTIFACTS |
################################################################################

option(WMM_INSTALL_EXAMPLE_MOD "Installs the example mod into the ./sdk_mods directory" OFF)
option(WMM_INSTALL_STUBS "Installs stubs for pyunrealsdk and unrealsdk (./src and ./sdk_mods)" ON)

if (WMM_INSTALL_EXAMPLE_MOD)
    install(
            DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/src/example_mod"
            DESTINATION ${WMM_INSTALL_DIR_MODS}
            ${WMM_MOD_INSTALL_EXCLUDE_LIST}
    )
endif ()

if (WMM_INSTALL_STUBS)
    install( # Install stubs into install directory
            DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/vendor/pyunrealsdk/stubs/"
            DESTINATION ${WMM_INSTALL_DIR_MODS}
            PATTERN "Readme.*" EXCLUDE
            ${WMM_MOD_INSTALL_EXCLUDE_LIST}
    )
    install( # Install stubs into source directory
            DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/vendor/pyunrealsdk/stubs/"
            DESTINATION "${CMAKE_CURRENT_SOURCE_DIR}/src/"
            PATTERN "Readme.*" EXCLUDE
            ${WMM_MOD_INSTALL_EXCLUDE_LIST}
    )
endif ()

################################################################################
# | AUTO PACKAGER |
################################################################################

# This assumes the directory structure for the sdk-install-dir is the required i.e., Binaries/Plugins
find_package(Python3 REQUIRED)

set(WMM_PY_PACKAGE_ARGS
        --version "\"${CMAKE_PROJECT_VERSION}\""
        --install-dir "\"${WMM_INSTALL_ROOT}\""
        --build-type "\"${CMAKE_BUILD_TYPE}\""
        --output-dir "\"${CMAKE_CURRENT_SOURCE_DIR}/build\""
)

# Packages the install directory into a Release zip
add_custom_target(
        package_willow_mod_manager
        COMMAND
        "${Python3_EXECUTABLE}"
        "${CMAKE_CURRENT_SOURCE_DIR}/scripts/create_zip_release.py"
        ${WMM_PY_PACKAGE_ARGS}
        WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
)

# Optional Unpackage to game directory script see ./scripts/post_create_zip_release.toml.template
add_custom_command(
        TARGET package_willow_mod_manager
        POST_BUILD
        COMMAND
        "${Python3_EXECUTABLE}"
        "${CMAKE_CURRENT_SOURCE_DIR}/scripts/post_create_zip_release.py"
        ${WMM_PY_PACKAGE_ARGS}
        WORKING_DIRECTORY
        "${CMAKE_CURRENT_SOURCE_DIR}"
)
