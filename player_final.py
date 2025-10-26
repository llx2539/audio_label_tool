import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from PIL import Image, ImageTk
import pygame
import pandas as pd

pygame.mixer.init()

class AudioLabelTool:
    def __init__(self, root):
        self.root = root
        self.root.title("音频标注工具")
        self.root.geometry("1200x700")

        self.audio_folder = ""
        self.spec_folder = ""
        self.audio_files = []
        self.current_index = 0
        self.is_playing = False
        self.output_file = "labels.csv"

        # 样式设置
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TButton", font=("Arial", 14, "bold"), foreground="white", padding=6)
        style.configure("Play.TButton", background="#28a745")
        style.map("Play.TButton", background=[('active', '#218838'), ('pressed', '#1e7e34')])
        style.configure("Prev.TButton", background="#17a2b8")
        style.map("Prev.TButton", background=[('active', '#138496'), ('pressed', '#117a8b')])
        style.configure("Next.TButton", background="#17a2b8")
        style.map("Next.TButton", background=[('active', '#138496'), ('pressed', '#117a8b')])
        style.configure("Yes.TButton", background="#007bff")
        style.map("Yes.TButton", background=[('active', '#0069d9'), ('pressed', '#0056b3')])
        style.configure("No.TButton", background="#dc3545")
        style.map("No.TButton", background=[('active', '#c82333'), ('pressed', '#bd2130')])

        # 布局
        self.frame_left = tk.Frame(root, width=800, height=700, bg="black")
        self.frame_left.pack(side="left", fill="both", expand=True)
        self.frame_right = tk.Frame(root, width=400, bg="#f8f9fa")
        self.frame_right.pack(side="right", fill="y")

        # 显示语谱图
        self.label_img = tk.Label(self.frame_left, bg="black")
        self.label_img.pack(fill="both", expand=True)

        # 控制区（播放按钮 + 上一首/下一首）
        frame_controls = tk.Frame(self.frame_left, bg="black")
        frame_controls.pack(pady=10)

        self.btn_prev = ttk.Button(frame_controls, text="⏮ 上一首", style="Prev.TButton", command=self.prev_audio)
        self.btn_prev.grid(row=0, column=0, padx=15)
        self.btn_play = ttk.Button(frame_controls, text="▶ 播放", style="Play.TButton", command=self.play_pause)
        self.btn_play.grid(row=0, column=1, padx=15)
        self.btn_next = ttk.Button(frame_controls, text="下一首 ⏭", style="Next.TButton", command=self.next_audio)
        self.btn_next.grid(row=0, column=2, padx=15)

        # 播放进度条
        self.progress = ttk.Scale(self.frame_left, from_=0, to=100, orient="horizontal", length=700)
        self.progress.pack(pady=10)

        # 打开文件夹
        self.btn_open = ttk.Button(self.frame_right, text="📂 打开文件夹", style="Play.TButton", command=self.open_folder)
        self.btn_open.pack(pady=40)

        # 标注按钮
        tk.Label(self.frame_right, text="标注结果：", font=("Arial", 18), bg="#f8f9fa").pack(pady=40)
        self.btn_yes = ttk.Button(self.frame_right, text="1", style="Yes.TButton", command=lambda: self.save_label(1))
        self.btn_yes.pack(pady=10)
        self.btn_no = ttk.Button(self.frame_right, text="0", style="No.TButton", command=lambda: self.save_label(0))
        self.btn_no.pack(pady=10)

        # 定时检测播放状态
        self.root.after(500, self.check_music_end)
        self.root.after(500, self.update_progress)

    # ===== 功能实现 =====

    def open_folder(self):
        folder = filedialog.askdirectory(title="选择包含 audio/ 与 spectrogram/ 的文件夹")
        if not folder:
            return
        self.audio_folder = os.path.join(folder, "audio")
        self.spec_folder = os.path.join(folder, "spectrogram")

        if not os.path.exists(self.audio_folder) or not os.path.exists(self.spec_folder):
            messagebox.showerror("错误", "该文件夹下必须包含 audio/ 和 spectrogram/ 两个子文件夹！")
            return

        self.audio_files = [f for f in os.listdir(self.audio_folder)
                            if f.lower().endswith(('.wav', '.mp3'))]
        self.audio_files.sort()

        if not self.audio_files:
            messagebox.showerror("错误", "未找到音频文件！")
            return

        self.current_index = 0
        self.load_current_audio()

    def load_current_audio(self):
        audio_path = os.path.join(self.audio_folder, self.audio_files[self.current_index])
        spec_path = os.path.join(self.spec_folder,
                                 os.path.splitext(self.audio_files[self.current_index])[0] + ".png")

        # 加载语谱图
        if os.path.exists(spec_path):
            img = Image.open(spec_path)
            img = img.resize((800, 500))
            self.img_tk = ImageTk.PhotoImage(img)
            self.label_img.config(image=self.img_tk)
        else:
            self.label_img.config(image='', text='[无语谱图]', fg='white', bg='black', font=('Arial', 20))

        pygame.mixer.music.load(audio_path)
        self.root.title(f"音频标注工具 - {os.path.basename(audio_path)}")
        self.progress.set(0)

    def play_pause(self):
        if not self.audio_files:
            return
        if not self.is_playing:
            pygame.mixer.music.play()
            self.is_playing = True
            self.btn_play.config(text="⏸ 暂停")
        else:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.btn_play.config(text="▶ 播放")

    def next_audio(self):
        if not self.audio_files:
            return
        self.current_index = (self.current_index + 1) % len(self.audio_files)
        pygame.mixer.music.stop()
        self.is_playing = False
        self.btn_play.config(text="▶ 播放")
        self.load_current_audio()

    def prev_audio(self):
        if not self.audio_files:
            return
        self.current_index = (self.current_index - 1) % len(self.audio_files)
        pygame.mixer.music.stop()
        self.is_playing = False
        self.btn_play.config(text="▶ 播放")
        self.load_current_audio()

    def check_music_end(self):
        """检测播放结束后恢复按钮"""
        if not pygame.mixer.music.get_busy() and self.is_playing:
            self.is_playing = False
            self.btn_play.config(text="▶ 播放")
        self.root.after(500, self.check_music_end)

    def update_progress(self):
        """更新播放进度条"""
        if self.is_playing:
            try:
                pos = pygame.mixer.music.get_pos() / 1000  # 毫秒转秒
                length = self.get_audio_length()
                if length > 0:
                    self.progress.set(pos / length * 100)
            except:
                pass
        self.root.after(500, self.update_progress)

    def get_audio_length(self):
        """获取音频时长（秒）"""
        try:
            import wave
            import contextlib
            audio_path = os.path.join(self.audio_folder, self.audio_files[self.current_index])
            if audio_path.endswith(".wav"):
                with contextlib.closing(wave.open(audio_path, 'r')) as f:
                    frames = f.getnframes()
                    rate = f.getframerate()
                    return frames / float(rate)
        except:
            return 0
        return 0

    def save_label(self, label_value):
        if not self.audio_files:
            return
        file_name = self.audio_files[self.current_index]
        data = {"file": [file_name], "label": [label_value]}

        if os.path.exists(self.output_file):
            df = pd.read_csv(self.output_file)
            df = df[df["file"] != file_name]
            df = pd.concat([df, pd.DataFrame(data)], ignore_index=True)
        else:
            df = pd.DataFrame(data)
        df.to_csv(self.output_file, index=False)
        messagebox.showinfo("已保存", f"{file_name} 标注为 {label_value}")

root = tk.Tk()
app = AudioLabelTool(root)
root.mainloop()