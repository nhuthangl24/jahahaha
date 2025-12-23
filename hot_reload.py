import sys
import time
import os
import subprocess

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("⚠️  Chưa cài đặt thư viện 'watchdog'.")
    print("👉 Vui lòng chạy lệnh: pip install watchdog")
    sys.exit(1)

class ReloadHandler(FileSystemEventHandler):
    def __init__(self, main_script):
        self.main_script = main_script
        self.process = None
        self.restart()

    def restart(self):
        if self.process:
            try:
                # Kill process tree if needed, but simple terminate is usually enough for GUI
                self.process.terminate()
                self.process.wait()
            except Exception as e:
                print(f"Lỗi khi dừng process: {e}")
            print("\n🔄 Đang khởi động lại ứng dụng...\n")
        else:
            print("\n🚀 Khởi động ứng dụng lần đầu...\n")
        
        self.process = subprocess.Popen([sys.executable, self.main_script])

    def on_modified(self, event):
        if event.is_directory:
            return
        
        filename = event.src_path
        # Chỉ reload khi sửa file .py hoặc .qss
        if filename.endswith('.py') or filename.endswith('.qss'):
            # Bỏ qua file hot_reload.py chính nó để tránh loop
            if "hot_reload.py" in filename:
                return
                
            print(f"\n📝 Phát hiện thay đổi: {os.path.basename(filename)}")
            self.restart()

if __name__ == "__main__":
    script_to_run = "main.py"
    
    if not os.path.exists(script_to_run):
        print(f"❌ Không tìm thấy file {script_to_run}")
        sys.exit(1)

    print(f"👀 Đang theo dõi thay đổi trong thư mục hiện tại...")
    print("👉 Sửa code và lưu file để tự động reload.")
    print("👉 Nhấn Ctrl+C để thoát.")
    
    event_handler = ReloadHandler(script_to_run)
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if event_handler.process:
            event_handler.process.terminate()
    observer.join()
