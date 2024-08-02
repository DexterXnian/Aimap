import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QTextEdit
from PyQt5.QtGui import QPixmap
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mappin import AImapping
import os

class AImappingApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # 界面布局
        self.setWindowTitle('AImapping Application')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        self.map_label = QLabel('Map will be displayed here')
        layout.addWidget(self.map_label)

        self.description_edit = QTextEdit('Enter description here')
        layout.addWidget(self.description_edit)

        self.load_button = QPushButton('Load Shapefiles')
        self.load_button.clicked.connect(self.load_shapefiles)
        layout.addWidget(self.load_button)

        self.generate_button = QPushButton('Generate Map')
        self.generate_button.clicked.connect(self.generate_map)
        layout.addWidget(self.generate_button)

        self.setLayout(layout)

    def load_shapefiles(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self, "Load Shapefiles", "", "Shapefiles (*.shp);;All Files (*)", options=options)
        if files:
            self.shapefiles = files

    def generate_map(self):
        description = self.description_edit.toPlainText()
        if hasattr(self, 'shapefiles'):
            map_name = 'Generated Map'
            aimapping = AImapping(map_name, description, *self.shapefiles)
            self.display_map('output.png')  # 假设 AImapping 类生成了一个 output.png 文件来保存生成的地图

    def display_map(self, map_path):
        pixmap = QPixmap(map_path)
        self.map_label.setPixmap(pixmap)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AImappingApp()
    ex.show()
    sys.exit(app.exec_())
