// HoltOS default desktop layout — the stock defaultPanel template's panel,
// rebuilt here so its opacity can be set: "translucent" turns the panel
// into a glass bar over the pool-rings wallpaper (with KWin Blur +
// Background Contrast on, see ../defaults). loadTemplate() would not
// hand the panel object back, hence the copy.
var panel = new Panel
var panelScreen = panel.screen

panel.height = 2 * Math.ceil(gridUnit * 2.5 / 2)
panel.opacity = "translucent"

const maximumAspectRatio = 21/9;
if (panel.formFactor === "horizontal") {
    const geo = screenGeometry(panelScreen);
    const maximumWidth = Math.ceil(geo.height * maximumAspectRatio);
    if (geo.width > maximumWidth) {
        panel.alignment = "center";
        panel.minimumLength = maximumWidth;
        panel.maximumLength = maximumWidth;
    }
}

panel.addWidget("org.kde.plasma.kickoff")
panel.addWidget("org.kde.plasma.pager")
panel.addWidget("org.kde.plasma.icontasks")
panel.addWidget("org.kde.plasma.marginsseparator")
panel.addWidget("org.kde.plasma.systemtray")
panel.addWidget("org.kde.plasma.digitalclock")
panel.addWidget("org.kde.plasma.showdesktop")

var desktopsArray = desktopsForActivity(currentActivity());
for (var j = 0; j < desktopsArray.length; j++) {
    desktopsArray[j].wallpaperPlugin = 'org.kde.image';
}
