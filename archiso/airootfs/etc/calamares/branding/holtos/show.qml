import QtQuick 2.0
import calamares.slideshow 1.0

Presentation {
    id: presentation

    // Real HoltOS Design System tokens (styles.css).
    property color holtDeep: "#0D0B12"
    property color holtInk: "#FFFFFF"
    property color holtHealthy: "#28E0C8"

    Slide {
        Rectangle { anchors.fill: parent; color: presentation.holtDeep }
        Image {
            id: logo
            source: "logo-icon.svg"
            width: 220
            height: 220
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.top
            anchors.topMargin: 40
            fillMode: Image.PreserveAspectFit
        }
        Text {
            anchors.top: logo.bottom
            anchors.topMargin: 30
            anchors.horizontalCenter: parent.horizontalCenter
            text: "Installing HoltOS — a self-hosted homelab server."
            color: presentation.holtInk
            font.pointSize: 18
        }
    }

    Slide {
        Rectangle { anchors.fill: parent; color: presentation.holtDeep }
        Text {
            anchors.centerIn: parent
            width: parent.width * 0.8
            wrapMode: Text.WordWrap
            horizontalAlignment: Text.AlignHCenter
            text: "HoltOS ships Authentik SSO, Sonarr, Radarr, Prowlarr, Jellyseerr, qBittorrent, and Plex, pre-wired as Podman Quadlets."
            color: presentation.holtInk
            font.pointSize: 16
        }
    }

    Slide {
        Rectangle { anchors.fill: parent; color: presentation.holtDeep }
        Text {
            anchors.centerIn: parent
            text: "Sit back and relax while HoltOS installs."
            color: presentation.holtHealthy
            font.pointSize: 18
        }
    }

    Timer {
        interval: 5000
        running: true
        repeat: true
        onTriggered: presentation.goToNextSlide()
    }
}
