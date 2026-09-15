"""Background jobs for HoltOS Apps: run blocking calls (network, flatpak) in Qt's thread pool and hand the result back on the GUI thread."""

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal
from PySide6.QtGui import QPixmap
import flathub


class _Relay(QObject):
    done = Signal(object)
    failed = Signal(str)

    def __init__(self, on_done, on_error):
        super().__init__()
        self._on_done = on_done
        self._on_error = on_error
        self.done.connect(self._done)
        self.failed.connect(self._failed)

    def _done(self, result):
        try:
            self._on_done(result)
        except RuntimeError:
            pass  # the widget was closed
        finally:
            _LIVE.discard(self)

    def _failed(self, message):
        try:
            if self._on_error:
                self._on_error(message)
        except RuntimeError:
            pass  # the widget was closed
        finally:
            _LIVE.discard(self)


_LIVE = set()  # keeps relays alive until their job finishes


class _Job(QRunnable):
    def __init__(self, fn, args, relay):
        super().__init__()
        self._fn = fn
        self._args = args
        self._relay = relay

    def run(self):
        try:
            result = self._fn(*self._args)
        except Exception as error:
            self._emit(self._relay.failed, str(error) or error.__class__.__name__)
            return
        self._emit(self._relay.done, result)

    @staticmethod
    def _emit(signal, value):
        try:
            signal.emit(value)
        except RuntimeError:
            pass  # the window closed while the job ran


def run_async(fn, *args, on_done, on_error=None):
    relay = _Relay(on_done, on_error)
    _LIVE.add(relay)
    QThreadPool.globalInstance().start(_Job(fn, args, relay))


def load_pixmap(url, on_done):
    def _build(path):
        pixmap = QPixmap(path) if path else None
        if pixmap is not None and pixmap.isNull():
            pixmap = None
        on_done(pixmap)

    run_async(flathub.fetch_media, url, on_done=_build)
