import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QFrame, QInputDialog, QMessageBox, QTextEdit, QLabel
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineCore import QWebEngineCookieStore

import douyin.service as service

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

        self.setWindowTitle("PyQt Layout Example")
        self.setGeometry(100, 100, 1200, 800)

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
        self.web_view.setUrl(QUrl("https://www.douyin.com/"))

        # Input and buttons layout
        input_buttons_widget = QWidget()
        input_buttons_layout = QVBoxLayout(input_buttons_widget)

        # Button 1: 批量下载账号作品
        self.button1 = QPushButton("批量下载账号作品")
        self.button1.clicked.connect(self.show_account_works_dialog)

        # Button 2: 批量下载链接作品
        self.button2 = QPushButton("批量下载链接作品")
        self.button2.clicked.connect(self.show_bulk_download_dialog)

        # Button 3: 采集作品评论数据
        self.button3 = QPushButton("采集作品评论数据")
        self.button3.clicked.connect(self.show_collect_comments_dialog)

        # Button 4: 采集搜索结果数据
        self.button4 = QPushButton("采集搜索结果数据")
        self.button4.clicked.connect(self.show_collect_search_results_dialog)

        # Button 5: 采集抖音热榜数据
        self.button5 = QPushButton("采集抖音热榜数据")
        self.button5.clicked.connect(self.show_hot_list_dialog)

        # Button 6: 批量下载收藏作品
        self.button6 = QPushButton("批量下载收藏作品")
        self.button6.clicked.connect(self.show_collect_favorites_dialog)

        input_buttons_layout.addWidget(self.button1)
        input_buttons_layout.addWidget(self.button2)
        input_buttons_layout.addWidget(self.button3)
        input_buttons_layout.addWidget(self.button4)
        input_buttons_layout.addWidget(self.button5)
        input_buttons_layout.addWidget(self.button6)
        
        self.get_cookies_button = QPushButton("获取 Cookies")
        self.get_cookies_button.clicked.connect(self.get_cookies)
        input_buttons_layout.addWidget(self.get_cookies_button)

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
        self.table1 = QTableWidget(5, 7)  # 5行7列
        self.table1.setHorizontalHeaderLabels(["发布时间","评论ID","用户ID", "用户昵称", "地点", "评论内容", "评论点赞数量", "评论回复数量"])
        for row in range(5):
            for col in range(7):
                self.table1.setItem(row, col, QTableWidgetItem(f"Item {row+1}-{col+1}"))

        # Table 2: 评论信息表格
        # self.table2 = QTableWidget(10, 9)  # 10行9列
        # self.table2.setHorizontalHeaderLabels(["序号", "昵称", "抖音号", "地址", "评论时间", "评论内容", "点赞数量", "不喜欢数量", "转发数量"])
        # for row in range(10):
        #     for col in range(9):
        #         self.table2.setItem(row, col, QTableWidgetItem(f"Item {row+1}-{col+1}"))

        # Log text edit
        self.log_text = LogTextEdit()

        # Adding to right layout
        right_layout.addWidget(title_label)
        right_layout.addWidget(self.table1)
        # right_layout.addWidget(self.table2)
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
        self.cookies.append((cookie_name, cookie_value))

    def get_cookies(self):
        if not self.cookies:
            self.log_text.append_log("未能获取任何 cookie.")
            return
        cookie_list = [f"{name}={value}" for name, value in self.cookies]
        cookie_str = "; ".join(cookie_list)
        self.log_text.append_log(f"获取的 cookie: {cookie_str}")
        service.set_cookie(cookie_str)

    def show_account_works_dialog(self):
        dialog = InputDialog("批量下载账号作品", "请输入账号链接:", self)
        if dialog.exec_():
            account_link = dialog.textValue()
            self.log_text.append_log(f"开始批量下载账号作品，账号链接为: {account_link}")

    def show_bulk_download_dialog(self):
        dialog = InputDialog("批量下载链接作品", "请输入链接作品内容:", self)
        dialog.setTextValue("多行文本\n内容")
        if dialog.exec_():
            bulk_content = dialog.textValue()
            self.log_text.append_log(f"开始批量下载链接作品，内容为:\n{bulk_content}")

    def show_collect_comments_dialog(self):
        dialog = InputDialog("采集作品评论数据", "请输入账号链接:", self)
        if dialog.exec_():
            account_link = dialog.textValue()
            self.log_text.append_log(f"开始采集作品评论数据，账号链接为: {account_link}")
            data = service.fetch_video_comments(account_link)
            service.update_comments_table(self.table1,data);

    def show_collect_search_results_dialog(self):
        dialog = InputDialog("采集搜索结果数据", "请输入筛选条件:", self)
        if dialog.exec_():
            search_criteria = dialog.textValue()
            self.log_text.append_log(f"开始采集搜索结果数据，筛选条件为: {search_criteria}")

    def show_hot_list_dialog(self):
        QMessageBox.information(self, "采集抖音热榜数据", "尚未开放")

    def show_collect_favorites_dialog(self):
        dialog = InputDialog("批量下载收藏作品", "请输入账号链接:", self)
        if dialog.exec_():
            account_link = dialog.textValue()
            self.log_text.append_log(f"开始批量下载收藏作品，账号链接为: {account_link}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
