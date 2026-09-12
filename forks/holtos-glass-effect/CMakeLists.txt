# HoltOS Glass — a KWin background-blur effect owned by HoltOS.
#
# Forked from KWin 6.7.5's built-in blur effect (src/plugins/blur, GPL-2.0-or-later)
# and built OUT OF TREE against the installed KWin's development headers,
# the same way kwin-effects-forceblur ("Better Blur", GPL-3.0-or-later) does —
# several of its features are ported here. See README.md.
#
# The plugin id is "holtosglass" (the library file name); enable it with
#   [Plugins] holtosglassEnabled=true   (and blurEnabled=false)
# in kwinrc. It replaces the stock blur, it does not stack on top of it.
cmake_minimum_required(VERSION 3.16.0)

project(holtos-glass-effect)
set(PROJECT_VERSION "0.1.0")
set(PROJECT_VERSION_MAJOR 0)

set(KF_MIN_VERSION "6.0.0")
set(QT_MIN_VERSION "6.6.0")
set(QT_MAJOR_VERSION 6)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE "Release" CACHE STRING "Choose Release or Debug" FORCE)
endif()

find_package(ECM REQUIRED NO_MODULE)
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${ECM_MODULE_PATH} ${ECM_KDE_MODULE_DIR})

option(HOLTOSGLASS_WAYLAND "Build the effect for the Wayland KWin if present." ON)
option(HOLTOSGLASS_X11 "Build the effect for KWin X11 if present." OFF)

include(FeatureSummary)
include(KDEInstallDirs)
include(KDECMakeSettings)
include(KDECompilerSettings NO_POLICY_SCOPE)

find_package(Qt6 ${QT_MIN_VERSION} CONFIG REQUIRED COMPONENTS
    Core
    DBus
    Gui
    OpenGL
    Widgets
)

find_package(KF6 ${KF_MIN_VERSION} REQUIRED COMPONENTS
    Config
    ConfigWidgets
    CoreAddons
    I18n
    KCMUtils
    WidgetsAddons
    WindowSystem
)

find_package(epoxy REQUIRED)
# xcbutils.h (X11 blur-region property, used for Xwayland windows too) is
# header-only and calls libxcb directly.
find_package(XCB REQUIRED COMPONENTS XCB)
find_package(KDecoration3 REQUIRED)

if(HOLTOSGLASS_WAYLAND)
    find_package(KWin COMPONENTS kwineffects)
    if(${KWin_FOUND})
        find_package(KWinDBusInterface CONFIG REQUIRED)
    else()
        set(HOLTOSGLASS_WAYLAND OFF)
    endif()
endif()
if(HOLTOSGLASS_X11)
    find_package(KWinX11 COMPONENTS kwineffects)
    if(${KWinX11_FOUND})
        find_package(KWinX11DBusInterface CONFIG REQUIRED)
        set(KWin_VERSION ${KWinX11_VERSION})
    else()
        set(HOLTOSGLASS_X11 OFF)
    endif()
endif()

if(NOT HOLTOSGLASS_WAYLAND AND NOT HOLTOSGLASS_X11)
    message(FATAL_ERROR "Neither KWin (Wayland) nor KWin X11 development files were found.")
endif()

# This fork tracks KWin's private effect API release by release; the
# sources here are from 6.7. Refuse to build against anything else so a
# silent ABI mismatch never ships in an image.
if(${KWin_VERSION} VERSION_LESS 6.7 OR ${KWin_VERSION} VERSION_GREATER_EQUAL 6.8)
    message(FATAL_ERROR "HoltOS Glass ${PROJECT_VERSION} is written against KWin 6.7.x; found ${KWin_VERSION}. Port the sources before building (see README.md).")
endif()

add_subdirectory(src)

feature_summary(WHAT ALL FATAL_ON_MISSING_REQUIRED_PACKAGES)
