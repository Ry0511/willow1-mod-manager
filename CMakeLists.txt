cmake_minimum_required(VERSION 3.23)
project(
        willow_mod_manager
        VERSION 1.1.0
        DESCRIPTION "BL1 PythonSDK Mod Manager"
)

# TODO: Cleanup this file.

add_custom_target(${PROJECT_NAME})

################################################################################
# DEPENDENCIES
################################################################################

# Default install directory is install/Binaries/Plugins
set(WMM_INSTALL_ROOT "${CMAKE_INSTALL_PREFIX}/../../")

add_subdirectory(./vendor/pyunrealsdk)

# Need to exclude this since we don't want its install dependencies
add_subdirectory(./vendor/plugin_loader EXCLUDE_FROM_ALL)

add_dependencies(${PROJECT_NAME} proxy_dsound pyunrealsdk)

# Probably should make this process a function
pyunrealsdk_add_module(_input_base src/input_base/_input_base.cpp)
install(TARGETS _input_base DESTINATION ${WMM_INSTALL_ROOT}/Mods/input_base)
add_dependencies(${PROJECT_NAME} _input_base)

################################################################################
# PACKAGING MOD MANAGER
################################################################################

# Honestly, might be a better idea to avoid the install stuff and just have a build target which
#  packages everything we need. Then just give that to the packager script.

install(TARGETS proxy_dsound RUNTIME DESTINATION ${WMM_INSTALL_ROOT}/Binaries)
install(
        DIRECTORY ./vendor/pyunrealsdk/stubs/pyunrealsdk
        DESTINATION "${CMAKE_CURRENT_SOURCE_DIR}/src"
)
install(
        DIRECTORY ./vendor/pyunrealsdk/stubs/unrealsdk
        DESTINATION "${CMAKE_CURRENT_SOURCE_DIR}/src"
)
install(FILES "unrealsdk.toml" DESTINATION ${WMM_INSTALL_ROOT}/Binaries/Plugins)

install( # Install contents excluding some file types since
        DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/src/
        DESTINATION ${WMM_INSTALL_ROOT}/Mods
        PATTERN "example_mod" EXCLUDE
        PATTERN ".idea" EXCLUDE
        PATTERN ".git" EXCLUDE
        PATTERN ".gitignore" EXCLUDE
        PATTERN ".github" EXCLUDE
)

option(WMM_INSTALL_EXAMPLE_MOD OFF)
if (WMM_INSTALL_EXAMPLE_MOD)
    install(
            DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/src/example_mod"
            DESTINATION "${WMM_INSTALL_ROOT}/Mods"
            PATTERN ".idea" EXCLUDE
            PATTERN ".git" EXCLUDE
            PATTERN ".gitignore" EXCLUDE
            PATTERN ".github" EXCLUDE
    )
endif ()

option(WMM_INSTALL_STUBS "Installs the stubs for implicit/builtin libraries" ON)

if (WMM_INSTALL_STUBS)
    install( # Install stubs into install directory
            DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/vendor/pyunrealsdk/stubs/"
            DESTINATION "${WMM_INSTALL_ROOT}/Mods/"
            PATTERN ".idea" EXCLUDE
            PATTERN ".git" EXCLUDE
            PATTERN ".gitignore" EXCLUDE
            PATTERN ".github" EXCLUDE
            PATTERN "Readme.*" EXCLUDE
    )
    install( # Install stubs into source directory; only used to resolve references for internal mods
            DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/vendor/pyunrealsdk/stubs/"
            DESTINATION "${CMAKE_CURRENT_SOURCE_DIR}/src/"
            PATTERN ".idea" EXCLUDE
            PATTERN ".git" EXCLUDE
            PATTERN ".gitignore" EXCLUDE
            PATTERN ".github" EXCLUDE
            PATTERN "Readme.*" EXCLUDE
    )
endif ()

# This assumes the directory structure for the sdk-install-dir is the required i.e., Binaries/Plugins
find_package(Python3 REQUIRED)

set(WMM_PY_PACKAGE_ARGS
        --version "\"${CMAKE_PROJECT_VERSION}\""
        --install-dir "\"${WMM_INSTALL_ROOT}\""
        --build-type "\"${CMAKE_BUILD_TYPE}\""
        --output-dir "\"${CMAKE_CURRENT_SOURCE_DIR}/build\""
)

add_custom_target(
        package_willow_mod_manager
        COMMAND
        "${Python3_EXECUTABLE}"
        "${CMAKE_CURRENT_SOURCE_DIR}/scripts/create_zip_release.py"
        ${WMM_PY_PACKAGE_ARGS}
        WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
)

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
