/* HoltOS KSplash — the moment between SDDM and the desktop.
   HoltOS Glass, principle 04 "drawn, never spun": the ring under the
   otter DRAWS itself over 1.6 s on the ease-out curve, then holds; the
   whole scene fades in at stage 2 and the ring fades out at stage 5,
   matching the stage protocol Breeze's Splash.qml uses. No spinner.
*/
import QtQuick

Rectangle {
    id: root
    color: "#0D0B12"

    property int stage

    onStageChanged: {
        if (stage == 2) {
            introAnimation.running = true;
            ringDraw.running = true;
        } else if (stage == 5) {
            outroAnimation.running = true;
        }
    }

    Item {
        id: content
        anchors.fill: parent
        opacity: 0

        // Faint ambient glow, top-right — the Glass ground layer.
        Rectangle {
            width: 700; height: 420; radius: 350
            x: parent.width * 0.70 - width / 2
            y: -parent.height * 0.08 - height / 2
            gradient: Gradient {
                orientation: Gradient.Vertical
                GradientStop { position: 0.0; color: Qt.rgba(177/255, 77/255, 1, 0.14) }
                GradientStop { position: 1.0; color: Qt.rgba(177/255, 77/255, 1, 0.0) }
            }
            opacity: 0.9
        }

        Image {
            id: otter
            anchors.centerIn: parent
            anchors.verticalCenterOffset: -60
            source: "images/otter.png"
            width: 200
            fillMode: Image.PreserveAspectFit
            asynchronous: true
        }

        // The drawn ring.
        Canvas {
            id: ring
            property real progress: 0
            width: 72; height: 72
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: otter.bottom
            anchors.topMargin: 40
            onProgressChanged: requestPaint()
            onPaint: {
                var ctx = getContext("2d");
                ctx.reset();
                var cx = width / 2, cy = height / 2, r = 30;
                ctx.lineWidth = 5;
                ctx.lineCap = "round";
                // track
                ctx.strokeStyle = Qt.rgba(1, 1, 1, 0.09);
                ctx.beginPath(); ctx.arc(cx, cy, r, 0, 2 * Math.PI); ctx.stroke();
                // drawn arc
                if (progress > 0) {
                    ctx.strokeStyle = "#B14DFF";
                    ctx.beginPath();
                    ctx.arc(cx, cy, r, -Math.PI / 2, -Math.PI / 2 + 2 * Math.PI * progress);
                    ctx.stroke();
                }
            }
        }

        Image {
            source: "images/lockup.png"
            width: 180
            fillMode: Image.PreserveAspectFit
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 56
            opacity: 0.85
            asynchronous: true
        }
    }

    NumberAnimation {
        id: ringDraw
        target: ring
        property: "progress"
        from: 0; to: 1
        duration: 1600
        easing.type: Easing.OutCubic
        running: false
    }

    OpacityAnimator {
        id: introAnimation
        running: false
        target: content
        from: 0; to: 1
        duration: 500
        easing.type: Easing.OutCubic
    }

    OpacityAnimator {
        id: outroAnimation
        running: false
        target: ring
        from: 1; to: 0
        duration: 220
        easing.type: Easing.OutCubic
    }
}
