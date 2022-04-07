import sys

from PyQt5.QtWidgets import QApplication

from welcome_dialogue import SelectDBDialog
from main_window import MainWindow


def main():
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

