import os
import logging
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from tkinter import ttk, messagebox
import gui.video.duanju.service as service



class TextHandler(logging.Handler):
    """Class to handle logging messages and display them in the Tkinter Text widget."""
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.insert(tk.END, msg + '\n')
        self.text_widget.see(tk.END)

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

# 获取当前工作目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 构建 ffmpeg.exe 的路径
ffmpeg_path = os.path.join(current_dir, 'ffmpeg.exe')

class VideoProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("悟空")
        self.create_widgets()
        self.setup_logging()
        self.current_process = None

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 检查日期并弹出提示框
        # self.check_and_show_date_alert()

    def create_widgets(self):
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.start_button = ttk.Button(self.frame, text="开始", command=self.start_processing)
        self.start_button.pack(pady=10)

        self.progress_bar = ttk.Progressbar(self.frame, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(pady=5, fill=tk.X, expand=True)

        self.log_text = tk.Text(self.frame, height=15, wrap='word')
        self.log_text.pack(pady=5, fill=tk.BOTH, expand=True)

    def setup_logging(self):
        text_handler = TextHandler(self.log_text)
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        text_handler.setFormatter(formatter)
        logging.getLogger().addHandler(text_handler)

    def start_processing(self):
        folder_path = "."
        if folder_path:
            self.process_videos(folder_path)

    def update_progress(self, value):
        self.progress_bar['value'] = value
        self.root.update_idletasks()

    def process_videos(self, folder_path):
        process_videos_in_folder(folder_path, self.update_progress, self.set_current_process)

    def set_current_process(self, process):
        self.current_process = process

    def on_closing(self):
        if self.current_process is not None:
            self.current_process.terminate()
        self.root.destroy()
        
    # 日期过滤    
    def check_and_show_date_alert(self):
        current_date = datetime.now()
        check_date = datetime(2024, 6, 13)
        if current_date > check_date + timedelta(days=7):
            messagebox.showinfo("软件过期提醒", "悟空已过期，无法使用")
            self.on_closing()



def process_video(input_video, progress_callback, file_index, total_files, set_process_callback):
    try:
        output_video = input_video.replace(".mp4", "_out.mp4")
        service.duanju(input_video, output_video, progress_callback, file_index, total_files, set_process_callback)
    except Exception as e:
        logging.error(f"Error processing video: {input_video} - {e}")

def process_videos_in_folder(folder_path, progress_callback, set_process_callback):
    absolute_folder_path = os.path.abspath(folder_path)

    files_list = []
    for root, dirs, files in os.walk(absolute_folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if file_path.endswith(".mp4"):
                files_list.append(file_path)

    logging.info(f"需要处理的文件列表: {files_list}")

    total_files = len(files_list)
    for idx, file_path in enumerate(files_list):
        logging.info(f"开始处理第 {idx + 1} 个文件，总计：{total_files}，文件路径：{file_path}")
        process_video(file_path, progress_callback, idx + 1, total_files, set_process_callback)
        progress = int(((idx + 1) / total_files) * 100)
        progress_callback(progress)

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoProcessorApp(root)
    root.mainloop()
