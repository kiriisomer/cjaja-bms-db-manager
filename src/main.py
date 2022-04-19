import sys

from PyQt5.QtWidgets import QApplication

from welcome_dialogue import SelectDBDialog
from main_window import MainWindow


def check_python_ver():
    """I use python3.8, so I need to check it."""
    import platform
    major, minor, _ = [int(x) for x in platform.python_version_tuple()]
    if any((major!=3, minor<8)):
        print("Need Python Version 3.8 or above", file=sys.stderr)
        sys.exit(1)


def main():
    check_python_ver()
    # can open file in command line.
    file_path = None
    app = QApplication(sys.argv)
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = SelectDBDialog.welcome_dialog()

    if file_path:
        mainWin = MainWindow()
        mainWin.open_file(file_path)
        mainWin.show()
        sys.exit(app.exec_())

main()

