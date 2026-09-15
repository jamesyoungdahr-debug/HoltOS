/* "Keeping Windows?" — shown before the Partitions step (settings.conf,
   notesqml@dualboot). Embedded QML cannot be glass (see branding.desc), so
   the page sits on the opaque surface colour like the top and bottom bars.
   Liam, 2026-09-14: install alongside an existing OS. */
import QtQuick 2.3
import QtQuick.Layouts 1.3

Rectangle {
    color: "#171423"

    readonly property color ink: "#FFFFFF"
    readonly property color inkSoft: Qt.rgba(1, 1, 1, 0.70)
    readonly property color lilac: "#F4EBFF"
    readonly property color warning: "#FFB84D"

    Flickable {
        anchors.fill: parent
        anchors.margins: 32
        contentHeight: column.implicitHeight
        clip: true

        ColumnLayout {
            id: column
            width: parent.width
            spacing: 18

            Text {
                text: "Keeping Windows on this computer?"
                color: ink
                font.family: "Nunito"
                font.weight: Font.Black
                font.pixelSize: 26
            }
            Text {
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                text: "HoltOS can install alongside Windows, and the boot menu lets you pick either one when the computer starts. Before you continue:"
                color: inkSoft
                font.family: "Nunito"
                font.pixelSize: 15
            }

            Repeater {
                model: [
                    { title: "Turn off Fast Startup in Windows",
                      body: "Control Panel > Power Options > Choose what the power buttons do > untick \"Turn on fast startup\". Otherwise Windows keeps its disk locked and HoltOS cannot safely make room next to it." },
                    { title: "Have your BitLocker recovery key ready",
                      body: "If Windows uses BitLocker or Device Encryption, changing the disk can make it ask for the recovery key at the next start. You can find the key at aka.ms/myrecoverykey." },
                    { title: "Make room for HoltOS",
                      body: "HoltOS needs at least 40 GB. Shrinking the Windows partition first in Windows' Disk Management is the safest way; then choose \"Install alongside\" or the free space on the next page." },
                    { title: "Back up anything important",
                      body: "Changing partitions is safe when nothing goes wrong, but a power cut halfway could lose data." }
                ]
                delegate: RowLayout {
                    Layout.fillWidth: true
                    spacing: 14
                    Rectangle {
                        Layout.alignment: Qt.AlignTop
                        Layout.topMargin: 6
                        width: 10; height: 10; radius: 5
                        color: warning
                    }
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 4
                        Text {
                            text: modelData.title
                            color: lilac
                            font.family: "Nunito"
                            font.weight: Font.ExtraBold
                            font.pixelSize: 16
                        }
                        Text {
                            Layout.fillWidth: true
                            wrapMode: Text.WordWrap
                            text: modelData.body
                            color: inkSoft
                            font.family: "Nunito"
                            font.pixelSize: 14
                        }
                    }
                }
            }

            Text {
                Layout.fillWidth: true
                Layout.topMargin: 8
                wrapMode: Text.WordWrap
                text: "Installing HoltOS on its own and erasing the whole disk? You can skip all of this: press Next."
                color: inkSoft
                font.family: "Nunito"
                font.italic: true
                font.pixelSize: 14
            }
        }
    }
}
