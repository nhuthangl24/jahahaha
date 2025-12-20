import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class RestartHandler(FileSystemEventHandler):
    def __init__(self, script):
        self.script = script
        self.process = None
        self.start_process()

    def start_process(self):
        if self.process:
            # Kill tiến trình cũ
            self.process.terminate()
            self.process.wait()
        
        print(f"\n🔄 Phát hiện thay đổi! Đang khởi động lại ứng dụng...\n")
        # Khởi động lại main.py
        self.process = subprocess.Popen([sys.executable, self.script])

    def on_modified(self, event):
        # Chỉ restart khi sửa file .py hoặc .qss
        if event.src_path.endswith(".py") or event.src_path.endswith(".qss"):
            self.start_process()

if __name__ == "__main__":
    script_to_run = "main.py" # File chính của bạn
    
    event_handler = RestartHandler(script_to_run)
    observer = Observer()
    
    # Theo dõi thư mục hiện tại và các thư mục con
    observer.schedule(event_handler, path=".", recursive=True)
    observer.start()
    
    print(f"👀 Đang theo dõi thay đổi trong project. Nhấn Ctrl+C để dừng.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if event_handler.process:
            event_handler.process.terminate()
    observer.join()