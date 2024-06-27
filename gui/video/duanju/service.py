
import subprocess
import logging
import re
from moviepy.editor import VideoFileClip


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_video_duration(video_file):
    try:
        clip = VideoFileClip(video_file)
        duration = clip.duration
        clip.close()
        return duration
    except Exception as e:
        logging.error(f"Error getting video duration: {e}")
        return None

def duanju(input_video, output_video, progress_callback, file_index, total_files, set_process_callback):
    ffmpeg_command = [
        "ffmpeg.exe",  # Adjust path as necessary
        "-i", input_video, 
        "-y",
        "-filter_complex", "[0:v]select='mod(n,20)'[outv];[0:a]atempo=1[aout];[outv]hue=s=1.01[outv_sat]",
        "-map", "[outv_sat]", "-map", "[aout]",
        "-ss", "0.1",
        "-c:v", "libx264", "-c:a", "aac", 
        "-strict", "experimental",
        output_video
    ]
    print(ffmpeg_command)
    process = subprocess.Popen(ffmpeg_command, stderr=subprocess.PIPE, universal_newlines=True, creationflags=subprocess.CREATE_NO_WINDOW)
    set_process_callback(process)

    total_duration = get_video_duration(input_video)

    progress_regex = re.compile(r'time=(\d+:\d+:\d+\.\d+)')

    for stderr_line in process.stderr:
        match = progress_regex.search(stderr_line)
        if match:
            time_str = match.group(1)
            hours, minutes, seconds = map(float, time_str.split(':'))
            total_seconds = hours * 3600 + minutes * 60 + seconds
            progress_percentage = int(total_seconds / total_duration * 100)
            logging.info(f"当前文件处理进度: {progress_percentage}%")
            if progress_callback:
                overall_progress = int(((file_index - 1 + total_seconds / total_duration) / total_files) * 100)
                progress_callback(overall_progress)