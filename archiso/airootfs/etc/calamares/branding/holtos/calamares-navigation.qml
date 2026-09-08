/* Horizontal top bar: Back (left), the HoltOS logo (center), Cancel +
   Next (right) — replaces Calamares' default navigation button placement.
   Adapted from the KaOS branding component's calamares-navigation.qml (a
   real, shipped reference for the "navigation: qml" option and the
   ViewManager API: backEnabled/nextEnabled/quitEnabled/quitVisible/
   backAndNextVisible/currentStepIndex/rowCount()/quitTooltip, and the
   back()/next()/quit() actions) — rebuilt as a RowLayout instead of
   KaOS's ColumnLayout, dropped the Debug/About buttons (About is already
   reachable from the Welcome page itself), and recolored to the HoltOS
   palette instead of KaOS's light-grey hover states.
*/
import io.calamares.ui 1.0
import io.calamares.core 1.0

import QtQuick 2.3
import QtQuick.Controls 2.10
import QtQuick.Layouts 1.3

Rectangle {
    id: navigationBar
    color: Branding.styleString( Branding.SidebarBackground )
    width: parent.width
    height: 64

    readonly property color idleColor: Branding.styleString( Branding.SidebarBackground )
    readonly property color hoverColor: "#2a2438"
    readonly property color disabledTextColor: "#5a5568"
    readonly property color nextIdleColor: Branding.styleString( Branding.SidebarBackgroundCurrent )
    readonly property color nextHoverColor: "#c46eff"

    RowLayout {
        anchors.fill: parent
        spacing: 1

        Rectangle {
            id: backArea
            Layout.preferredWidth: 96
            Layout.fillHeight: true
            color: mouseBack.containsMouse ? navigationBar.hoverColor : navigationBar.idleColor
            enabled: ViewManager.backEnabled
            visible: ViewManager.backAndNextVisible

            MouseArea {
                id: mouseBack
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                hoverEnabled: true

                Text {
                    anchors.centerIn: parent
                    text: qsTr("Back")
                    color: !backArea.enabled ? navigationBar.disabledTextColor : Branding.styleString( Branding.SidebarText )
                    font.pointSize: 9
                }

                onClicked: { ViewManager.back(); }
            }
        }

        Item { Layout.fillWidth: true }

        Image {
            id: logo
            Layout.alignment: Qt.AlignVCenter | Qt.AlignHCenter
            height: 46
            width: height
            source: "file:/" + Branding.imagePath( Branding.ProductLogo )
            sourceSize.width: width
            sourceSize.height: height
            fillMode: Image.PreserveAspectFit
        }

        Item { Layout.fillWidth: true }

        Rectangle {
            id: cancelArea
            Layout.preferredWidth: 96
            Layout.fillHeight: true
            color: mouseCancel.containsMouse ? navigationBar.hoverColor : navigationBar.idleColor
            enabled: ViewManager.quitEnabled
            visible: ViewManager.quitVisible && ( ViewManager.currentStepIndex < ViewManager.rowCount() - 1 )

            ToolTip {
                visible: mouseCancel.containsMouse
                timeout: 5000
                delay: 1000
                text: ViewManager.quitTooltip
            }

            MouseArea {
                id: mouseCancel
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                hoverEnabled: true

                Text {
                    anchors.centerIn: parent
                    text: qsTr("Cancel")
                    color: !cancelArea.enabled ? navigationBar.disabledTextColor : Branding.styleString( Branding.SidebarText )
                    font.pointSize: 9
                }

                onClicked: { ViewManager.quit(); }
            }
        }

        Rectangle {
            id: nextArea
            Layout.preferredWidth: 96
            Layout.fillHeight: true
            color: mouseNext.containsMouse ? navigationBar.nextHoverColor : navigationBar.nextIdleColor
            enabled: ViewManager.nextEnabled
            visible: ViewManager.backAndNextVisible

            MouseArea {
                id: mouseNext
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                hoverEnabled: true

                Text {
                    anchors.centerIn: parent
                    text: qsTr("Next")
                    color: !nextArea.enabled ? navigationBar.disabledTextColor : Branding.styleString( Branding.SidebarTextCurrent )
                    font.pointSize: 9
                    font.bold: true
                }

                onClicked: { ViewManager.next(); }
            }
        }
    }
}
