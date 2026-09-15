"""The Snapshots tab of HoltOS Updates: the Btrfs snapshots HoltOS keeps
(before every update, and on request), with Create, Restore and Delete.

Reading the list needs no privileges (/var/lib/holtos/snapshots.log is
world-readable). Creating, restoring and deleting run the root helpers
through pkexec, in the background so the window never freezes.
"""
import os
import subprocess
from datetime import datetime, timezone

from PySide6.QtCore import QProcess, QTimer
from PySide6.QtWidgets import (
    QHBoxLayout, QHeaderView, QLabel, QMessageBox, QPushButton, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)

SNAP_LOG = "/var/lib/holtos/snapshots.log"
SNAPSHOT = "/usr/local/bin/holtos-btrfs-snapshot"
RESTORE = "/usr/local/bin/holtos-btrfs-restore"
REASONS = {
    "config": "Before a HoltOS update",
    "system": "Before a system update",
    "manual": "Created by you",
    "pre-restore": "Before a snapshot was restored",
}


def read_snapshots():
    """Snapshots from the log, newest first: dicts with when, label, name."""
    entries = []
    try:
        with open(SNAP_LOG) as f:
            for line in f:
                parts = line.rstrip("\n").split("\t")
                if len(parts) == 3 and parts[2]:
                    entries.append({"when": parts[0], "label": parts[1], "name": parts[2]})
    except OSError:
        pass
    entries.reverse()
    return entries


def friendly(stamp):
    try:
        when = datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).astimezone()
    except ValueError:
        return stamp
    return when.strftime("%d %b %Y at %H:%M")


class SnapshotsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.snapshots = []
        self.proc = None
        self.mtime = None
        layout = QVBoxLayout(self)

        intro = QLabel(
            "HoltOS takes a snapshot of the system before every update. Restoring one "
            "undoes everything installed or changed on the system since then; your home "
            "folder is never touched."
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Taken", "Why"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self.update_buttons)
        layout.addWidget(self.table, 1)

        self.status = QLabel()
        self.status.setWordWrap(True)
        layout.addWidget(self.status)

        row = QHBoxLayout()
        self.create_btn = QPushButton("Create snapshot now")
        self.restore_btn = QPushButton("Restore...")
        self.delete_btn = QPushButton("Delete...")
        self.refresh_btn = QPushButton("Refresh")
        self.create_btn.clicked.connect(self.create)
        self.restore_btn.clicked.connect(self.restore)
        self.delete_btn.clicked.connect(self.delete)
        self.refresh_btn.clicked.connect(lambda: self.refresh(force=True))
        row.addWidget(self.create_btn)
        row.addWidget(self.restore_btn)
        row.addWidget(self.delete_btn)
        row.addStretch()
        row.addWidget(self.refresh_btn)
        layout.addLayout(row)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(5000)
        self.refresh(force=True)

    def refresh(self, force=False):
        try:
            mtime = os.path.getmtime(SNAP_LOG)
        except OSError:
            mtime = None
        if not force and mtime == self.mtime:
            return
        self.mtime = mtime
        self.snapshots = read_snapshots()
        self.table.setRowCount(len(self.snapshots))
        for row, snap in enumerate(self.snapshots):
            self.table.setItem(row, 0, QTableWidgetItem(friendly(snap["when"])))
            self.table.setItem(row, 1, QTableWidgetItem(REASONS.get(snap["label"], snap["label"])))
        if not self.snapshots and not self.proc:
            self.status.setText("No snapshots yet. HoltOS takes one before the next update.")
        self.update_buttons()

    def selected(self):
        row = self.table.currentRow()
        if 0 <= row < len(self.snapshots) and self.table.selectionModel().hasSelection():
            return self.snapshots[row]
        return None

    def update_buttons(self):
        idle = self.proc is None
        has = self.selected() is not None
        self.create_btn.setEnabled(idle)
        self.restore_btn.setEnabled(idle and has)
        self.delete_btn.setEnabled(idle and has)

    def run_root(self, args, busy_text, on_done):
        if self.proc is not None:
            return
        self.status.setText(busy_text)
        proc = QProcess(self)
        proc.setProcessChannelMode(QProcess.MergedChannels)
        proc.finished.connect(lambda code, _status, p=proc: self.finished(p, code, on_done))
        self.proc = proc
        self.update_buttons()
        proc.start("pkexec", args)

    def finished(self, proc, code, on_done):
        output = bytes(proc.readAll()).decode(errors="replace").strip()
        proc.deleteLater()
        self.proc = None
        self.status.setText("")
        self.refresh(force=True)
        on_done(code, output)

    def failed(self, what, output):
        tail = "\n".join(output.splitlines()[-8:])
        QMessageBox.warning(self, "HoltOS Updates", f"{what} did not work:\n\n{tail}")

    def create(self):
        def done(code, output):
            if code == 0:
                self.status.setText("Snapshot created.")
            elif code not in (126, 127):
                self.failed("Creating the snapshot", output)
        self.run_root([SNAPSHOT, "manual"], "Creating a snapshot...", done)

    def restore(self):
        snap = self.selected()
        if not snap:
            return
        answer = QMessageBox.question(
            self, "HoltOS Updates",
            f"Restore the system to how it was on {friendly(snap['when'])}?\n\n"
            "Everything installed or changed on the system since then is undone after a "
            "restart. Your home folder is kept. The current system is saved as a snapshot first.",
        )
        if answer != QMessageBox.Yes:
            return

        def done(code, output):
            if code == 0:
                again = QMessageBox.question(self, "HoltOS Updates", "Snapshot restored. Restart now to finish?")
                if again == QMessageBox.Yes:
                    subprocess.Popen(["systemctl", "reboot"])
            elif code not in (126, 127):
                self.failed("Restoring the snapshot", output)
        self.run_root([RESTORE, snap["name"]], "Restoring the snapshot... this can take a minute.", done)

    def delete(self):
        snap = self.selected()
        if not snap:
            return
        answer = QMessageBox.question(
            self, "HoltOS Updates",
            f"Delete the snapshot from {friendly(snap['when'])}? It cannot be restored afterwards.",
        )
        if answer != QMessageBox.Yes:
            return

        def done(code, output):
            if code == 0:
                self.status.setText("Snapshot deleted.")
            elif code not in (126, 127):
                self.failed("Deleting the snapshot", output)
        self.run_root([SNAPSHOT, "--delete", snap["name"]], "Deleting the snapshot...", done)
