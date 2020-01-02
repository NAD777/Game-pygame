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

        self.all_cfg = open("list.json", "r")
        self.cfg = open("cfg.json", "r")

        self.add_items()

    def exit_event(self):
        sys.exit()

    def start_event(self):
        cfg = open("cfg.json", "r")
        data = json.load(cfg)
        cfg.close()
        
        data['resolution'] = self.resolutions.currentText().replace(" × ", ";")
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
        items = data["resolutions"]
        try:
            items.remove(cfg["resolution"])
        except ValueError:
            pass
        items = map(lambda x: x.replace(";", " × "), items)
            
        self.resolutions.addItem(cfg["resolution"].replace(";", " × "))
        self.resolutions.addItems(items)

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