import QtQuick 2.0
import calamares.slideshow 1.0

Presentation {
    id: presentation

    Slide {
        Image {
            id: logo
            source: "logo.svg"
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
            font.pointSize: 18
        }
    }

    Slide {
        Text {
            anchors.centerIn: parent
            width: parent.width * 0.8
            wrapMode: Text.WordWrap
            horizontalAlignment: Text.AlignHCenter
            text: "HoltOS ships Authentik SSO, Sonarr, Radarr, Prowlarr, Jellyseerr, qBittorrent, and Plex, pre-wired as Podman Quadlets."
            font.pointSize: 16
        }
    }

    Slide {
        Text {
            anchors.centerIn: parent
            text: "Sit back and relax while HoltOS installs."
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
