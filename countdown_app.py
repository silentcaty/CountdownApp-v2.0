import tkinter as tk
import time
import random
from playsound import playsound
import threading, os, sys
from tkinter import filedialog, messagebox
import configparser
import pygame, configparser
from pystray import Icon as TrayIcon, Menu as TrayMenu, MenuItem as TrayMenuItem
from PIL import Image

pygame.mixer.init()

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class CountdownApp:

    # 初始界面
    def __init__(self, root):
        self.root = root
        self.root.title("Countdown App")
        self.root.geometry("600x500")  # 初始界面大小
        self.root.configure(bg="#2C3E50")  # 深蓝色背景
        self.is_paused = False  # 增加暂停状态变量

        self.custom_audio_path = self.load_audio_config()
        self.tray_icon_created = False

        # 自定义字体
        # font_style = ("Segoe UI", 14)
        font_style = ("Microsoft YaHei", 14, "bold")
        
        self.countdown_thread = None
        self.is_counting = False

        # Create frames
        self.initial_frame = tk.Frame(self.root, bg="#2C3E50")
        self.countdown_frame = tk.Frame(self.root, bg="#2C3E50")
        # 添加自定义设置区域
        settings_frame = tk.Frame(self.initial_frame, bg="#2C3E50")
        settings_frame.pack(pady=10)


        font_entry = ("Microsoft YaHei", 13)

        # 总倒计时时长设置
        tk.Label(settings_frame, text="总倒计时(分钟):", fg="white", bg="#2C3E50", font=font_entry).grid(row=0,
                                                                                                         column=0,
                                                                                                         pady=2,
                                                                                                         sticky='e')
        self.total_time_entry = tk.Entry(settings_frame, font=font_entry)
        self.total_time_entry.insert(0, "90")
        self.total_time_entry.grid(row=0, column=1, pady=2)

        # 随机休息间隔设置
        tk.Label(settings_frame, text="随机间隔最小(分钟):", fg="white", bg="#2C3E50", font=font_entry).grid(row=1,
                                                                                                             column=0,
                                                                                                             pady=2,
                                                                                                             sticky='e')
        self.random_min_entry = tk.Entry(settings_frame, font=font_entry)
        self.random_min_entry.insert(0, "3")
        self.random_min_entry.grid(row=1, column=1, pady=2)

        tk.Label(settings_frame, text="随机间隔最大(分钟):", fg="white", bg="#2C3E50", font=font_entry).grid(row=2,
                                                                                                             column=0,
                                                                                                             pady=2,
                                                                                                             sticky='e')
        self.random_max_entry = tk.Entry(settings_frame, font=font_entry)
        self.random_max_entry.insert(0, "5")
        self.random_max_entry.grid(row=2, column=1, pady=2)

        # 随机休息时长设置
        tk.Label(settings_frame, text="每次休息时长(秒):", fg="white", bg="#2C3E50", font=font_entry).grid(row=3,
                                                                                                           column=0,
                                                                                                           pady=2,
                                                                                                           sticky='e')
        self.break_duration_entry = tk.Entry(settings_frame, font=font_entry)
        self.break_duration_entry.insert(0, "10")
        self.break_duration_entry.grid(row=3, column=1, pady=2)

        # 音频选择
        tk.Label(settings_frame, text="选择提示音:", fg="white", bg="#2C3E50", font=font_entry).grid(row=4, column=0,
                                                                                                     pady=2, sticky='e')
        self.custom_audio_path = self.load_audio_config()

        self.audio_options = {
            "提示音1": "1.wav",
            "提示音2": "2.wav",
            "提示音3": "3.wav",
            "提示音4": "4.mp3",
            "自定义音频": "custom"
        }

        self.selected_audio = tk.StringVar()
        self.selected_audio.set("提示音1")  # 默认选项设置为字典的某个key值
        self.audio_menu = tk.OptionMenu(settings_frame, self.selected_audio, *self.audio_options.keys())
        self.audio_menu.grid(row=4, column=1, pady=2, sticky='w')

        # 试听按钮
        self.test_audio_button = tk.Button(settings_frame, text="试听", command=self.test_audio)
        self.test_audio_button.grid(row=4, column=2, padx=5)

        # 上传按钮
        self.upload_button = tk.Button(settings_frame, text="上传音频", command=self.upload_audio)
        self.upload_button.grid(row=5, column=1, pady=5, sticky='w')

        # Initial frame: Start and Shutdown buttons
        self.start_button = tk.Button(
            self.initial_frame, text="开始倒计时", command=self.start_countdowns,
            bg="#1ABC9C", fg="white", font=font_style, padx=15, pady=8, relief='flat', cursor="hand2"
        )
        self.start_button.pack(pady=15, ipadx=10, ipady=5)

        self.initial_shutdown_button = tk.Button(
            self.initial_frame, text="退出程序", command=self.shutdown,
            bg="#E74C3C", fg="white", font=font_style, padx=15, pady=8, relief='flat', cursor="hand2"
        )
        self.initial_shutdown_button.pack(pady=15, ipadx=10, ipady=5)

        # Countdown frame: Countdown label and Shutdown button
        self.countdown_label = tk.Label(
            self.countdown_frame, text="90:00", font=("Microsoft YaHei", 48, "bold"), fg="white", bg="#2C3E50"
        )
        self.countdown_label.pack(pady=20)

        self.pause_button = tk.Button(
            self.countdown_frame, text="暂停", command=self.toggle_pause,
            bg="#3498DB", fg="white", font=font_style,
            padx=15, pady=8, relief='flat', cursor="hand2"
        )
        self.pause_button.pack(pady=10, ipadx=10, ipady=5)

        self.countdown_shutdown_button = tk.Button(
            self.countdown_frame, text="停止倒计时", command=self.stop_countdowns,
            bg="#FF4136", fg="white", font=font_style, padx=15, pady=8, relief='flat', cursor="hand2"
        )
        self.countdown_shutdown_button.pack(pady=15, ipadx=10, ipady=5)


        # 初始状态
        self.initial_frame.pack(expand=True)


    def start_countdowns(self):
        # 获取用户设置参数
        self.total_time_sec = int(float(self.total_time_entry.get()) * 60)
        self.random_min_sec = int(float(self.random_min_entry.get()) * 60)
        self.random_max_sec = int(float(self.random_max_entry.get()) * 60)
        self.break_duration_sec = int(self.break_duration_entry.get())

        self.audio_file = self.selected_audio.get()

        if self.audio_file == "自定义音频" and not self.custom_audio_path:
            messagebox.showwarning("提示", "请先上传自定义音频！")
            return

        self.start_button.config(state="disabled")
        self.initial_frame.pack_forget()
        self.countdown_frame.pack()

        # 倒计时开始后才创建“最小化到托盘”按钮（仅创建一次）
        if not hasattr(self, "minimize_button"):
            font_style = ("Microsoft YaHei", 14, "bold")
            self.minimize_button = tk.Button(
                self.countdown_frame,
                text="最小化到托盘",
                command=self.minimize_to_tray,
                bg="#95A5A6", fg="white", font=font_style,
                padx=15, pady=8, relief='flat', cursor="hand2"
            )
            self.minimize_button.pack(pady=10, ipadx=10, ipady=5)

        self.is_counting = True
        self.countdown_thread = threading.Thread(target=self.countdown_loop, daemon=True)
        self.countdown_thread.start()

        self.update_90min_countdown(self.total_time_sec)

    def stop_countdowns(self):
        # Stop countdowns and return to initial frame
        self.is_counting = False
        self.countdown_frame.pack_forget()
        self.initial_frame.pack()
        self.start_button.config(state="normal")

    def test_audio(self):
        selected_audio_key = self.selected_audio.get()
        audio_file = self.audio_options[selected_audio_key]

        if audio_file == "custom":
            if not self.custom_audio_path:
                messagebox.showinfo("提示", "请上传自定义音频后再试听！")
                return
            audio_path = self.custom_audio_path
        else:
            audio_path = resource_path(audio_file)

        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()

    # 暂停按钮
    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_button.config(text="继续", bg="#E67E22")
        else:
            self.pause_button.config(text="暂停", bg="#3498DB")

    def save_audio_config(self, path):
        config = configparser.ConfigParser()
        config['AUDIO'] = {'custom_audio_path': path}
        with open('settings.ini', 'w') as configfile:
            config.write(configfile)

    def load_audio_config(self):
        config = configparser.ConfigParser()
        config.read('settings.ini')
        return config['AUDIO'].get('custom_audio_path', '') if 'AUDIO' in config else ''

    def upload_audio(self):
        filepath = filedialog.askopenfilename(
            title="选择音频文件",
            filetypes=[("音频文件", "*.wav *.mp3 *.ogg")]
        )
        if filepath:
            self.custom_audio_path = filepath
            self.save_audio_config(filepath)
            self.selected_audio.set("自定义音频")


    def shutdown(self):
        # Terminate the application
        self.root.quit()

    def update_90min_countdown(self, remaining):
        if self.is_counting and remaining >= 0:
            if not self.is_paused:
                minutes = remaining // 60
                seconds = remaining % 60
                self.countdown_label.config(text=f"{minutes:02d}:{seconds:02d}")
                remaining -= 1
            self.root.after(1000, self.update_90min_countdown, remaining)


    def countdown_loop(self):
        start_time = time.time()
        elapsed_pause_time = 0

        while self.is_counting and (time.time() - start_time - elapsed_pause_time < self.total_time_sec):
            interval = random.randint(self.random_min_sec, self.random_max_sec)
            elapsed = 0
            while elapsed < interval and self.is_counting:
                time.sleep(1)
                if not self.is_paused:
                    elapsed += 1
                else:
                    elapsed_pause_time += 1
            if self.is_counting and not self.is_paused:
                self.root.after(0, self.show_countdown, self.break_duration_sec)

        if self.is_counting:
            self.root.after(0, self.show_countdown, 20 * 60)  # 最后20分钟保持原有逻辑

    # 黑屏倒计时
    def show_countdown(self, seconds):
        countdown_window = tk.Toplevel(self.root)
        countdown_window.configure(bg="black")
        countdown_window.attributes("-fullscreen", True)
        countdown_window.attributes("-topmost", True)
        countdown_window.overrideredirect(True)  # 可选，去除窗口边框
        countdown_window.lift()
        countdown_window.focus_force()
        countdown_window.deiconify()

        selected_audio_key = self.selected_audio.get()
        audio_file = self.audio_options[selected_audio_key]
        audio_path = self.custom_audio_path if audio_file == "custom" else resource_path(audio_file)

        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()  # 异步播放

        label = tk.Label(countdown_window, text="", font=("Microsoft YaHei", 100, "bold"), fg="#2ECC71", bg="#000000")

        label.pack(expand=True)

        tip_label = tk.Label(
            countdown_window,
            text="按 Esc 退出",
            font=("Microsoft YaHei", 16),
            fg="#888888",
            bg="#000000"
        )
        tip_label.pack(side="top", anchor="ne", padx=20, pady=10)

        def update_countdown(remaining):
            if remaining >= 0:
                label.config(text=f"{remaining} 秒")
                countdown_window.after(1000, update_countdown, remaining - 1)
            else:
                countdown_window.destroy()

        update_countdown(seconds)
        countdown_window.bind("<Escape>", lambda e: countdown_window.destroy())

    def setup_tray(self):
        icon_path = resource_path("clock_icon.ico")
        image = Image.open(icon_path)

        menu = TrayMenu(
            TrayMenuItem('显示窗口', self.restore_window),
            TrayMenuItem('退出程序', self.quit_from_tray)
        )

        self.tray_icon = TrayIcon("CountdownApp", image, "倒计时程序", menu)
        self.tray_icon.icon = image
        self.tray_icon.title = "CountdownApp"

        try:
            self.tray_icon._on_click = self.restore_window  # 支持左键点击恢复窗口（仅限某些平台）
        except Exception:
            pass

        self.tray_icon.run_detached()

    def restore_window(self, icon=None, item=None):
        self.root.deiconify()

    def quit_from_tray(self, icon=None, item=None):
        self.tray_icon.stop()
        self.root.quit()

    def minimize_to_tray(self):
        self.root.withdraw()
        if not hasattr(self, 'tray_icon_created') or not self.tray_icon_created:
            self.setup_tray()
            self.tray_icon_created = True


if __name__ == "__main__":
    root = tk.Tk()
    app = CountdownApp(root)
    root.mainloop()