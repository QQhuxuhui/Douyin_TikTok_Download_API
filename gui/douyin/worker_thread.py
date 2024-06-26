from PyQt5.QtCore import QObject, pyqtSignal, QRunnable
import asyncio
import gui.douyin.service as service
import json

class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    result = pyqtSignal(str)  # Signal with a string object

class Worker(QRunnable):
    def __init__(self, account_link, log_text):
        super().__init__()
        self.signals = WorkerSignals()
        self.account_link = account_link
        self.log_text = log_text

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            self.log_text.append_log(f"开始采集作品评论数据，账号链接为: {self.account_link}")
            coroutine = service.fetch_video_comments(self.log_text, self.account_link)
            loop.run_until_complete(self.fetch_all_comments(coroutine))
            self.signals.finished.emit()
        except Exception as e:
            self.signals.error.emit(str(e))
        finally:
            loop.close()

    async def fetch_all_comments(self, coroutine):
        async for data in coroutine:
            self.signals.result.emit(data)
