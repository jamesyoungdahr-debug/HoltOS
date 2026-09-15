"""Fix updates, from HoltOS Updates > Settings: runs holtos-update-repair
through pkexec and shows each step as it happens. The dialog cannot be
closed while the repair runs, so nobody walks away from a half-finished one.
"""
from PySide6.QtCore import QProcess
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QPlainTextEdit, QVBoxLayout

REPAIR = "/usr/local/bin/holtos-update-repair"


class RepairDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Fix updates")
        self.resize(640, 420)
        layout = QVBoxLayout(self)

        intro = QLabel(
            "HoltOS clears a stuck update, removes half-finished downloads, repairs the "
            "package keys, picks fast mirrors and refreshes everything. Your apps and "
            "files are not touched."
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFontDatabase.systemFont(QFontDatabase.FixedFont))
        layout.addWidget(self.output, 1)

        self.result = QLabel("Working...")
        self.result.setWordWrap(True)
        layout.addWidget(self.result)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Close)
        self.buttons.rejected.connect(self.reject)
        self.buttons.setEnabled(False)
        layout.addWidget(self.buttons)

        self.proc = QProcess(self)
        self.proc.setProcessChannelMode(QProcess.MergedChannels)
        self.proc.readyReadStandardOutput.connect(self.read)
        self.proc.finished.connect(self.finished)
        self.proc.start("pkexec", [REPAIR])

    def read(self):
        text = bytes(self.proc.readAllStandardOutput()).decode(errors="replace")
        for line in text.splitlines():
            self.output.appendPlainText(line[4:] if line.startswith("==> ") else line)

    def finished(self, code, _status):
        self.read()
        self.buttons.setEnabled(True)
        if code == 0:
            self.result.setText("Done. Updates should work again.")
        elif code in (126, 127):
            self.reject()
        else:
            self.result.setText(
                "Some steps did not work (see above). If updates still fail, create a "
                "support bundle from the HoltOS tray menu."
            )

    def reject(self):
        # Escape and the window's close button end up here: wait for the repair.
        if self.proc.state() != QProcess.NotRunning:
            return
        super().reject()
