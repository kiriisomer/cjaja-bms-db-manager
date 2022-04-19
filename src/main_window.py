from pathlib import Path
from PyQt5.QtCore import (
    QDate, QFile, Qt, QTextStream, QAbstractTableModel, QVariant, QModelIndex,
    QThread, pyqtSignal, pyqtSlot,
)
from PyQt5.QtGui import (
    QFont, QIcon, QKeySequence, QTextCharFormat,
    QTextCursor, QTextTableFormat, QStandardItemModel
)
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QGridLayout,
    QSpacerItem, QSizePolicy,
    QAction, QTreeWidget, QTreeWidgetItem, QSplitter, QTableView, QHeaderView,
    QDialog, QDockWidget, QPushButton, QLabel, QLineEdit,
    QFileDialog, QListWidget, QMainWindow, QMessageBox, QTextEdit,
    QProgressBar,
)
from db.service_code import (
    search_bms_list, search_folder_list, search_song_list,
    prepare_sqlite3_db,
    add_bms, add_folder, add_song,
    add_song_bms_relation,
)
from bms.parser import scan_bms_file_iter


class MainWindow(QMainWindow):
    def __init__(self, window_title:str = "Bms File Manager"):
        super().__init__()

        self.window_title = window_title
        self.setWindowTitle(self.window_title)
        self.resize(854, 480)

        self._init_menus()
        self._init_status_bar()
        self._init_widgets()

    def _init_menus(self):
        """init window menus"""
        self._menu_action_quit = QAction("&Quit", self, shortcut="Ctrl+Q",
                statusTip="Quit the application", triggered=self.close)
        self._menu_action_scan_dir = QAction("&Scan dir", self, shortcut="Ctrl+D",
                statusTip="Quit the application", triggered=self._action_scan_dir)
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self._menu_action_quit)
        self.fileMenu.addAction(self._menu_action_scan_dir)

        self._menu_action_about = QAction("&About", self,
                statusTip="Show the application's About box",
                triggered=self._about)

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self._menu_action_about)

    def _init_status_bar(self):
        self.statusBar().showMessage("Ready")

    def _init_widgets(self):
        """init main tree widget and grid widget"""
        splitter = QSplitter()
        r_frame = QWidget()
        space_1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        filter_dlg_btn = QPushButton("Filter")
        self.prev_btn = QPushButton("prev page")
        self.next_btn = QPushButton("next page")
        page_hint_label = QLabel(" 1 / 1 ")
        hl_1 = QHBoxLayout()
        hl_1.setObjectName("horizontal_layout_1")
        hl_1.addWidget(filter_dlg_btn)
        hl_1.addItem(space_1)
        hl_1.addWidget(self.prev_btn)
        hl_1.addWidget(self.next_btn)
        hl_1.addWidget(page_hint_label)
        self.tree = NameTree()
        self.table = QTableView()
        self.table_model = TableModel()
        self.table.setModel(self.table_model)
        vl_2 = QVBoxLayout()
        vl_2.setObjectName("verticalLayout_2")
        vl_2.addLayout(hl_1)
        vl_2.addWidget(self.table)
        r_frame.setLayout(vl_2)
        splitter.addWidget(self.tree)
        splitter.addWidget(r_frame)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        self.setCentralWidget(splitter)

        self.tree.clicked.connect(self.onTreeClicked)
        self.prev_btn.clicked.connect(self.onPrevBtnClicked)
        self.next_btn.clicked.connect(self.onNextBtnClicked)

    def _about(self):
        QMessageBox.about(self, f"About {self.window_title}",
            "Manage <b>Cjaja</b> bms database."
        )

    def _action_scan_dir(self):
        """scan bms files in directory recursively"""
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self,
                "Select Directory", "", options=options)
        if directory:
            print(f"{directory=}")
            """popup a dialog to show progress"""
            _ = ScanDirProgressDialog.scan_process_dialog(self, Path(directory))

    def open_file(self, file_path:Path):
        """open database file"""
        try:
            prepare_sqlite3_db(Path(file_path))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Open file {file_path} failed: {e}")
            self.close()

    def onTreeClicked(self, qmodelindex: QModelIndex):
        item = self.tree.currentItem()
        self.table_model.fetch_data(item.text(0))

    def onPrevBtnClicked(self):
        if self.table_model.query_params["page"] > 1:
            self.table_model.query_params["page"] -= 1
        else:
            self.table_model.query_params["page"] = 1

    def onNextBtnClicked(self):
        if self.table_model.query_params["page"] < self.table_model.query_params["total_page"]:
            self.table_model.query_params["page"] += 1


class FilterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        mainLayout = QGridLayout()

        label_01 = QLabel("title:")
        self.edit_01 = QLineEdit()
        label_01.setBuddy(self.edit_01)
        label_02 = QLabel("genre:")
        self.edit_02 = QLineEdit()
        label_02.setBuddy(self.edit_02)
        label_03 = QLabel("level:")
        self.edit_03 = QLineEdit()
        label_03.setBuddy(self.edit_03)

        mainLayout.addWidget(label_01, 0, 0, 1, 1)
        mainLayout.addWidget(self.edit_01, 0, 1, 1, 3)
        mainLayout.addWidget(label_02, 1, 0, 1, 1)
        mainLayout.addWidget(self.edit_02, 1, 1, 1, 3)
        mainLayout.addWidget(label_03, 2, 0, 1, 1)
        mainLayout.addWidget(self.edit_03, 2, 1, 1, 3)

        # mainLayout.setRowStretch(0, 1)
        # mainLayout.setRowStretch(1, 1)
        # mainLayout.setRowStretch(2, 1)
        # mainLayout.setColumnStretch(0, 1)
        # mainLayout.setColumnStretch(1, 1)
        self.setLayout(mainLayout)

        self.setWindowTitle("Styles")


class ScanDirProgressDialog(QDialog):
    def __init__(self, parent=None, scan_dir:Path=None):
        super().__init__(parent)

        self.info_label = QLabel("")
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)
        self.cancel_btn = QPushButton("Interrupt")
        self.cancel_btn.clicked.connect(self.on_cancel)

        layout = QGridLayout()
        layout.setColumnStretch(1, 1)

        layout.addWidget(self.info_label, 0, 0)
        layout.addWidget(self.progress_bar, 1, 0)
        layout.addWidget(self.cancel_btn, 2, 0)

        self.setLayout(layout)
        self.setWindowTitle("Scanning...")

        # init work thread
        self.work_thread = ScanDirThread(self, scan_dir)
        self.work_thread.register_signal(self.on_signal)
        self.work_thread.start()

    def on_signal(self, status:int, count:int, bms_file:Path):
        if status == 0:
            self.info_label.setText(f"{count} -- {bms_file}")
        else:
            # close this dialog
            self.close()

    def on_cancel(self):
        self.close()

    def closeEvent(self, event) -> None:
        if self.work_thread.isRunning():
            self.work_thread.interrupt()
        event.accept()

    @staticmethod
    def scan_process_dialog(parent, dir_:Path):
        """scan directory recursively"""
        if not dir_.exists():
            raise FileNotFoundError(f"{dir_} not found")
        if not dir_.is_dir():
            raise NotADirectoryError(f"{dir_} is not a directory")

        progress_dialog = ScanDirProgressDialog(parent, dir_)
        progress_dialog.exec_()

        return progress_dialog.result


class ScanDirThread(QThread):
    _signal = pyqtSignal(int, int, str)

    def __init__(self, parent, scan_dir:Path):
        super().__init__(parent)
        self.scan_dir = Path(scan_dir)
        self.interrupt = False

    def register_signal(self, slot):
        self._signal.connect(slot)

    def interrupt(self):
        self.interrupt = True

    def run(self):
        try:
            counter = 0
            for info in scan_bms_file_iter(self.scan_dir):
                counter += 1
                self._signal.emit(0, counter, str(info["file_path"]))
                bms_obj=add_bms(info["file_path"], info, on_error_raise_exc=False)
                song_obj=add_song(info["TITLE"], info["file_path"].parent, on_error_raise_exc=False)
                add_song_bms_relation(song_obj, bms_obj)
                if self.interrupt:
                    break

            self._signal.emit(1, 0, "")
            self.exit(0)
        except Exception as e:
            print(e)
            self._signal.emit(2, 0, "")
            self.exit(1)


class TableModel(QAbstractTableModel):
    """right table model"""
    def __init__(self):
        super().__init__()
        self.headers = []
        self.datas = []
        self.query_params = {
            "table_name": "",
            "page": 1,
            "pagesize": 100,
            "total_page": 0,
        }

    def rowCount(self, parent):
        """required by QAbstractTableModel"""
        return len(self.datas)
    def columnCount(self, parent):
        """required by QAbstractTableModel"""
        return len(self.headers)
    def data(self, index, role):
        """required by QAbstractTableModel"""
        if role != Qt.DisplayRole:
            return QVariant()
        return self.datas[index.row()][index.column()]
    def headerData(self, section, orientation, role):
        """required by QAbstractTableModel"""
        if role != Qt.DisplayRole or orientation != Qt.Horizontal:
            return QVariant()
        return self.headers[section]

    def fetch_data(self, table_name:str, filter_name=None, page=1, page_size=100):
        """"""
        print("fetch_data: ", table_name)
        self.beginResetModel()
        if table_name == "bms":
            self._query_bms()
        elif table_name == "song":
            self._query_song()
        elif table_name == "folder":
            self._query_folder()
        else:
            self.headers = []
            self.datas = []
        self.endResetModel()

    def _format_datas(self, data:list):
        """format dict type data to list type data"""
        result = []
        for item in data:
            result.append([item[key] for key in self.headers])
        return result

    def _query_bms(self):
        """"""
        self.headers = [
            "id", "file_path", "PLAYER", "TITLE", "ARTIST", "GENRE", "PLAYLEVEL",
            "RANK", "TOTAL", "DIFFICULTY", "BPM", "PREVIEW", "MIN_BPM", "MAX_BPM",
        ]
        result = search_bms_list(
            page=self.query_params["page"], page_size=self.query_params["pagesize"])

        self.query_params["total_page"] = result["total"] // self.query_params["pagesize"] + 1
        self.datas = self._format_datas(result["data"])

    def _query_song(self, filter_name=None, page=1, page_size=100):
        """"""
        self.headers = ["id", "name", "dir_path"]
        result = search_song_list(
            page=self.query_params["page"], page_size=self.query_params["pagesize"])

        self.query_params["total_page"] = result["total"] // self.query_params["pagesize"] + 1
        self.datas = self._format_datas(result["data"])

    def _query_folder(self, filter_name=None, page=1, page_size=100):
        """"""
        self.headers = ["id", "name", "desc", "info"]
        result = search_folder_list(
            page=self.query_params["page"], page_size=self.query_params["pagesize"])

        self.query_params["total_page"] = result["total"] // self.query_params["pagesize"] + 1
        self.datas = self._format_datas(result["data"])


class NameTree(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setHeaderLabels(("Setting", ))
        self.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.init_tree()

    def init_tree(self):
        """init tree items"""
        self.clear()
        self.createItem("bms", None, 0)
        self.createItem("song", None, 1)
        self.createItem("folder", None, 2)

    def createItem(self, text, parent, index):
        after = None
        if index != 0:
            after = self.childAt(parent, index - 1)

        if parent is not None:
            item = QTreeWidgetItem(parent, after)
        else:
            item = QTreeWidgetItem(self, after)

        item.setText(0, text)
        return item

    def childAt(self, parent, index):
        if parent is not None:
            return parent.child(index)
        else:
            return self.topLevelItem(index)
