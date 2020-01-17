from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QListWidgetItem, QFormLayout, QVBoxLayout, QLabel
from PyQt5 import QtGui
import sys
import json
import os
from subprocess import Popen


class Map(QWidget):
    def __init__(self, text):
        super().__init__()
        uic.loadUi('item.ui', self)

        self.setLayout(self.gridLayout)
        self.level_name = text
        text = text[:-4]
        self.label.setText(text)
        
        self.start_btn.clicked.connect(self.game_start)
    
    def game_start(self):
        cfg = open("cfg.json", "r")
        data = json.load(cfg)
        Popen(["python", 'game.py', self.level_name, data['name']])


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.cur_layout = None
        self.open_levels()

        self.settings_btn.clicked.connect(self.open_settigns)
        # self.cup.clicked.connect(self.open_table)

        self.back_btn.hide()
    
    def open(self, cls):
        self.cur_layout = cls
        self.clearLayout(self.horizontalLayout)
        self.horizontalLayout.addWidget(self.cur_layout)

    def open_settigns(self):
        self.open(Settings(self))
    
    def open_table(self):
        self.open(Table(self))

    def open_levels(self):
        self.open(Levels(self))
    
    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
    
class List(QWidget):
    def __init__(self, parent):
        super().__init__()
        uic.loadUi('List.ui', self)

        self.setLayout(self.gridLayout)

        self.scrollLayout = QFormLayout()
        self.scrollWidget = QWidget()
        self.scrollWidget.setLayout(self.scrollLayout)

        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.scrollWidget)

        self.parent = parent

    def add_part(self, widget):
        self.scrollLayout.addWidget(widget)


class Levels(List):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent.settings_btn.show()
        # self.parent.cup.show()
        self.parent.back_btn.hide()
        for filename in sorted(os.listdir("data/maps")):
            self.add_part(Map(filename))


class Part_table(QWidget):
    def __init__(self, place):
        super().__init__()
        uic.loadUi('table_part.ui', self)
        color_bg = "rgb(213, 224, 252)"
        color_text = "rgb(0, 0, 0)"
        if place == 0:
            color_bg = "rgba(255, 77, 0, 0.7)"
            color_text = "rgb(0, 0, 0)"
        elif place == 1:
            color_bg = "rgba(255, 117, 24, 0.7)"
            color_text = "rgb(0, 0, 0)"
        elif place == 2:
            color_bg = "rgba(119, 221, 119, 0.7)"
            color_text = "rgb(0, 0, 0)"
        
        self.nickname.setStyleSheet(f"padding:5px;background-color: {color_bg};color: {color_text}")

        self.setLayout(self.gridLayout)


class Table(List):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent.settings_btn.hide()
        self.parent.cup.hide()
        self.parent.back_btn.show()
        self.parent.back_btn.clicked.connect(self.back)

        for place in range(5):
            self.add_part(Part_table(place))
    
    def back(self):
        self.parent.open_levels()


class Settings(QMainWindow):
    def __init__(self, parent):
        super().__init__()
        uic.loadUi('Settings.ui', self)

        self.all_cfg = open("list.json", "r")
        self.cfg = open("cfg.json", "r")

        self.parent = parent

        self.parent.settings_btn.hide()
        # self.parent.cup.hide()

        self.parent.back_btn.show()
        self.parent.back_btn.clicked.connect(self.set_event)

        self.add_items()

    def set_event(self):
        cfg = open("cfg.json", "r")
        data = json.load(cfg)
        cfg.close()

        data['fps'] = self.fps.currentText()
        data['name'] = self.lineEdit.text()

        print(data)
        cfg_write = open("cfg.json", "w")
        json.dump(data, cfg_write, indent=4, sort_keys=True)
        cfg_write.close()
        self.all_cfg.close()
        self.parent.open_levels()

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

        self.lineEdit.setText(cfg["name"])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())