# main.py

import sys
import os
from PyQt5.QtWidgets import QApplication
from douyin.gui import MainWindow
import subprocess

# 添加当前文件的目录到 sys.path 中，以便正确导入自定义模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from douyin.config import main as update_config_main  # 修改导入语句


def start_uvicorn():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    start_path = os.path.abspath(os.path.join(script_dir, '../'))
    subprocess.Popen(['python', start_path + '/' +  'start.py'])

def main():
    update_config_main()
    
    # 启动API服务
    start_uvicorn()
    
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
