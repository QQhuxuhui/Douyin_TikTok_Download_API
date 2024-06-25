import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QFrame, QInputDialog, QMessageBox, QTextEdit, QLabel
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtCore import QUrl, Qt,QThreadPool
from PyQt5.QtWebEngineCore import QWebEngineCookieStore

import douyin.service as service
from douyin.worker_thread import Worker, WorkerSignals

class InputDialog(QInputDialog):
    def __init__(self, title, label_text, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setLabelText(label_text)

class LogTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.append("日志显示区域\n这里可以显示日志或其他文本内容。")

    def append_log(self, text):
        self.append(text)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("抖音数据")
        self.setGeometry(100, 100, 1500, 1000)

        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Main layout
        main_layout = QHBoxLayout(main_widget)

        # Left layout
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Web view frame
        web_frame = QFrame()
        web_frame.setFrameShape(QFrame.Box)
        web_layout = QVBoxLayout(web_frame)
        self.web_view = QWebEngineView()
        web_layout.addWidget(self.web_view)
        self.web_view.setUrl(QUrl("https://www.douyin.com/discover"))

        # Input and buttons layout
        input_buttons_widget = QWidget()
        input_buttons_layout = QVBoxLayout(input_buttons_widget)

        # self.get_cookies_button = QPushButton("更新登录信息（扫码登录成功后点击）")
        # self.get_cookies_button.clicked.connect(self.get_cookies)
        # input_buttons_layout.addWidget(self.get_cookies_button)
        divider = QLabel("\n已开放功能区域\n")
        divider.setAlignment(Qt.AlignCenter)
        divider.setStyleSheet("font-size: 14px; font-weight: bold;")
        input_buttons_layout.addWidget(divider)
        
        # Open functionality buttons
        self.open_button = QPushButton("采集作品评论数据")
        self.open_button.clicked.connect(self.show_collect_comments_dialog)
        input_buttons_layout.addWidget(self.open_button)

        # Divider line
        divider = QLabel("\n未开放功能区域\n")
        divider.setAlignment(Qt.AlignCenter)
        divider.setStyleSheet("font-size: 14px; font-weight: bold;")
        input_buttons_layout.addWidget(divider)

        # Button 1: 批量下载账号作品
        self.button1 = QPushButton("批量下载账号作品")
        self.button1.clicked.connect(self.no_function)

        # Button 2: 批量下载链接作品
        self.button2 = QPushButton("批量下载链接作品")
        self.button2.clicked.connect(self.no_function)

        # Button 3: 采集作品评论数据
        self.button3 = QPushButton("获取用户喜欢作品")
        self.button3.clicked.connect(self.no_function)

        # Button 4: 获取用户收藏作品
        self.button4 = QPushButton("获取用户收藏作品")
        self.button4.clicked.connect(self.no_function)

        # Button 5: 获取用户合辑作品
        self.button5 = QPushButton("获取用户合辑作品")
        self.button5.clicked.connect(self.no_function)

        # Button 6: 获取用户直播流数据
        self.button6 = QPushButton("获取用户直播流数据")
        self.button6.clicked.connect(self.no_function)

        # Button 6: 获取直播间送礼用户排行榜
        self.button7 = QPushButton("获取直播间送礼用户排行榜")
        self.button7.clicked.connect(self.no_function)

        self.button8 = QPushButton("获取直播间商品信息")
        self.button8.clicked.connect(self.no_function)

        input_buttons_layout.addWidget(self.button1)
        input_buttons_layout.addWidget(self.button2)
        input_buttons_layout.addWidget(self.button3)
        input_buttons_layout.addWidget(self.button4)
        input_buttons_layout.addWidget(self.button5)
        input_buttons_layout.addWidget(self.button6)
        input_buttons_layout.addWidget(self.button7)
        input_buttons_layout.addWidget(self.button8)

        # Adding to left layout
        left_layout.addWidget(web_frame, 7)
        left_layout.addWidget(input_buttons_widget, 3)

        # Right layout
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Title label for extracting works information
        title_label = QLabel("提取作品信息")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")

        # Table 1: 文章信息表格
        self.table1 = QTableWidget(0, 8)  # 5行8列
        self.table1.setHorizontalHeaderLabels(["发布时间", "评论ID", "用户ID", "用户昵称", "地点", "评论内容", "评论点赞数量", "评论回复数量"])

        self.log_text = LogTextEdit()

        # Adding to right layout
        right_layout.addWidget(title_label)
        right_layout.addWidget(self.table1)
        self.export_button = QPushButton("导出表格数据")
        self.export_button.clicked.connect(lambda: service.export_table_to_csv(self, self.log_text, self.table1))
        right_layout.addWidget(self.export_button)
        right_layout.addWidget(self.log_text)

        # Adding to main layout
        main_layout.addWidget(left_widget, 6)
        main_layout.addWidget(right_widget, 4)

        # Store cookies
        self.cookies = []
        profile = QWebEngineProfile.defaultProfile()
        profile.cookieStore().cookieAdded.connect(self.on_cookie_added)

    def on_cookie_added(self, cookie):
        cookie_name = cookie.name().data().decode('utf-8')
        cookie_value = cookie.value().data().decode('utf-8')
        new_cookie = (cookie_name, cookie_value)
        if new_cookie not in self.cookies:
            self.cookies.append(new_cookie)
            self.update_cookies_in_service()

    def update_cookies_in_service(self):
        cookie_list = [f"{name}={value}" for name, value in self.cookies]
        cookie_str = "; ".join(cookie_list)
        service.set_cookie(cookie_str)

    def get_cookies(self):
        try:
            if not self.cookies:
                self.log_text.append_log("未能获取任何 cookie.")
                return
            self.update_cookies_in_service()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"获取 Cookie 时发生错误: {str(e)}")

    def show_account_works_dialog(self):
        try:
            dialog = InputDialog("批量下载账号作品", "请输入账号链接:", self)
            if dialog.exec_():
                account_link = dialog.textValue()
                self.log_text.append_log(f"开始批量下载账号作品，账号链接为: {account_link}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"批量下载账号作品时发生错误: {str(e)}")

    def show_bulk_download_dialog(self):
        try:
            dialog = InputDialog("批量下载链接作品", "请输入链接作品内容:", self)
            dialog.setTextValue("多行文本\n内容")
            if dialog.exec_():
                bulk_content = dialog.textValue()
                self.log_text.append_log(f"开始批量下载链接作品，内容为:\n{bulk_content}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"批量下载链接作品时发生错误: {str(e)}")

    def show_collect_comments_dialog(self):
        try:
            dialog = InputDialog("采集作品评论数据", "请输入账号链接:", self)
            if dialog.exec_():
                account_link = dialog.textValue()

                # Create a worker instance
                worker = Worker(account_link, self.log_text)
                
                # Connect signals from the worker
                worker.signals.result.connect(self.on_worker_result)
                worker.signals.finished.connect(self.on_worker_finished)
                worker.signals.error.connect(self.on_worker_error)
                
                # Execute the worker in the thread pool
                QThreadPool.globalInstance().start(worker)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"采集作品评论数据时发生错误: {str(e)}")

    def on_worker_result(self, data):
        # Handle the received data here
        service.update_comments_table(self.table1, data)

    def on_worker_finished(self):
        QMessageBox.information(self, "提示", "评论数据采集完成")

    def on_worker_error(self, error_message):
        QMessageBox.critical(self, "错误", f"采集作品评论数据时发生错误: {error_message}")

    def show_collect_search_results_dialog(self):
        try:
            dialog = InputDialog("采集搜索结果数据", "请输入筛选条件:", self)
            if dialog.exec_():
                search_criteria = dialog.textValue()
                self.log_text.append_log(f"开始采集搜索结果数据，筛选条件为: {search_criteria}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"采集搜索结果数据时发生错误: {str(e)}")

    def no_function(self):
        try:
            QMessageBox.information(self, "采集抖音热榜数据", "尚未开放")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"采集抖音热榜数据时发生错误: {str(e)}")

    def show_collect_favorites_dialog(self):
        try:
            dialog = InputDialog("批量下载收藏作品", "请输入账号链接:", self)
            if dialog.exec_():
                account_link = dialog.textValue()
                self.log_text.append_log(f"开始批量下载收藏作品，账号链接为: {account_link}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"批量下载收藏作品时发生错误: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
