# main.py

import sys
import os
from PyQt5.QtWidgets import QApplication
from douyin.gui import MainWindow
import subprocess

sys.path.append(os.path.join(os.path.dirname(__file__), 'douyin'))
from update_config import main as update_config_main


def start_uvicorn():
    subprocess.Popen(['python', 'start.py'])

def main():
    update_config_main()
    start_uvicorn()
    
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
