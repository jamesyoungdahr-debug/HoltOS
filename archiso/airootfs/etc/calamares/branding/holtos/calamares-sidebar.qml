/* Horizontal step list along the bottom of the window (branding.desc
   "sidebar: qml,bottom"), adapted from KaOS's shipped calamares-sidebar.qml.
   HoltOS Glass, opaque twin: holt-surface bar with a hairline top border,
   step names as mono eyebrows (JetBrains Mono, uppercase, 2.2px tracking),
   the current step in ink with a 2px purple bar and a 10% purple tint,
   the rest at ink-55 (branding.desc SidebarText). */
import io.calamares.ui 1.0
import io.calamares.core 1.0

import QtQuick 2.3
import QtQuick.Layouts 1.3

Rectangle {
    id: sideBar
    color: Branding.styleString( Branding.SidebarBackground )
    height: 48
    width: parent.width

    Rectangle { anchors.top: parent.top; width: parent.width; height: 1; color: Qt.rgba(1, 1, 1, 0.09); z: 5 }

    RowLayout {
        anchors.fill: parent
        spacing: 0

        Repeater {
            model: ViewManager
            Rectangle {
                readonly property bool isCurrent: index == ViewManager.currentStepIndex
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: isCurrent ? Qt.rgba(177 / 255, 77 / 255, 1, 0.10) : "transparent"

                Rectangle {
                    anchors.top: parent.top
                    width: parent.width
                    height: 2
                    color: Branding.styleString( Branding.SidebarBackgroundCurrent )
                    visible: isCurrent
                }

                Text {
                    anchors.centerIn: parent
                    color: isCurrent ? Branding.styleString( Branding.SidebarTextCurrent ) : Branding.styleString( Branding.SidebarText )
                    text: display.toUpperCase()
                    font.family: "JetBrains Mono"
                    font.pixelSize: 11
                    font.letterSpacing: 2.2
                    font.weight: isCurrent ? Font.DemiBold : Font.Normal
                }
            }
        }
    }
}
