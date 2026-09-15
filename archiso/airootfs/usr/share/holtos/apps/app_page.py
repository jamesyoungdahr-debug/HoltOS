"""The page for one app in Stash: screenshots, description, developer, sizes, licence, permissions, release notes, links, and Install / Open / Update / Remove."""

import html
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QMessageBox, QProgressBar,
    QPushButton, QScrollArea, QVBoxLayout, QWidget,
)
import flathub
import workers

AMBER = "#FFB84D"
RISKY = ("all your files", "system folders", "outside its sandbox",
         "Full access", "saved passwords")


class AppPage(QWidget):

    def __init__(self, store, on_back):
        super().__init__()
        self.store = store
        self.on_back = on_back
        self.app = None
        self.info = None
        self.token = 0

        outer = QVBoxLayout(self)

        back = QPushButton("← Back")
        back.clicked.connect(on_back)
        outer.addWidget(back, alignment=Qt.AlignLeft)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        body = QWidget()
        self.body = QVBoxLayout(body)
        scroll.setWidget(body)
        outer.addWidget(scroll, 1)

        # Header
        header = QHBoxLayout()
        self.icon = QLabel("")
        self.icon.setFixedSize(96, 96)
        header.addWidget(self.icon)

        text_col = QVBoxLayout()
        self.name = QLabel()
        self.name.setStyleSheet("font-size: 18pt; font-weight: 700;")
        self.developer = QLabel()
        self.summary = QLabel()
        self.summary.setWordWrap(True)
        text_col.addWidget(self.name)
        text_col.addWidget(self.developer)
        text_col.addWidget(self.summary)
        header.addLayout(text_col, 1)

        actions_col = QVBoxLayout()
        self.primary = QPushButton("Install")
        self.primary.clicked.connect(self.primary_clicked)
        self.remove = QPushButton("Remove")
        self.remove.clicked.connect(self.remove_clicked)
        self.bar = QProgressBar()
        self.bar.setMaximumHeight(8)
        self.bar.setTextVisible(False)
        self.status = QLabel()
        actions_col.addWidget(self.primary)
        actions_col.addWidget(self.remove)
        actions_col.addWidget(self.bar)
        actions_col.addWidget(self.status)
        header.addLayout(actions_col)

        self.body.addLayout(header)

        # Facts
        self.facts = QLabel()
        self.facts.setWordWrap(True)
        self.body.addWidget(self.facts)

        # Screenshots section title
        self.shots_title = QLabel("Screenshots")
        self.shots_title.setStyleSheet("font-size: 13pt; font-weight: 600;")
        self.body.addWidget(self.shots_title)

        # Screenshots row in horizontal scroll area
        shots_scroll = QScrollArea()
        shots_scroll.setFixedHeight(300)
        shots_scroll.setWidgetResizable(True)
        shots_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        shots_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        shots_widget = QWidget()
        self.shots_row = QHBoxLayout(shots_widget)
        self.shots_row.setContentsMargins(0, 0, 0, 0)
        shots_scroll.setWidget(shots_widget)
        self.body.addWidget(shots_scroll)

        # About section title
        about_title = QLabel("About")
        about_title.setStyleSheet("font-size: 13pt; font-weight: 600;")
        self.body.addWidget(about_title)

        # Description
        self.description = QLabel()
        self.description.setWordWrap(True)
        self.description.setTextFormat(Qt.PlainText)
        self.description.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.body.addWidget(self.description)

        # Permissions section title
        perms_title = QLabel("Permissions")
        perms_title.setStyleSheet("font-size: 13pt; font-weight: 600;")
        self.body.addWidget(perms_title)

        # Permissions
        self.permissions = QLabel()
        self.permissions.setWordWrap(True)
        self.body.addWidget(self.permissions)

        # What's new section title
        releases_title = QLabel("What's new")
        releases_title.setStyleSheet("font-size: 13pt; font-weight: 600;")
        self.body.addWidget(releases_title)

        # Releases
        self.releases = QLabel()
        self.releases.setWordWrap(True)
        self.body.addWidget(self.releases)

        # Links row
        links_row = QHBoxLayout()
        self.homepage = QPushButton("Homepage")
        self.homepage.clicked.connect(lambda: self.open_link("homepage"))
        self.bugs = QPushButton("Report a problem")
        self.bugs.clicked.connect(lambda: self.open_link("bugtracker"))
        self.donate = QPushButton("Donate")
        self.donate.clicked.connect(lambda: self.open_link("donation"))
        links_row.addWidget(self.homepage)
        links_row.addWidget(self.bugs)
        links_row.addWidget(self.donate)
        self.body.addLayout(links_row)

        self.body.addStretch()

        self.store.changed.connect(self.update_state)

    def show_app(self, app):
        """Display information for *app* dict and fetch full details."""
        self.app = app
        self.info = None
        self.token += 1
        token = self.token

        self.name.setText(app["name"])
        self.summary.setText(app["summary"])

        dev_text = html.escape(app.get("developer") or "")
        if app.get("verified"):
            dev_text += " · ✓ Verified"
        self.developer.setText(dev_text)

        # Icon placeholder
        self.icon.setText("")
        if app.get("icon"):
            workers.load_pixmap(
                app["icon"],
                lambda p, t=token: self._set_icon(p, t),
            )

        # Clear screenshots
        while self.shots_row.count():
            w = self.shots_row.takeAt(0)
            if w and w.widget():
                w.widget().deleteLater()

        self.facts.setText("Loading details…")
        self.description.setText("")
        self.permissions.setText("")
        self.releases.setText("")
        self.homepage.hide()
        self.bugs.hide()
        self.donate.hide()

        workers.run_async(
            flathub.details, app["id"],
            on_done=lambda d, t=token: self._show_details(d, t),
            on_error=lambda m, t=token: self._details_failed(m, t),
        )
        self.update_state()

    def _set_icon(self, pixmap, token):
        if token != self.token or pixmap is None:
            return
        self.icon.setPixmap(
            pixmap.scaled(96, 96, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    def _details_failed(self, message, token):
        if token != self.token:
            return
        self.facts.setText(f"Could not load the details: {html.escape(message)}")

    def _show_details(self, info, token):
        if token != self.token:
            return
        self.info = info

        # Curated picks carry no icon URL: use the one from the details.
        if not self.app.get("icon") and info.get("icon"):
            workers.load_pixmap(info["icon"], lambda p, t=token: self._set_icon(p, t))

        # Update developer label if we got more detail from API
        if not self.app.get("developer"):
            dev_text = html.escape(info.get("developer") or "")
            if self.app.get("verified"):
                dev_text += " · ✓ Verified"
            self.developer.setText(dev_text)

        # Facts
        parts = []
        if info["download_size"]:
            parts.append(f"Download {flathub.human_size(info['download_size'])}")
        if info["installed_size"]:
            parts.append(f"Installed {flathub.human_size(info['installed_size'])}")

        lic = info["license"] or ""
        if lic.startswith("LicenseRef-proprietary"):
            lic_display = "Proprietary"
        elif not lic:
            lic_display = "Unknown licence"
        else:
            lic_display = lic
        if info["free"]:
            lic_display += " (free software)"
        parts.append(lic_display)

        facts_html = html.escape("  ·  ".join(parts))
        if info["runtime_eol"] or info["eol"]:
            facts_html += f'<br><span style="color:{AMBER}">This app no longer gets updates from its developers.</span>'
        self.facts.setText(facts_html)

        # Screenshots
        shots = (info.get("screenshots") or [])[:6]
        if shots:
            self.shots_title.show()

            # Clear existing screenshot labels
            while self.shots_row.count():
                w = self.shots_row.takeAt(0)
                if w and w.widget():
                    w.widget().deleteLater()

            for url in shots:
                label = QLabel("…")
                label.setFixedSize(480, 270)
                label.setAlignment(Qt.AlignCenter)
                self.shots_row.addWidget(label)
                workers.load_pixmap(
                    url,
                    lambda p, l=label, t=token: self._set_shot(l, p, t),
                )
        else:
            self.shots_title.hide()

        # Description
        self.description.setText(info["description"] or info["summary"])

        # Permissions
        warnings = flathub.permission_warnings(info["permissions"])
        if not warnings:
            self.permissions.setText("Runs in its sandbox with no extra access.")
        else:
            lines = []
            for w in warnings:
                escaped = html.escape(w)
                risky = any(r in w for r in RISKY)
                if risky:
                    lines.append(f'<span style="color:{AMBER}">⚠ {escaped}</span>')
                else:
                    lines.append(f"• {escaped}")
            self.permissions.setText("<br>".join(lines))

        # Releases
        rels = (info.get("releases") or [])[:3]
        if rels:
            rel_parts = []
            for r in rels:
                line = f"<b>{html.escape(r['version'])}</b> {html.escape(r['date'])}"
                notes = r.get("notes", "")
                if notes:
                    escaped_notes = html.escape(notes).replace("\n", "<br>")
                    line += f"<br>{escaped_notes}"
                rel_parts.append(line)
            self.releases.setText("<br><br>".join(rel_parts))
        else:
            self.releases.setText("No release notes.")

        # Links
        for btn, key in [(self.homepage, "homepage"), (self.bugs, "bugtracker"), (self.donate, "donation")]:
            url = info.get(key, "")
            if url.startswith("https://"):
                btn.show()
            else:
                btn.hide()

    def _set_shot(self, label, pixmap, token):
        if token != self.token or pixmap is None:
            return
        try:
            label.setPixmap(
                pixmap.scaled(480, 270, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        except RuntimeError:
            pass

    def open_link(self, key):
        url = (self.info or {}).get(key, "")
        if url.startswith("https://"):
            QDesktopServices.openUrl(QUrl(url))

    def update_state(self):
        if not self.app:
            return
        app_id = self.app["id"]
        busy = self.store.busy.get(app_id)
        installed = app_id in self.store.installed
        has_update = app_id in self.store.updates

        if installed and has_update:
            self.primary.setText("Update")
        elif installed:
            self.primary.setText("Open")
        else:
            self.primary.setText("Install")

        self.primary.setEnabled(not busy)
        self.remove.setEnabled(not busy)
        self.remove.setVisible(installed)

        show_progress = bool(busy)
        self.bar.setVisible(show_progress)
        self.status.setVisible(show_progress)

        if busy:
            pct, text = self.store.progress.get(app_id, (-1, ""))
            if pct < 0:
                self.bar.setRange(0, 0)
            else:
                self.bar.setRange(0, 100)
                self.bar.setValue(pct)
            status_text = text or {
                "install": "Installing…",
                "remove": "Removing…",
                "update": "Updating…",
            }[busy]
            self.status.setText(status_text)

    def primary_clicked(self):
        app_id = self.app["id"]
        installed = app_id in self.store.installed
        if installed and app_id in self.store.updates:
            self.store.run(app_id, "update", self)
        elif installed:
            self.store.open(app_id)
        else:
            warnings = (
                flathub.permission_warnings(self.info["permissions"])
                if self.info else []
            )
            risky = [w for w in warnings if any(r in w for r in RISKY)]
            if risky:
                msg = (
                    f"{self.app['name']} asks to:\n\n"
                    + "\n".join("• " + w for w in risky)
                    + "\n\nInstall it anyway?"
                )
                if QMessageBox.question(self, "Stash", msg) != QMessageBox.Yes:
                    return
            self.store.run(app_id, "install", self)

    def remove_clicked(self):
        app_id = self.app["id"]
        if QMessageBox.question(
            self, "Stash", f"Remove {self.app['name']}?"
        ) == QMessageBox.Yes:
            self.store.run(app_id, "remove", self)
