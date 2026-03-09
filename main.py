import sys
import os
import ctypes

os.environ["QT_OPENGL"] = "angle"
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = " ".join([
    "--ignore-gpu-blocklist",
    "--enable-gpu-rasterization",
    "--enable-zero-copy",
    "--disable-software-rasterizer",
])

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from ui.login_dialog import LoginDialog
from ui.main_window import MainWindow
from utils.paths import resource_path
from ui.theme import ThemeManager

def main():
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Termovizor.SCADA")
    except Exception:
        pass

    app = QApplication(sys.argv)
    theme = ThemeManager()
    theme.apply_to_app(app)

    icon = QIcon(resource_path("assets/icon.ico"))
    app.setWindowIcon(icon)

    login_dialog = LoginDialog()
    login_dialog.setWindowIcon(icon)

    if login_dialog.exec() != LoginDialog.DialogCode.Accepted:
        return 0

    win = MainWindow(
        login_dialog.api_client,
        login_dialog.selected_device_id,
        {},
        login_dialog.devices,
    )
    win.setWindowIcon(icon)
    win.showMaximized()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
