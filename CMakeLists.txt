cmake_minimum_required(VERSION 3.23)
project(
        willow_mod_manager
        VERSION 1.1.0
        DESCRIPTION "BL1 PythonSDK Mod Manager"
)

################################################################################
# DEPENDENCIES
################################################################################

add_subdirectory(./vendor/pyunrealsdk)

# Need to exclude this since we don't want its install dependencies
add_subdirectory(./vendor/plugin_loader EXCLUDE_FROM_ALL)

################################################################################
# CUSTOM BUILD TARGET
################################################################################

# Relative to: '../${presetName}/Binaries/Plugins'
set(WMM_INSTALL_ROOT "${CMAKE_INSTALL_PREFIX}/../../")

add_custom_target(${PROJECT_NAME})
add_dependencies(${PROJECT_NAME} proxy_dsound pyunrealsdk)

install(TARGETS proxy_dsound RUNTIME DESTINATION ${WMM_INSTALL_ROOT}/Binaries)
install(
        DIRECTORY ./vendor/pyunrealsdk/stubs/pyunrealsdk
        DESTINATION "${CMAKE_CURRENT_SOURCE_DIR}/src"
)
install(
        DIRECTORY ./vendor/pyunrealsdk/stubs/unrealsdk
        DESTINATION "${CMAKE_CURRENT_SOURCE_DIR}/src"
)
install(FILES "unrealsdk.env" DESTINATION ${WMM_INSTALL_ROOT}/Binaries/Plugins)

# This assumes the directory structure for the sdk-install-dir is the required i.e., Binaries/Plugins
find_package(Python3 REQUIRED)
add_custom_target(
        package_willow_mod_manager
        COMMAND
        ${Python3_EXECUTABLE}
        ./create_zip_release.py
        # The literal quotes are not actually required.
        --version "\"${CMAKE_PROJECT_VERSION}\""
        --sdk-install-dir "\"${WMM_INSTALL_ROOT}\""
        --mods-dir "\"${CMAKE_CURRENT_SOURCE_DIR}/src\""
        --build-type "\"${CMAKE_BUILD_TYPE}\""
        --output-dir "\"${CMAKE_CURRENT_SOURCE_DIR}/build\""
        WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
)
