
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QGridLayout,
    QDialog, QFileDialog,
    QLabel, QPushButton,
    QMessageBox,
)


class SelectDBDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        label_1 = QLabel("Create new Cjaja bms Database")
        self.new_button = QPushButton("create new")
        label_2 = QLabel("Open Exist Cjaja bms Database")
        self.open_button = QPushButton("open exist")

        self.new_button.clicked.connect(self.new)
        self.open_button.clicked.connect(self.open)

        layout = QGridLayout()
        layout.setColumnStretch(1, 1)
        layout.addWidget(label_1, 0, 0)
        layout.addWidget(self.new_button, 1, 0)
        layout.addWidget(label_2, 2, 0)
        layout.addWidget(self.open_button, 3, 0)
        self.setLayout(layout)

        self.setWindowTitle("Welcome")

        self.select_file = None

    def new(self):
        # open directory for storage
        options = options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self,
                "Select Directory", "", options=options)
        if directory:
            # QMessageBox.information(self, "test", str(directory))
            self.select_file = Path(directory) / "data.sqlite3"
            self.accept()

    def open(self):
        options = QFileDialog.Options()
        file, _ = QFileDialog.getOpenFileName(self,
                "Open DB File", "",
                "DB Files (*.sqlite3);;All Files (*)", options=options)
        print("======  ", _)
        if file:
            # QMessageBox.information(self, "test", str(file))
            self.select_file = Path(file)
            self.accept()

    @staticmethod
    def welcome_dialog():
        """show welcome dialog"""
        dialog = SelectDBDialog()
        _ = dialog.exec()
        data = dialog.select_file

        return data


if __name__ == '__main__':
    # for test
    import sys
    app = QApplication(sys.argv)
    file_path = SelectDBDialog.welcome_dialog()
    print("result: ", file_path)
    # sys.exit(app.exec_())
