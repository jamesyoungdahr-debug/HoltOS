"""Managing apps in Stash: the Installed page (sizes, sort, remove with or without data, clean up unused runtimes) and the Updates page (update one or all, with progress)."""

import html
import os

from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

import flathub

AMBER = "#FFB84D"
ICON = 48
ICON_DIRS = (
    "/var/lib/flatpak/exports/share/icons/hicolor",
    os.path.expanduser("~/.local/share/flatpak/exports/share/icons/hicolor"),
)


def local_icon(app_id):
    """Return a QIcon for *app_id* from the local Flatpak icon dirs, or a theme fallback."""
    for base in ICON_DIRS:
        for size in ("128x128", "256x256", "64x64", "48x48", "scalable"):
            for ext in ("png", "svg"):
                path = os.path.join(base, size, "apps", f"{app_id}.{ext}")
                if os.path.exists(path):
                    return QIcon(path)
    return QIcon.fromTheme(app_id, QIcon.fromTheme("application-x-executable"))


def scroll_list():
    """Return a (scroll_area, inner_layout) pair ready for inserting rows."""
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)

    inner = QWidget()
    layout = QVBoxLayout(inner)
    layout.addStretch()
    scroll.setWidget(inner)
    return scroll, layout


class AppRow(QFrame):
    """One installed app with its actions and progress."""

    def __init__(self, app_id, store, on_open, on_remove):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)

        self._app_id = app_id
        self._store = store
        self._on_open = on_open
        self._on_remove = on_remove

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)

        icon_label = QLabel()
        icon_label.setPixmap(local_icon(app_id).pixmap(ICON, ICON))
        layout.addWidget(icon_label)

        text_layout = QVBoxLayout()
        self.title = QLabel()
        self.detail = QLabel()
        self.bar = QProgressBar()
        self.bar.setMaximumHeight(6)
        self.bar.setTextVisible(False)
        self.status = QLabel()
        text_layout.addWidget(self.title)
        text_layout.addWidget(self.detail)
        text_layout.addWidget(self.bar)
        text_layout.addWidget(self.status)
        layout.addLayout(text_layout, 1)

        btn_layout = QVBoxLayout()
        self.open_btn = QPushButton("Open")
        self.details_btn = QPushButton("Details")
        self.update_btn = QPushButton("Update")
        self.remove_btn = QPushButton("Remove")
        self.open_btn.clicked.connect(lambda: store.open(app_id))
        self.details_btn.clicked.connect(self._on_details)
        self.update_btn.clicked.connect(lambda: store.run(app_id, "update", self))
        self.remove_btn.clicked.connect(lambda: on_remove(app_id))
        btn_layout.addWidget(self.open_btn)
        btn_layout.addWidget(self.details_btn)
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.remove_btn)
        layout.addLayout(btn_layout)

        store.changed.connect(self.refresh)
        self.refresh()

    def _on_details(self):
        """Open this app's page."""
        info = self._store.installed.get(self._app_id, {})
        self._on_open({
            "id": self._app_id,
            "name": info.get("name", self._app_id),
            "summary": info.get("summary", ""),
        })

    def refresh(self):
        """Re-read store state and update the row widgets."""
        info = self._store.installed.get(self._app_id)
        if info is None and self._app_id not in self._store.busy:
            return
        if info is None:
            info = {"name": self._app_id}

        title = f"<b>{html.escape(info.get('name', self._app_id))}</b>"
        if info.get("eol"):
            title += f' <span style="color:{AMBER}">· no longer updated</span>'
        self.title.setText(title)

        parts = []
        version = info.get("version")
        if version:
            parts.append(f"Version {version}")
        installed_size = info.get("installed_size")
        if installed_size:
            parts.append(flathub.human_size(installed_size))
        self.detail.setText(" · ".join(parts))

        busy = self._store.busy.get(self._app_id)
        self.update_btn.setVisible(self._app_id in self._store.updates)
        enabled = not bool(busy)
        self.open_btn.setEnabled(enabled)
        self.details_btn.setEnabled(enabled)
        self.update_btn.setEnabled(enabled)
        self.remove_btn.setEnabled(enabled)

        show_progress = bool(busy)
        self.bar.setVisible(show_progress)
        self.status.setVisible(show_progress)

        if busy:
            pct, text = self._store.progress.get(self._app_id, (-1, ""))
            if pct < 0:
                self.bar.setRange(0, 0)
            else:
                self.bar.setRange(0, 100)
                self.bar.setValue(pct)
            self.status.setText(text)

    def close_row(self):
        """Disconnect and schedule deletion."""
        try:
            self._store.changed.disconnect(self.refresh)
        except (RuntimeError, TypeError):
            pass
        self.deleteLater()


class InstalledPage(QWidget):
    """The Installed apps page with sorting, removal, and runtime cleanup."""

    def __init__(self, store, on_open):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        top = QHBoxLayout()
        self.message = QLabel()
        top.addWidget(self.message)
        top.addStretch()
        top.addWidget(QLabel("Sort by"))
        self.sort = QComboBox()
        self.sort.addItems(["Name", "Size"])
        self.sort.currentIndexChanged.connect(lambda: self.rebuild(force=True))
        top.addWidget(self.sort)
        layout.addLayout(top)

        self.cleanup = QPushButton()
        self.cleanup.clicked.connect(self.clean_up)
        layout.addWidget(self.cleanup)

        scroll, list_layout = scroll_list()
        self._list_layout = list_layout
        layout.addWidget(scroll)

        self.rows = {}
        self.pending_data = set()
        self._store = store
        self._on_open = on_open

        store.changed.connect(self.rebuild)
        self.rebuild()

    def rebuild(self, force=False):
        """Re-sync the row widgets with current store state."""
        store = self._store
        installed = store.installed

        for app_id in list(self.pending_data):
            if app_id not in installed and app_id not in store.busy:
                store.remove_data(app_id)
        cleaned = {k for k in self.pending_data if k in installed or k in store.busy}
        self.pending_data = cleaned

        for app_id, row in list(self.rows.items()):
            if app_id not in installed and app_id not in store.busy:
                row.close_row()
                del self.rows[app_id]

        if force:
            for row in list(self.rows.values()):
                row.close_row()
            self.rows.clear()

        sort_index = self.sort.currentIndex()
        ids = sorted(
            set(installed.keys()) | set(store.busy.keys()),
            key=lambda i: installed.get(i, {}).get("name", i).lower() if sort_index == 0 else -(installed.get(i, {}).get("installed_size", 0)),
        )

        for app_id in ids:
            if app_id not in self.rows:
                row = AppRow(app_id, store, self._on_open, self.remove)
                self._list_layout.insertWidget(self._list_layout.count() - 1, row)
                self.rows[app_id] = row

        for idx, app_id in enumerate(ids):
            if app_id in self.rows:
                row = self.rows[app_id]
                self._list_layout.removeWidget(row)
                self._list_layout.insertWidget(idx, row)

        n = len(installed)
        total = sum(i.get("installed_size", 0) for i in installed.values())

        if not store.loaded:
            self.message.setText("Loading…")
        elif store.error:
            self.message.setText(f"Could not read the installed apps: {store.error}")
        else:
            text = f"{n} app(s) installed"
            if total > 0:
                text += f", {flathub.human_size(total)} in total"
            self.message.setText(text)

        count, size = store.unused
        self.cleanup.setVisible(count > 0)
        if count > 0:
            self.cleanup.setText(f"Clean up {count} unused runtime(s) ({flathub.human_size(size)})")
        self.cleanup.setEnabled("*" not in store.busy)

    def remove(self, app_id):
        """Show a confirmation dialog and queue removal for *app_id*."""
        info = self._store.installed.get(app_id, {})
        name = info.get("name", app_id)
        box = QMessageBox(
            QMessageBox.Question,
            "Stash",
            f"Remove {name}?",
            QMessageBox.Yes | QMessageBox.No,
            self,
        )
        size = self._store.data_size(app_id)
        check = None
        if size:
            check = QCheckBox(f"Also delete its settings and data ({flathub.human_size(size)})")
            box.setCheckBox(check)

        if box.exec() != QMessageBox.Yes:
            return

        if check and check.isChecked():
            self.pending_data.add(app_id)

        self._store.run(app_id, "remove", self)

    def clean_up(self):
        """Confirm and prune unused runtimes."""
        count, size = self._store.unused
        reply = QMessageBox.question(
            self,
            "Stash",
            f"Remove {count} runtime(s) no app uses any more? This frees {flathub.human_size(size)}.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self._store.prune(self)


class UpdatesPage(QWidget):
    """The Updates page showing available app and runtime updates."""

    def __init__(self, store, on_open):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        top = QHBoxLayout()
        self.message = QLabel()
        font = self.message.font()
        font.setPointSize(13)
        font.setWeight(QFont.Weight.DemiBold)
        self.message.setFont(font)
        top.addWidget(self.message)
        top.addStretch()
        self.check_btn = QPushButton("Check again")
        self.all_btn = QPushButton("Update all")
        self.cancel_btn = QPushButton("Cancel")
        self.check_btn.clicked.connect(lambda: store.refresh())
        self.all_btn.clicked.connect(lambda: store.update_all(self))
        self.cancel_btn.clicked.connect(lambda: store.cancel("*"))
        top.addWidget(self.check_btn)
        top.addWidget(self.all_btn)
        top.addWidget(self.cancel_btn)
        layout.addLayout(top)

        self.bar = QProgressBar()
        self.bar.setMaximumHeight(8)
        self.bar.setTextVisible(False)
        self.status = QLabel()
        layout.addWidget(self.bar)
        layout.addWidget(self.status)

        self.note = QLabel()
        self.note.setWordWrap(True)
        layout.addWidget(self.note)

        scroll, list_layout = scroll_list()
        self._list_layout = list_layout
        layout.addWidget(scroll)

        self.rows = {}
        self._store = store
        self._on_open = on_open

        store.changed.connect(self.rebuild)
        self.rebuild()

    def rebuild(self):
        """Re-sync the row widgets with current update state."""
        store = self._store
        ids = sorted(store.updates, key=lambda i: store.installed.get(i, {}).get("name", i).lower())

        for app_id, row in list(self.rows.items()):
            if app_id not in ids and app_id not in store.busy:
                row.close_row()
                del self.rows[app_id]

        for app_id in ids:
            if app_id not in self.rows:
                row = AppRow(app_id, store, self._on_open, lambda i: None)
                row.remove_btn.hide()
                self._list_layout.insertWidget(self._list_layout.count() - 1, row)
                self.rows[app_id] = row

        apps = len(ids)
        runtimes = store.runtime_updates

        if not store.loaded:
            self.message.setText("Checking for updates…")
        elif apps or runtimes:
            text = f"{apps} app update(s)"
            if runtimes:
                text += f" and {runtimes} runtime update(s)"
            self.message.setText(text)
        else:
            self.message.setText("Everything is up to date.")

        self.note.setText(
            "Runtimes are the shared parts apps are built on; Update all includes them." if runtimes else ""
        )

        self.all_btn.setEnabled((apps or runtimes) and "*" not in store.busy)
        busy_all = "*" in store.busy
        self.cancel_btn.setVisible(busy_all)
        self.bar.setVisible(busy_all)
        self.status.setVisible(busy_all)

        if busy_all:
            pct, text = store.progress.get("*", (-1, ""))
            if pct < 0:
                self.bar.setRange(0, 0)
            else:
                self.bar.setRange(0, 100)
                self.bar.setValue(pct)
            self.status.setText(text)
