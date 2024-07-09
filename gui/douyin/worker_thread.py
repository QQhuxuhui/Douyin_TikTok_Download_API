from PyQt5.QtCore import QObject, pyqtSignal, QRunnable
import asyncio
import gui.douyin.service as service
import json

class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    result = pyqtSignal(str)  # Signal with a string object
    result2 = pyqtSignal(int)  # 第二种类型的结果信号，例如
    

class Worker(QRunnable):
    def __init__(self, coroutine_func, account_link, log_text):
        super().__init__()
        self.signals = WorkerSignals()
        self.coroutine_func = coroutine_func
        self.account_link = account_link
        self.log_text = log_text

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            self.log_text.append_log(f"开始处理链接: {self.account_link}")
            coroutine = service.coroutine_func(self.log_text, self.account_link)
            loop.run_until_complete(self.fetch_all_comments(coroutine))
            self.signals.finished.emit()
        except Exception as e:
            self.signals.error.emit(str(e))
        finally:
            loop.close()

    async def fetch_all_comments(self, coroutine):
        async for data in coroutine:
            # 根据数据类型发送对应的结果信号
            if isinstance(data, str):
                self.signals.result1.emit(data)  # 发送第一种类型的结果信号
            elif isinstance(data, int):
                self.signals.result2.emit(data)  # 发送第二种类型的结果信号
