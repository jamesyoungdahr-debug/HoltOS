/* HoltOS install slideshow — HoltOS Glass. Full-bleed holt-deep ground
   (the Presentation itself is transparent; without the root Rectangle
   the QQuickWidget's white clear colour showed as a frame around the
   slide — seen live 2026-09-11), one otter sticker, one line of plain
   language per slide (principle 01), and DRAWN progress dots: the
   current slide's dot is a pill that fills over the slide's 5 s
   (principle 04 — nothing spins). */
import QtQuick 2.0
import calamares.slideshow 1.0

Presentation {
    id: presentation

    readonly property color holtDeep: "#0D0B12"
    readonly property color holtInk: "#FFFFFF"
    readonly property color holtCurrent: "#B14DFF"
    readonly property int slideMs: 5000
    readonly property int slideCount: 3

    // Ground — fixes the white frame.
    Rectangle { anchors.fill: parent; color: presentation.holtDeep; z: -1 }

    // Faint ambient glow, top-right.
    Rectangle {
        width: 520; height: 320; radius: 260
        x: parent.width * 0.72 - width / 2
        y: -height * 0.55
        color: Qt.rgba(177 / 255, 77 / 255, 1, 0.10)
        z: -1
    }

    Slide {
        Image {
            id: logo1
            source: "logo-icon.svg"
            width: 160; height: 160
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            anchors.verticalCenterOffset: -60
            fillMode: Image.PreserveAspectFit
            sourceSize.width: 160; sourceSize.height: 160
        }
        Text {
            anchors.top: logo1.bottom; anchors.topMargin: 28
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width * 0.8
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
            text: "Setting up HoltOS."
            color: presentation.holtInk
            font.family: "Nunito"; font.weight: Font.ExtraBold; font.pixelSize: 30; font.letterSpacing: -1
        }
    }

    Slide {
        Text {
            anchors.centerIn: parent
            width: parent.width * 0.8
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
            text: "The Den — your movie and TV library — is already on board."
            color: presentation.holtInk
            font.family: "Nunito"; font.weight: Font.ExtraBold; font.pixelSize: 26; font.letterSpacing: -0.8
        }
    }

    Slide {
        Text {
            anchors.centerIn: parent
            width: parent.width * 0.8
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
            text: "Snapshots are taken before every update, so you can always go back."
            color: presentation.holtInk
            font.family: "Nunito"; font.weight: Font.ExtraBold; font.pixelSize: 26; font.letterSpacing: -0.8
        }
    }

    // Drawn progress dots.
    Row {
        id: dots
        spacing: 8
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 26
        z: 10
        Repeater {
            model: presentation.slideCount
            Rectangle {
                readonly property bool isCurrent: index === presentation.currentSlide
                height: 6
                width: isCurrent ? 28 : 6
                radius: 3
                color: Qt.rgba(1, 1, 1, 0.15)
                Behavior on width { NumberAnimation { duration: 220; easing.type: Easing.OutCubic } }
                Rectangle {
                    height: parent.height; radius: 3
                    color: presentation.holtCurrent
                    visible: parent.isCurrent
                    width: 0
                    onVisibleChanged: {
                        width = 0
                        if (visible) draw.restart()
                    }
                    NumberAnimation on width {
                        id: draw
                        running: false
                        from: 0; to: 28
                        duration: presentation.slideMs
                        easing.type: Easing.OutCubic
                    }
                    Component.onCompleted: if (visible) draw.start()
                }
            }
        }
    }

    Timer {
        interval: presentation.slideMs
        running: true
        repeat: true
        onTriggered: presentation.goToNextSlide()
    }
}
