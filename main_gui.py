# main.py

import sys
from PyQt5.QtWidgets import QApplication
from gui.douyin.gui import MainWindow


def start_gui():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()   
    sys.exit(app.exec_()) 
    

def start():
    start_gui()

   
if __name__ == "__main__":
    start()
