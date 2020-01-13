from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QListWidgetItem, QFormLayout, QVBoxLayout, QLabel
from PyQt5 import QtGui
import sys
import json
import os


class Map(QWidget):
    def __init__(self, text):
        super().__init__()
        uic.loadUi('item.ui', self)

        self.setLayout(self.gridLayout)

        self.label.setText(text)
    
    def mousePressEvent(self, event):
        self.label.setStyleSheet("""
            background-color: rgb(213, 224, 252); 
            padding:5px;
            border-radius: 8px;
        """)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        
        self.scrollLayout = QFormLayout()
        self.scrollWidget = QWidget()
        self.scrollWidget.setLayout(self.scrollLayout)

        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.scrollWidget)

        self.add_btn.clicked.connect(self.add_part)

        for filename in os.listdir("maps"):
            self.add_part(Map(filename))
        # self.add_part()

    def add_part(self, widget):
        self.scrollLayout.addWidget(widget)
    


class Settings(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main_window.ui', self)
        self.exit_btn.clicked.connect(self.exit_event)
        self.start_btn.clicked.connect(self.start_event)

        self.all_cfg = open("list.json", "r")
        self.cfg = open("cfg.json", "r")

        self.add_items()

    def exit_event(self):
        sys.exit()

    def start_event(self):
        cfg = open("cfg.json", "r")
        data = json.load(cfg)
        cfg.close()

        data['fps'] = self.fps.currentText()

        print(data)
        cfg_write = open("cfg.json", "w")
        json.dump(data, cfg_write, indent=4, sort_keys=True)
        cfg_write.close()
        self.all_cfg.close()

    def add_items(self):
        data = json.load(self.all_cfg)
        cfg = json.load(self.cfg)
        print(data)

        try:
            fps = data['fps']
            fps.remove(cfg['fps'])
            self.fps.addItem(cfg['fps'])
            self.fps.addItems(fps)
            
        except ValueError:
            self.fps.addItems(data['fps'])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())