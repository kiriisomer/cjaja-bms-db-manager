from pathlib import Path
from PyQt5.QtCore import (
    QDate, QFile, Qt, QTextStream, QAbstractTableModel, QVariant, QModelIndex
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
    QFileDialog, QListWidget, QMainWindow, QMessageBox, QTextEdit
)


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

        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self._menu_action_quit)

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

    def open_file(self, file_path:Path):
        """open database file"""

    def onTreeClicked(self, qmodelindex: QModelIndex):
        item = self.tree.currentItem()
        self.table_model.fetch_data(item.text(0))

    def onPrevBtnClicked(self):
        if self.table_model.query_params["page"] > 1:
            self.table_model.query_params["page"] -= 1
        else:
            self.table_model.query_params["page"] = 1

    def onNextBtnClicked(self):
        pass


class FilterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        mainLayout = QGridLayout()

        label_01 = QLabel("name:")
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


headers = ["Scientist name", "Birthdate", "Contribution"]
rows = [("Newton", "1643-01-04", "Classical mechanics"),
        ("Einstein", "1879-03-14", "Relativity"),
        ("Darwin", "1809-02-12", "Evolution")]


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
            "name": None,
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
        if table_name == "song":
            self._query_bms_file()
        elif table_name == "bms":
            self._query_song()
        elif table_name == "folder":
            self._query_folder()
        else:
            self.headers = []
            self.datas = []
        self.endResetModel()

    def _query_bms_file(self):
        """"""
        self.headers = ["name", "song_info_1", "song_info_2", "song_info_3"]
        self.datas = [("001", "001_1", "001_2", "001_3")]

    def _query_song(self, filter_name=None, page=1, page_size=100):
        """"""
        self.headers = ["name", "bms_info_1", "bms_info_2"]
        self.datas = rows

    def _query_folder(self, filter_name=None, page=1, page_size=100):
        """"""
        self.headers = ["name", "folder_info_1", "folder_info_2"]
        self.datas = []


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
