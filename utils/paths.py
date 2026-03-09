import os
import sys


def resource_path(relative: str) -> str:
    """
    Абсолютный путь к ресурсу.
    Работает и в обычном запуске, и в PyInstaller --onefile.
    """
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS  # type: ignore[attr-defined]
        return os.path.join(base, relative)

    # project root = папка, где лежит main.py
    root = os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.join(root, relative)
