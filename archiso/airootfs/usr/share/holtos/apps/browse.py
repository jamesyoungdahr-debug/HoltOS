"""Browsing in HoltOS Apps: app tiles, the Browse page (HoltOS picks, Flathub collections, categories) and a list page for categories, "See all" and search results."""

import html
import json
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
import flathub
import workers

CATALOG_PATH = "/usr/share/holtos/apps.json"
ICON = 64
COLUMNS = 3


class AppTile(QFrame):
    """A clickable app tile."""

    def __init__(self, app, store, on_open):
        super().__init__()
        self.app = app
        self.store = store
        self.on_open = on_open
        self.setFrameShape(QFrame.StyledPanel)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumWidth(250)

        layout = QHBoxLayout(self)

        self.icon = QLabel()
        self.icon.setFixedSize(ICON, ICON)
        default_pixmap = QIcon.fromTheme("application-x-executable").pixmap(ICON, ICON)
        self.icon.setPixmap(default_pixmap)
        self.icon.setAlignment(Qt.AlignTop)
        layout.addWidget(self.icon)

        text_layout = QVBoxLayout()

        name_label = QLabel(f"<b>{html.escape(app['name'])}</b>")
        if app.get("verified"):
            name_label.setText(name_label.text() + ' <span style="color:#28E0C8">✓</span>')
        name_label.setWordWrap(False)
        text_layout.addWidget(name_label)

        summary = app.get("summary", "") or ""
        if len(summary) > 90:
            summary = summary[:88].rstrip() + "…"
        summary_label = QLabel(summary)
        summary_label.setTextFormat(Qt.PlainText)
        # Top-aligned, so text that still runs long is cut at the bottom
        # instead of spilling up over the app's name.
        summary_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        summary_label.setWordWrap(True)
        line = summary_label.fontMetrics().lineSpacing()
        summary_label.setFixedHeight(line * 2 + 2)
        text_layout.addWidget(summary_label)

        self.bar = QProgressBar()
        self.bar.setMaximumHeight(6)
        self.bar.setTextVisible(False)
        text_layout.addWidget(self.bar)

        button_row = QHBoxLayout()
        self.button = QPushButton()
        self.button.clicked.connect(self.button_clicked)
        button_row.addWidget(self.button)
        button_row.addStretch()
        text_layout.addLayout(button_row)

        layout.addLayout(text_layout)

        store.changed.connect(self.update_state)
        self.update_state()

        if app.get("icon"):
            workers.load_pixmap(app["icon"], self._set_icon)
        else:
            workers.run_async(
                flathub.details,
                app["id"],
                on_done=lambda info: info.get("icon") and workers.load_pixmap(info["icon"], self._set_icon),
                on_error=lambda m: None,
            )

    def _set_icon(self, pixmap):
        if pixmap is None:
            return
        try:
            self.icon.setPixmap(pixmap.scaled(ICON, ICON, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except RuntimeError:
            pass

    def update_state(self):
        id = self.app["id"]
        busy = self.store.busy.get(id)
        installed = id in self.store.installed
        if installed and id in self.store.updates:
            text = "Update"
        elif installed:
            text = "Open"
        else:
            text = "Install"
        self.button.setText(text)
        self.button.setEnabled(not busy)
        self.bar.setVisible(bool(busy))
        if busy:
            pct = self.store.progress.get(id, (-1, ""))[0]
            if pct < 0:
                self.bar.setRange(0, 0)
            else:
                self.bar.setRange(0, 100)
                self.bar.setValue(pct)

    def button_clicked(self):
        id = self.app["id"]
        installed = id in self.store.installed
        if installed:
            if id in self.store.updates:
                self.store.run(id, "update", self)
            else:
                self.store.open(id)
        else:
            self.on_open(self.app)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.on_open(self.app)
        super().mouseReleaseEvent(event)

    def close_tile(self):
        try:
            self.store.changed.disconnect(self.update_state)
        except (RuntimeError, TypeError):
            pass
        self.deleteLater()


class TileGrid(QWidget):
    """Tiles in COLUMNS columns."""

    def __init__(self, store, on_open):
        super().__init__()
        self.store = store
        self.on_open = on_open
        self.grid = QGridLayout(self)
        self.tiles = []

    def set_apps(self, apps):
        self.clear()
        self.add_apps(apps)

    def add_apps(self, apps):
        for app in apps:
            if not app.get("id"):
                continue
            tile = AppTile(app, self.store, self.on_open)
            n = len(self.tiles)
            self.grid.addWidget(tile, n // COLUMNS, n % COLUMNS)
            self.tiles.append(tile)

    def clear(self):
        for t in self.tiles:
            t.close_tile()
        self.tiles = []


def section_title(text):
    label = QLabel(text)
    label.setStyleSheet("font-size: 15pt; font-weight: 700;")
    return label


class BrowsePage(QScrollArea):
    """HoltOS picks, Flathub collections and categories."""

    def __init__(self, store, on_open, on_list):
        super().__init__()
        self.store = store
        self.on_open = on_open
        self.on_list = on_list
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)
        host = QWidget()
        self.body = QVBoxLayout(host)
        self.setWidget(host)

        # Categories
        cat_title = section_title("Categories")
        self.body.addWidget(cat_title)
        cat_grid = QGridLayout()
        for idx, (key, title) in enumerate(flathub.CATEGORIES):
            btn = QPushButton(title.replace("&", "&&"))
            row = idx // 5
            col = idx % 5
            cat_grid.addWidget(btn, row, col)
            btn.clicked.connect(lambda _, k=key: on_list(k, lambda page, _k=k: flathub.category(_k, page, 48)))
        self.body.addLayout(cat_grid)

        # HoltOS picks
        try:
            with open(CATALOG_PATH, "r", encoding="utf-8") as f:
                catalog = json.load(f)
        except (OSError, ValueError):
            catalog = {"categories": []}

        for category in catalog.get("categories", []):
            cat_name = category.get("title", "")
            apps = category.get("apps", [])

            header_row = QHBoxLayout()
            header_row.addWidget(section_title(cat_name))
            header_row.addStretch()
            see_all_btn = QPushButton("See all")
            see_all_btn.clicked.connect(
                lambda _, t=cat_name, a=apps: on_list(t, lambda page, _a=a: _a if page == 1 else [])
            )
            header_row.addWidget(see_all_btn)
            self.body.addLayout(header_row)

            grid = TileGrid(store, on_open)
            grid.set_apps(apps[:6])
            self.body.addWidget(grid)

        # Flathub rows
        flathub_rows = [
            ("popular", "Popular on Flathub"),
            ("trending", "Trending"),
            ("recently-added", "New on Flathub"),
            ("recently-updated", "Recently updated"),
        ]

        for name, title in flathub_rows:
            header_row = QHBoxLayout()
            header_row.addWidget(section_title(title))
            header_row.addStretch()
            see_all_btn = QPushButton("See all")
            see_all_btn.clicked.connect(
                lambda _, t=title, n=name: on_list(t, lambda page, _n=n: flathub.collection(_n, page, 48))
            )
            header_row.addWidget(see_all_btn)
            self.body.addLayout(header_row)

            grid = TileGrid(store, on_open)
            self.body.addWidget(grid)

            status = QLabel("Loading…")
            self.body.addWidget(status)

            workers.run_async(
                flathub.collection,
                name,
                1,
                6,
                on_done=lambda apps, g=grid, s=status: (s.hide(), g.set_apps(apps)),
                on_error=lambda m, s=status: s.setText("Flathub could not be reached. Check the internet connection."),
            )

        self.body.addStretch()


class ListPage(QWidget):
    """A titled grid of apps with Back and Load more."""

    def __init__(self, store, on_open, on_back):
        super().__init__()
        layout = QVBoxLayout(self)

        top_row = QHBoxLayout()
        back_btn = QPushButton("← Back")
        back_btn.clicked.connect(on_back)
        top_row.addWidget(back_btn)
        self.title = QLabel()
        self.title.setStyleSheet("font-size: 15pt; font-weight: 700;")
        top_row.addWidget(self.title)
        top_row.addStretch()
        layout.addLayout(top_row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll_host = QWidget()
        scroll_layout = QVBoxLayout(scroll_host)
        scroll.setWidget(scroll_host)

        self.grid = TileGrid(store, on_open)
        scroll_layout.addWidget(self.grid)

        self.status = QLabel()
        scroll_layout.addWidget(self.status)

        self.more = QPushButton("Load more")
        self.more.clicked.connect(self.load_more)
        scroll_layout.addWidget(self.more)
        scroll_layout.addStretch()

        layout.addWidget(scroll)

        self.loader = None
        self.page = 0
        self.token = 0

    def show_list(self, title, loader):
        self.title.setText(title)
        self.loader = loader
        self.page = 0
        self.token += 1
        self.grid.clear()
        self.more.hide()
        self.load_more()

    def load_more(self):
        self.page += 1
        token = self.token
        page = self.page
        self.status.setText("Loading…")
        self.status.show()
        self.more.setEnabled(False)
        workers.run_async(
            self.loader,
            page,
            on_done=lambda apps, t=token: self._loaded(apps, t),
            on_error=lambda m, t=token: self._failed(m, t),
        )

    def _loaded(self, apps, token):
        if token != self.token:
            return
        self.grid.add_apps(apps)
        none = not self.grid.tiles
        self.status.setText("No apps found." if none else "")
        self.status.setVisible(none)
        self.more.setEnabled(True)
        self.more.setVisible(len(apps) >= 48)

    def _failed(self, message, token):
        if token != self.token:
            return
        self.status.setText(f"Could not load apps: {message}")
        self.more.setEnabled(True)
