/* HoltOS SDDM greeter — the "Sign in" frame of HoltOS Glass.
   Ground: pool-rings wallpaper + faint purple glow + the otter at 9%
   bottom-right. Over it, one centred floating-glass card (400 wide,
   radius 14, surface at 84%, blur 28-ish) with the lockup, the user, a
   password field and the screen's single purple action. Restart / Shut
   down are quiet, at the bottom.

   Self-contained on purpose: only QtQuick, QtQuick.Controls.Basic and
   QtQuick.Effects (MultiEffect, Qt >= 6.5) — no Plasma/Kirigami imports,
   so an SDDM greeter with a partial Plasma runtime still renders it.
   Under software rendering (GraphicsInfo.api === Software) the glass
   falls back to its opaque twin, holt-surface #171423, per the brief.

   SDDM API used (Theme-API 2.0): sddm.login(user, password, sessionIndex),
   sddm.loginFailed/loginSucceeded, sddm.canReboot/reboot(),
   sddm.canPowerOff/powerOff(), sddm.hostName, userModel.lastUser /
   model role "name", sessionModel.lastIndex/count/role "name", config.<theme.conf keys>.
*/
import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Effects

Item {
    id: root
    width: 1920
    height: 1080

    readonly property bool softwareRendering: GraphicsInfo.api === GraphicsInfo.Software
    readonly property color deep: "#0D0B12"
    readonly property color surface: "#171423"
    readonly property color raised: "#1D1927"
    readonly property color ink: "#FFFFFF"
    readonly property color current: "#B14DFF"
    readonly property color healthy: "#28E0C8"
    readonly property color warning: "#FFB84D"
    readonly property color hairline: Qt.rgba(1, 1, 1, 0.09)
    readonly property color hairlineStrong: Qt.rgba(1, 1, 1, 0.15)

    property string userName: userModel.lastUser
    property bool showUsernameField: false
    property string errorText: ""

    // Chosen session (Plasma or HoltOS Game Mode); defaults to SDDM's
    // remembered last session, which holtos-session-apply keeps sane.
    property int sessionIndex: sessionModel.lastIndex >= 0 ? sessionModel.lastIndex : 0

    function currentSession() {
        return root.sessionIndex
    }

    function doLogin() {
        var user = showUsernameField ? userField.text : userName
        if (user === "" || passwordField.text === "") {
            return
        }
        errorText = ""
        loginButton.enabled = false
        sddm.login(user, passwordField.text, currentSession())
    }

    // Fallback: if there is no remembered last user, take the first one.
    ListView {
        model: userModel
        visible: false
        delegate: Item {
            Component.onCompleted: {
                if (index === 0 && root.userName === "") {
                    root.userName = model.name
                }
            }
        }
    }

    Connections {
        target: sddm
        function onLoginFailed() {
            root.errorText = "That password didn't work. Try again."
            passwordField.selectAll()
            passwordField.forceActiveFocus()
            loginButton.enabled = true
        }
        function onLoginSucceeded() {
            root.errorText = ""
        }
    }

    // ---- Ground -------------------------------------------------------
    Item {
        id: ground
        anchors.fill: parent

        Rectangle { anchors.fill: parent; color: root.deep }

        Image {
            anchors.fill: parent
            source: config.background
            fillMode: Image.PreserveAspectCrop
            asynchronous: true
        }

        Image {
            source: config.glow
            x: root.width * 0.70 - width / 2
            y: -root.height * 0.08 - height / 2
            opacity: 0.9
            asynchronous: true
        }

        Image {
            source: config.otter
            width: 520
            fillMode: Image.PreserveAspectFit
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.rightMargin: -80
            anchors.bottomMargin: -70
            opacity: 0.07
            asynchronous: true
        }
    }

    // ---- Floating glass card -----------------------------------------
    Item {
        id: card
        width: 400
        height: cardColumn.implicitHeight + 64
        anchors.centerIn: parent
        anchors.verticalCenterOffset: -24

        // Rounded-rect mask for the blurred backdrop (rendered off-screen,
        // hidden from the scene by hideSource).
        Rectangle {
            id: maskShape
            anchors.fill: parent
            radius: 14
            color: "black"
        }
        ShaderEffectSource {
            id: maskSource
            sourceItem: maskShape
            hideSource: true
            visible: false
        }

        // Blurred copy of the ground under the card — the "glass".
        Item {
            id: glassBackdrop
            anchors.fill: parent
            visible: !root.softwareRendering
            layer.enabled: !root.softwareRendering
            layer.effect: MultiEffect {
                maskEnabled: true
                maskSource: maskSource
                maskThresholdMin: 0.5
                maskSpreadAtMin: 1.0
            }

            ShaderEffectSource {
                id: groundSource
                anchors.fill: parent
                sourceItem: ground
                sourceRect: Qt.rect(card.x, card.y, card.width, card.height)
                live: false
                visible: false
            }
            MultiEffect {
                anchors.fill: parent
                source: groundSource
                blurEnabled: true
                blur: 1.0
                blurMax: 48
                saturation: 0.4
            }
        }

        Rectangle {
            id: cardFace
            anchors.fill: parent
            radius: 14
            color: root.softwareRendering ? root.surface : Qt.rgba(23 / 255, 20 / 255, 35 / 255, 0.84)
            border.width: 1
            border.color: root.hairlineStrong

            // inset top highlight
            Rectangle {
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.margins: 1
                height: 1
                color: Qt.rgba(1, 1, 1, 0.08)
            }
        }

        Column {
            id: cardColumn
            anchors.centerIn: parent
            width: parent.width - 64
            spacing: 16

            Image {
                source: config.lockup
                width: 150
                fillMode: Image.PreserveAspectFit
                asynchronous: true
            }

            Item { width: 1; height: 4 }

            Row {
                spacing: 12
                Rectangle {
                    id: avatar
                    width: 44; height: 44; radius: 22
                    gradient: Gradient {
                        orientation: Gradient.Horizontal
                        GradientStop { position: 0.0; color: root.current }
                        GradientStop { position: 1.0; color: root.healthy }
                    }
                    Text {
                        anchors.centerIn: parent
                        text: root.userName.length > 0 ? root.userName.charAt(0).toUpperCase() : "?"
                        color: root.deep
                        font.family: "Nunito"
                        font.weight: Font.Black
                        font.pixelSize: 20
                    }
                }
                Column {
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 2
                    Text {
                        text: root.userName.length > 0 ? root.userName : "Sign in"
                        color: root.ink
                        font.family: "Nunito"
                        font.weight: Font.ExtraBold
                        font.pixelSize: 18
                        font.letterSpacing: -0.4
                    }
                    Text {
                        text: (sddm.hostName || "holtos").toUpperCase()
                        color: Qt.rgba(1, 1, 1, 0.42)
                        font.family: "JetBrains Mono"
                        font.pixelSize: 11
                        font.letterSpacing: 2.2
                    }
                }
            }

            TextField {
                id: userField
                visible: root.showUsernameField
                width: parent.width
                placeholderText: "Username"
                placeholderTextColor: Qt.rgba(1, 1, 1, 0.42)
                color: root.ink
                font.family: "Nunito"
                font.pixelSize: 14
                leftPadding: 14; rightPadding: 14; topPadding: 10; bottomPadding: 10
                background: Rectangle {
                    color: root.deep
                    radius: 10
                    border.width: 1
                    border.color: userField.activeFocus ? root.current : root.hairlineStrong
                }
                onAccepted: passwordField.forceActiveFocus()
            }

            TextField {
                id: passwordField
                width: parent.width
                echoMode: TextInput.Password
                placeholderText: "Password"
                placeholderTextColor: Qt.rgba(1, 1, 1, 0.42)
                color: root.ink
                font.family: "Nunito"
                font.pixelSize: 14
                leftPadding: 14; rightPadding: 14; topPadding: 10; bottomPadding: 10
                background: Rectangle {
                    color: root.deep
                    radius: 10
                    border.width: 1
                    border.color: passwordField.activeFocus ? root.current : root.hairlineStrong
                }
                onAccepted: root.doLogin()
                Component.onCompleted: forceActiveFocus()
            }

            Text {
                visible: root.errorText.length > 0
                text: root.errorText
                color: root.warning
                font.family: "Nunito"
                font.pixelSize: 13
                wrapMode: Text.WordWrap
                width: parent.width
            }

            Button {
                id: loginButton
                width: parent.width
                height: 42
                text: "Log in"
                background: Rectangle {
                    radius: 10
                    color: !loginButton.enabled ? root.raised
                         : loginButton.down ? "#8F2FE0"
                         : loginButton.hovered ? "#C46EFF" : root.current
                }
                contentItem: Text {
                    text: loginButton.text
                    color: loginButton.enabled ? root.deep : Qt.rgba(1, 1, 1, 0.42)
                    font.family: "Nunito"
                    font.weight: Font.Bold
                    font.pixelSize: 15
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                onClicked: root.doLogin()
            }

            // Session picker: only shown when there is a choice (Plasma and
            // HoltOS Game Mode). Drafted by the local model.
            Column {
                id: sessionPicker
                width: parent.width
                spacing: 8
                visible: sessionModel.count > 1

                Text {
                    text: "SESSION"
                    color: Qt.rgba(1, 1, 1, 0.42)
                    font.family: "Nunito"
                    font.pixelSize: 11
                    font.letterSpacing: 1.5
                }

                Flow {
                    width: parent.width
                    spacing: 8

                    Repeater {
                        model: sessionModel
                        delegate: Rectangle {
                            id: chip
                            required property int index
                            required property string name
                            readonly property bool selected: root.sessionIndex === index
                            radius: 8
                            height: 28
                            width: label.implicitWidth + 24
                            color: selected ? root.current : root.raised
                            border.width: 1
                            border.color: selected ? root.current : root.hairlineStrong

                            Text {
                                id: label
                                anchors.centerIn: parent
                                text: name
                                color: selected ? root.deep : Qt.rgba(1, 1, 1, 0.75)
                                font.family: "Nunito"
                                font.weight: Font.Bold
                                font.pixelSize: 12
                            }

                            MouseArea {
                                anchors.fill: parent
                                cursorShape: Qt.PointingHandCursor
                                onClicked: root.sessionIndex = index
                            }
                        }
                    }
                }
            }

            Text {
                text: root.showUsernameField ? "Back to " + root.userName : "Not you? Sign in as someone else"
                color: Qt.rgba(1, 1, 1, 0.42)
                font.family: "Nunito"
                font.pixelSize: 12
                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        root.showUsernameField = !root.showUsernameField
                        if (root.showUsernameField) userField.forceActiveFocus()
                        else passwordField.forceActiveFocus()
                    }
                }
            }
        }
    }

    // ---- Quiet power actions -----------------------------------------
    Row {
        spacing: 28
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 40

        Repeater {
            model: [
                { label: "Restart",   enabled: sddm.canReboot,   action: function() { sddm.reboot() } },
                { label: "Shut down", enabled: sddm.canPowerOff, action: function() { sddm.powerOff() } }
            ]
            delegate: Text {
                required property var modelData
                text: modelData.label
                color: mouse.containsMouse ? root.ink : Qt.rgba(1, 1, 1, 0.55)
                font.family: "Nunito"
                font.weight: Font.Bold
                font.pixelSize: 13
                opacity: modelData.enabled ? 1 : 0.4
                MouseArea {
                    id: mouse
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: if (modelData.enabled) modelData.action()
                }
            }
        }
    }
}
