"""What is installed, what can be updated, and a queue of Flatpak jobs for HoltOS Apps. Jobs run one at a time through flatpak_helper.py in its own process; its JSON lines become progress the pages show."""

import json
import os
import re
import shutil
import sys

from PySide6.QtCore import QObject, QProcess, Signal
from PySide6.QtWidgets import QMessageBox


HELPER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flatpak_helper.py")
APP_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{2,254}$")
VERBS = {
    "install": "Installing",
    "remove": "Removing",
    "update": "Updating",
    "update-all": "Updating apps",
    "prune": "Cleaning up",
}
FAILED = {
    "install": "install",
    "remove": "remove",
    "update": "update",
    "update-all": "update apps",
    "prune": "clean up",
}


def _helper_args(*args):
    """Build the argument list for a helper invocation."""
    return [HELPER, *args]


class Store(QObject):
    """Central Flatpak job manager and state holder for HoltOS Apps."""

    changed = Signal()

    def __init__(self):
        super().__init__()
        self.installed = {}
        self.updates = set()
        self.runtime_updates = 0
        self.unused = (0, 0)
        self.busy = {}
        self.progress = {}
        self.loaded = False
        self.error = ""

        self._queue = []
        self._proc = None
        self._job = None
        self._ops = []
        self._current = 0
        self._buffer = b""
        self._cancelled = False

        self.refresh()

    # ------------------------------------------------------------------ public

    def refresh(self):
        """Run three short helper queries without blocking."""
        self._query(["list"], self._got_list)
        self._query(["updates"], self._got_updates)
        self._query(["unused"], self._got_unused)

    def run(self, app_id, action, parent):
        """Queue a single-app install / remove / update."""
        if action not in ("install", "remove", "update"):
            return
        if not APP_ID.match(app_id):
            return
        if app_id in self.busy:
            return
        self._enqueue(app_id, action, [app_id], parent)

    def update_all(self, parent):
        """Queue an update-all job."""
        if "*" in self.busy or not (self.updates or self.runtime_updates):
            return
        self._enqueue("*", "update-all", [], parent)

    def prune(self, parent):
        """Queue a prune job."""
        if "*" in self.busy:
            return
        self._enqueue("*", "prune", [], parent)

    def cancel(self, key):
        """Cancel a running or queued job identified by *key*."""
        if self._job and self._job[0] == key and self._proc is not None:
            self._cancelled = True
            self._proc.terminate()
            return

        # Remove from queue if present
        new_queue = [e for e in self._queue if e[0] != key]
        if len(new_queue) < len(self._queue):
            self._queue = new_queue
            self.busy.pop(key, None)
            self.progress.pop(key, None)

            # For update-all also clear per-app busy markers
            if key == "*":
                for app_id in list(self.busy.keys()):
                    if self.busy[app_id] == "update" and app_id != "*" and app_id not in [e[0] for e in self._queue]:
                        del self.busy[app_id]
                        self.progress.pop(app_id, None)

            self.changed.emit()

    def open(self, app_id):
        """Launch an installed Flatpak app."""
        if APP_ID.match(app_id):
            QProcess.startDetached("flatpak", ["run", app_id])

    def data_size(self, app_id):
        """Return the total size in bytes of user data for *app_id*."""
        path = os.path.join(os.path.expanduser("~"), ".var", "app", app_id)
        if not APP_ID.match(app_id) or not os.path.isdir(path):
            return 0
        total = 0
        try:
            for dirpath, _dirnames, filenames in os.walk(path, followlinks=False):
                for fn in filenames:
                    try:
                        total += os.lstat(os.path.join(dirpath, fn)).st_size
                    except OSError:
                        pass
        except OSError:
            pass
        return total

    def remove_data(self, app_id):
        """Remove user data directory for a non-installed *app_id*."""
        if not APP_ID.match(app_id):
            return False
        if app_id in self.installed or app_id in self.busy:
            return False
        home = os.path.expanduser("~")
        path = os.path.join(home, ".var", "app", app_id)
        base = os.path.realpath(os.path.join(home, ".var", "app"))
        real = os.path.realpath(path)
        if os.path.dirname(real) != base:
            return False
        shutil.rmtree(real, ignore_errors=True)
        return True

    # ------------------------------------------------------------------ private helpers

    def _query(self, args, handler):
        """Start a short-lived helper query and call *handler* per event."""
        p = QProcess(self)
        p.setProcessChannelMode(QProcess.SeparateChannels)
        p.finished.connect(lambda code, status, p=p: self._query_done(p, handler))
        p.start(sys.executable or "python3", _helper_args(*args))

    def _query_done(self, p, handler):
        """Collect output from a finished query and dispatch to *handler*."""
        try:
            data = bytes(p.readAllStandardOutput()).decode(errors="replace")
            p.deleteLater()
        except RuntimeError:
            return  # the window is closing
        for line in data.splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            handler(event)

    def _got_list(self, event):
        """Handle a list query result."""
        if event.get("event") == "list":
            self.installed = {a["id"]: a for a in event.get("apps", [])}
            self.loaded = True
            self.error = ""
        elif event.get("event") == "failed":
            self.error = event.get("message", "")
            self.loaded = True
        self.changed.emit()

    def _got_updates(self, event):
        """Handle an updates query result."""
        if event.get("event") == "updates":
            refs = event.get("refs", [])
            apps = {r["id"] for r in refs if r.get("kind") == "app"}
            self.updates = apps
            self.runtime_updates = sum(1 for r in refs if r.get("kind") == "runtime")
        self.changed.emit()

    def _got_unused(self, event):
        """Handle an unused query result."""
        if event.get("event") == "unused":
            self.unused = (int(event.get("count", 0)), int(event.get("size", 0)))
        self.changed.emit()

    # ------------------------------------------------------------------ job queue

    def _enqueue(self, key, action, ids, parent):
        """Add a job to the queue and start processing if idle."""
        self._queue.append((key, action, ids, parent))
        self.busy[key] = action
        self.progress[key] = (-1, "Waiting…")

        # For update-all also mark every updatable app as busy
        if action == "update-all":
            for app_id in self.updates:
                if app_id not in self.busy:
                    self.busy[app_id] = "update"
                    self.progress[app_id] = (-1, "Waiting…")

        self.changed.emit()
        self._next()

    def _next(self):
        """Start the next queued job if no process is running."""
        if self._proc is not None or not self._queue:
            return

        key, action, ids, parent = self._queue.pop(0)
        self._job = (key, action, ids, parent)
        self._ops = []
        self._current = 0
        self._buffer = b""
        self._cancelled = False
        self._job_error = ""

        self.progress[key] = (-1, VERBS[action] + "…")

        p = QProcess(self)
        p.setProcessChannelMode(QProcess.SeparateChannels)
        p.readyReadStandardOutput.connect(self._read)
        p.finished.connect(self._finished)
        # If Python or the helper cannot start, finished never fires: treat it
        # as a failed job so the queue moves on.
        p.errorOccurred.connect(
            lambda error, p=p: error == QProcess.FailedToStart and self._proc is p and self._finished(1, None)
        )
        self._proc = p
        p.start(sys.executable or "python3", _helper_args(action, *ids))
        self.changed.emit()

    # ------------------------------------------------------------------ job I/O

    def _read(self):
        """Read available output from the running helper process."""
        self._buffer += bytes(self._proc.readAllStandardOutput())
        while b"\n" in self._buffer:
            line, self._buffer = self._buffer.split(b"\n", 1)
            try:
                event = json.loads(line)
            except ValueError:
                continue
            self._event(event)

    def _event(self, event):
        """Dispatch a single JSON-line event from the helper."""
        key, action, ids, parent = self._job
        kind = event.get("event")

        if kind == "operation":
            index = int(event.get("index", 1))
            if index > len(self._ops):
                self._ops.append({
                    "size": int(event.get("download_size") or 0),
                    "done": False,
                    "name": event.get("name", ""),
                })
            self._current = index
            total = int(event.get("total") or len(self._ops))
            text = f"{VERBS[action]} {self._current} of {total}: {self._label(event.get('name', ''))}"
            self._set(key, ids, self._percent(0), text)

        elif kind == "progress":
            pct = int(event.get("percent") or 0)
            status = event.get("status") or ""
            if status.startswith("Downloading"):
                text = status
            else:
                text = VERBS[action] + "…"
            self._set(key, ids, self._percent(pct), text)

        elif kind == "operation-done":
            if 0 < self._current <= len(self._ops):
                self._ops[self._current - 1]["done"] = True

        elif kind in ("error", "failed"):
            self._job_error = event.get("message", "")

    def _label(self, name):
        """Resolve a raw ref name to a human-friendly label."""
        return self.installed.get(name, {}).get("name") or name.rsplit(".", 1)[-1]

    def _percent(self, pct):
        """Compute an overall percentage from per-operation data and current *pct*."""
        total = sum(o["size"] for o in self._ops)
        if not self._ops:
            return -1

        if total:
            done = sum(o["size"] for o in self._ops if o["done"])
            cur = 0
            if 0 < self._current <= len(self._ops):
                op = self._ops[self._current - 1]
                if not op["done"]:
                    cur = op["size"]
            return max(0, min(100, int((done + cur * pct / 100) * 100 / total)))
        else:
            return int(((self._current - 1) + pct / 100) * 100 / max(1, len(self._ops)))

    def _set(self, key, ids, pct, text):
        """Update progress for the job *key* and every app in *ids*."""
        self.progress[key] = (pct, text)
        for i in ids:
            self.progress[i] = (pct, text)
        self.changed.emit()

    def _finished(self, code, status):
        """Handle completion of the running helper process."""
        key, action, ids, parent = self._job
        message = self._job_error
        p = self._proc
        self._proc = None
        self._job = None
        p.deleteLater()

        # Clear busy / progress for this job's key and its app ids
        self.busy.pop(key, None)
        self.progress.pop(key, None)
        for i in ids:
            self.busy.pop(i, None)
            self.progress.pop(i, None)

        # For update-all also clear per-app markers that were not queued elsewhere
        if action == "update-all":
            for app_id in list(self.busy.keys()):
                if self.busy[app_id] == "update" and app_id != "*" and app_id not in [e[0] for e in self._queue]:
                    del self.busy[app_id]
                    self.progress.pop(app_id, None)

        self.refresh()
        self.changed.emit()

        # Show error dialog if the job failed (and was not cancelled)
        if code not in (0, 3) and not self._cancelled:
            name = "apps"
            if ids:
                name = self.installed.get(ids[0], {}).get("name", ids[0])
            msg = f"Could not {FAILED[action]} {name}.\n\n{message or 'Flatpak stopped with an error.'}"
            try:
                QMessageBox.warning(parent, "HoltOS Apps", msg)
            except RuntimeError:
                QMessageBox.warning(None, "HoltOS Apps", msg)

        self._next()
