#######################################
# Effect

set(holtosglass_SOURCES
    blur.cpp
    holtosglass.qrc
    main.cpp
)

kconfig_add_kcfg_files(holtosglass_SOURCES
    blurconfig.kcfgc
)

if(HOLTOSGLASS_WAYLAND)
    add_library(holtosglass MODULE ${holtosglass_SOURCES})
    target_link_libraries(holtosglass PRIVATE
        KDecoration3::KDecoration
        KF6::ConfigGui
        KWin::kwin
        XCB::XCB
    )
    install(TARGETS holtosglass DESTINATION ${KDE_INSTALL_PLUGINDIR}/kwin/effects/plugins)
endif()
if(HOLTOSGLASS_X11)
    add_library(holtosglass_x11 MODULE ${holtosglass_SOURCES})
    target_link_libraries(holtosglass_x11 PRIVATE
        KDecoration3::KDecoration
        KF6::ConfigGui
        KWinX11::kwin
        XCB::XCB
    )
    target_compile_definitions(holtosglass_x11 PRIVATE HOLTOSGLASS_X11)
    install(TARGETS holtosglass_x11 DESTINATION ${KDE_INSTALL_PLUGINDIR}/kwin-x11/effects/plugins)
endif()

#######################################
# Config module (System Settings > Desktop Effects > HoltOS Glass > configure)

set(kwin_holtosglass_config_SRCS
    blur_config.cpp
    blur_config.h
)

ki18n_wrap_ui(kwin_holtosglass_config_SRCS blur_config.ui)
kconfig_add_kcfg_files(kwin_holtosglass_config_SRCS blurconfig.kcfgc)

# The org.kde.kwin.Effects D-Bus interface, used to ask the running KWin
# to reconfigure the effect after Apply. Same interface on Wayland and X11.
qt_add_dbus_interface(kwin_holtosglass_config_SRCS ${KWIN_EFFECTS_INTERFACE} kwineffects_interface)

add_library(kwin_holtosglass_config MODULE ${kwin_holtosglass_config_SRCS})
target_link_libraries(kwin_holtosglass_config
    KF6::KCMUtils
    KF6::CoreAddons
    KF6::I18n
    KF6::WidgetsAddons
    Qt6::DBus
)

if(HOLTOSGLASS_WAYLAND)
    install(TARGETS kwin_holtosglass_config DESTINATION ${KDE_INSTALL_PLUGINDIR}/kwin/effects/configs)
endif()
if(HOLTOSGLASS_X11)
    install(TARGETS kwin_holtosglass_config DESTINATION ${KDE_INSTALL_PLUGINDIR}/kwin-x11/effects/configs)
endif()
