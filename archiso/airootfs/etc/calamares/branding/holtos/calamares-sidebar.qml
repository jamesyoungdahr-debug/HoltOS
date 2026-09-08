/* Horizontal step list along the bottom of the window, replacing
   Calamares' default vertical left-side step list. Adapted from the
   KaOS branding component's calamares-sidebar.qml (a real, shipped
   reference for the "sidebar: qml,bottom" branding.desc option) —
   simplified (no step-underline indicator image) and recolored to the
   HoltOS palette via the branding.desc style: keys.
*/
import io.calamares.ui 1.0
import io.calamares.core 1.0

import QtQuick 2.3
import QtQuick.Layouts 1.3

Rectangle {
    id: sideBar
    color: Branding.styleString( Branding.SidebarBackground )
    height: 48
    width: parent.width

    RowLayout {
        anchors.fill: parent
        spacing: 2

        Repeater {
            model: ViewManager
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: Branding.styleString( index == ViewManager.currentStepIndex ? Branding.SidebarBackgroundCurrent : Branding.SidebarBackground )

                Text {
                    anchors.centerIn: parent
                    color: Branding.styleString( index == ViewManager.currentStepIndex ? Branding.SidebarTextCurrent : Branding.SidebarText )
                    text: display
                    font.pointSize: index == ViewManager.currentStepIndex ? 10 : 9
                    font.bold: index == ViewManager.currentStepIndex
                }
            }
        }
    }
}
