import tkinter as tk
import time
import threading
import random
from playsound import playsound
import sys
import os


class CountdownApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Countdown App")
        self.root.geometry("300x300")  # 调整窗口大小以容纳新组件

        # Initialize state variables
        self.countdown_thread = None
        self.is_counting = False
        self.is_paused = False  # 新增暂停状态
        self.remaining_time = 0  # 新增剩余时间记录
        self.focus_duration = 90 * 60  # 默认专注时间 90 分钟

        # Create frames
        self.initial_frame = tk.Frame(self.root)
        self.countdown_frame = tk.Frame(self.root)

        # 新增专注时间选择
        self.focus_var = tk.StringVar(value="90")
        focus_options = ["90", "60", "30"]
        self.focus_menu = tk.OptionMenu(self.initial_frame, self.focus_var, *focus_options)
        self.focus_menu.pack(pady=10)

        # Initial frame: Start Countdowns and Shut Down buttons
        self.start_button = tk.Button(self.initial_frame, text="Start Countdowns", command=self.start_countdowns)
        self.start_button.pack(pady=10)
        self.initial_shutdown_button = tk.Button(self.initial_frame, text="Shut Down", command=self.shutdown)
        self.initial_shutdown_button.pack(pady=10)

        # Countdown frame: 90-minute countdown label, Pause/Resume, and Shut Down buttons
        self.countdown_label = tk.Label(self.countdown_frame, text="90:00", font=("Arial", 24))
        self.countdown_label.pack(pady=10)
        self.pause_button = tk.Button(self.countdown_frame, text="Pause", command=self.toggle_pause)
        self.pause_button.pack(pady=10)
        self.countdown_shutdown_button = tk.Button(self.countdown_frame, text="Shut Down", command=self.stop_countdowns)
        self.countdown_shutdown_button.pack(pady=10)

        # Show initial frame
        self.initial_frame.pack()

    def start_countdowns(self):
        # Disable start button and switch to countdown frame
        self.start_button.config(state="disabled")
        self.initial_frame.pack_forget()
        self.countdown_frame.pack()

        # 获取用户选择的专注时间
        self.focus_duration = int(self.focus_var.get()) * 60
        self.remaining_time = self.focus_duration  # 初始化剩余时间

        # Start countdown process
        self.is_counting = True
        self.is_paused = False
        self.countdown_thread = threading.Thread(target=self.countdown_loop, daemon=True)
        self.countdown_thread.start()

        # Start updating the countdown display
        self.update_countdown(self.remaining_time)

    def toggle_pause(self):
        if self.is_counting:
            self.is_paused = not self.is_paused
            if self.is_paused:
                self.pause_button.config(text="Resume")
            else:
                self.pause_button.config(text="Pause")

    def stop_countdowns(self):
        # Stop countdowns and return to initial frame
        self.is_counting = False
        self.is_paused = False
        self.countdown_frame.pack_forget()
        self.initial_frame.pack()
        self.start_button.config(state="normal")
        self.pause_button.config(text="Pause")

    def shutdown(self):
        # Terminate the application
        self.is_counting = False
        self.root.quit()

    def update_countdown(self, remaining):
        if self.is_counting:
            if not self.is_paused:
                minutes = remaining // 60
                seconds = remaining % 60
                self.countdown_label.config(text=f"{minutes:02d}:{seconds:02d}")
                if remaining > 0:
                    self.root.after(1000, self.update_countdown, remaining - 1)
                    self.remaining_time = remaining
                else:
                    # 专注时间结束，触发休息倒计时
                    rest_duration = int(self.focus_duration * 0.22)
                    self.root.after(0, self.show_countdown, rest_duration)
            else:
                self.root.after(1000, self.update_countdown, remaining)

    def countdown_loop(self):
        start_time = time.time()
        elapsed_time = 0

        while self.is_counting and elapsed_time < self.focus_duration:
            if not self.is_paused:
                # Random interval between 3 to 5 minutes (180 to 300 seconds)
                interval = random.randint(180, 300)
                # Sleep for the interval, checking periodically to allow interruption
                interval_start = time.time()
                while elapsed_time < self.focus_duration and time.time() - interval_start < interval and self.is_counting and not self.is_paused:
                    time.sleep(1)
                    elapsed_time = int(time.time() - start_time)
                if self.is_counting and not self.is_paused:
                    self.root.after(0, self.show_countdown, 10)
            else:
                time.sleep(1)

        # After focus duration, trigger rest countdown if still counting
        if self.is_counting:
            rest_duration = int(self.focus_duration * 0.22)
            self.root.after(0, self.show_countdown, rest_duration)

    def show_countdown(self, seconds):
        # 创建一个新的全屏窗口
        countdown_window = tk.Toplevel(self.root)
        countdown_window.attributes("-fullscreen", True)
        countdown_window.configure(bg="black")

        # 强制置顶显示
        countdown_window.attributes("-topmost", True)
        countdown_window.lift()

        def resource_path(relative_path):
            """用于打包后正确找到资源文件"""
            if hasattr(sys, '_MEIPASS'):
                return os.path.join(sys._MEIPASS, relative_path)
            return os.path.join(os.path.abspath("."), relative_path)

        # 播放“叮”声（在窗口弹出时）
        try:
            # playsound("ding.wav")  # 确保该文件与代码在同一目录
            playsound(resource_path("ding.wav"))
        except Exception as e:
            print("播放音效失败：", e)

        label = tk.Label(
            countdown_window,
            text="",
            font=("Arial", 100),
            fg="white",
            bg="black"
        )
        label.pack(expand=True)

        def update_countdown(remaining):
            if remaining >= 0:
                label.config(text=f"{remaining} seconds")
                countdown_window.after(1000, update_countdown, remaining - 1)
            else:
                countdown_window.destroy()
                if seconds == 20 * 60:
                    self.root.quit()

        update_countdown(seconds)
        countdown_window.bind("<Escape>", lambda e: countdown_window.destroy())


        # Start the countdown
        update_countdown(seconds)

        # Allow escape key to exit full-screen (optional, for testing)
        countdown_window.bind("<Escape>", lambda e: countdown_window.destroy())

if __name__ == "__main__":
    root = tk.Tk()
    app = CountdownApp(root)
    root.mainloop()