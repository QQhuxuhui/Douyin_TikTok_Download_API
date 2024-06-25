from PyQt5.QtCore import QObject, pyqtSignal, QRunnable
import douyin.service as service

class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    result = pyqtSignal(object)  # Signal with a data object

class Worker(QRunnable):
    def __init__(self, account_link, log_text):
        super().__init__()
        self.signals = WorkerSignals()
        self.account_link = account_link
        self.log_text = log_text

    def run(self):
        try:
            self.log_text.append_log(f"开始采集作品评论数据，账号链接为: {self.account_link}")
            data = service.fetch_video_comments(self.log_text, self.account_link)
            # Emit a signal to indicate the task is finished
            self.signals.result.emit(data)
            self.signals.finished.emit()  
        except Exception as e:
            # Emit an error signal if an exception occurs
            self.signals.error.emit(str(e))
