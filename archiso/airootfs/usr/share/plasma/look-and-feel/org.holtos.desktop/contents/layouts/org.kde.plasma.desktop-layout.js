// HoltOS default desktop layout (neon rebrand, Liam 2026-09-14): a thin glass
// menu bar across the top (app launcher with the HoltOS otter, the active app's
// menus, system tray, clock) and a floating glass dock at the bottom centre that
// is only as wide as its apps. It replaces the single full-width bottom panel.
// The glass comes from KWin Blur and Background Contrast (see ../defaults) behind
// translucent panels. holtos-glass-user-update applies this layout to accounts
// made before the rebrand, after backing up their panels.

// Menu bar
var bar = new Panel;
bar.location = "top";
bar.height = Math.round(gridUnit * 1.8);
bar.opacity = "translucent";
bar.floating = false;
bar.hiding = "none";

var launcher = bar.addWidget("org.kde.plasma.kickoff");
launcher.currentConfigGroup = ["General"];
launcher.writeConfig("icon", "holtos-logo");

bar.addWidget("org.kde.plasma.appmenu");
bar.addWidget("org.kde.plasma.panelspacer");
bar.addWidget("org.kde.plasma.systemtray");

var clock = bar.addWidget("org.kde.plasma.digitalclock");
clock.currentConfigGroup = ["Appearance"];
clock.writeConfig("showDate", true);

// Floating dock
var dock = new Panel;
dock.location = "bottom";
// 2.6 grid units: smaller icons, less cluttered (Liam, 2026-09-14; was 3.2).
dock.height = Math.round(gridUnit * 2.6);
dock.opacity = "translucent";
dock.floating = true;
dock.lengthMode = "fit";
dock.alignment = "center";
dock.hiding = "none";

var tasks = dock.addWidget("org.kde.plasma.icontasks");
tasks.currentConfigGroup = ["General"];
tasks.writeConfig("launchers", [
    "applications:org.kde.dolphin.desktop",
    "applications:chromium.desktop",
    "applications:steam.desktop",
    "applications:holtos-apps.desktop",
    "applications:org.kde.konsole.desktop",
    "applications:systemsettings.desktop"
]);

var desktopsArray = desktopsForActivity(currentActivity());
for (var j = 0; j < desktopsArray.length; j++) {
    desktopsArray[j].wallpaperPlugin = 'org.kde.image';
}
