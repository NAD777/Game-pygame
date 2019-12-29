from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
import json


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main_window.ui', self)
        self.exit_btn.clicked.connect(self.exit_event)
        self.start_btn.clicked.connect(self.start_event)
        self.add_items()

    def exit_event(self):
        sys.exit()

    def start_event(self):
        cfg_read = open("cfg.json", "r")
        data = json.load(cfg_read)
        cfg_read.close()
        
        data['resolution'] = self.resolutions.currentText().replace(" × ", ";")
        
        cfg_write = open("cfg.json", "w")
        json.dump(data, cfg_write, indent=4, sort_keys=True)
        cfg_write.close()

    def add_items(self):
        with open("list.json", "r") as read_file:
            data = json.load(read_file)
            print(data)
            items = map(lambda x: x.replace(";", " × "), data["resolutions"])
            self.resolutions.addItems(items)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())