import os
import csv
import threading
import time
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from PIL import Image, ImageTk
import sounddevice as sd
import soundfile as sf

# =============== 路径设置 ===============
AUDIO_DIR = "./audio"
SPEC_DIR = "./spectrogram"
OUTPUT_FILE = "annotations.csv"

# =============== 主界面 ===============
root = tk.Tk()
root.title("音频语谱图标注工具")
root.geometry("1200x700")
root.configure(bg="#f7f7f7")

# =============== 左侧：语谱图显示 ===============
frame_left = tk.Frame(root, bg="white", relief=tk.RIDGE, bd=2)
frame_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

canvas = tk.Canvas(frame_left, bg="black")
canvas.pack(fill=tk.BOTH, expand=True)

# =============== 右侧控制区 ===============
frame_right = tk.Frame(root, bg="#fafafa", width=250)
frame_right.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

# 音频选择
label_info = tk.Label(frame_right, text="选择音频文件：", bg="#fafafa", font=("Arial", 12))
label_info.pack(pady=10)

audio_files = sorted([f for f in os.listdir(AUDIO_DIR) if f.lower().endswith((".wav", ".mp3"))])
selected_file = tk.StringVar(value=audio_files[0] if audio_files else "")

combo = ttk.Combobox(frame_right, textvariable=selected_file, values=audio_files, width=25)
combo.pack(pady=5)

# 播放控制
progress = ttk.Scale(frame_right, from_=0, to=100, orient="horizontal", length=200)
progress.pack(pady=15)

btn_play = tk.Button(frame_right, text="▶ 播放", width=10, bg="#4CAF50", fg="white", font=("Arial",12))
btn_play.pack(pady=10)

# 标注按钮
label_tag = tk.Label(frame_right, text="标注结果：", bg="#fafafa", font=("Arial", 12))
label_tag.pack(pady=15)

# 使用 ttk.Style 让按钮文字和颜色更清晰
style = ttk.Style()
style.theme_use('default')  # 保证跨平台一致性

btn_yes = tk.Button(frame_right, text="1", font=("Arial", 14), width=10,
                    bg="#007bff", fg="white", activebackground="#0056b3", activeforeground="white")
btn_no = tk.Button(frame_right, text="0", font=("Arial", 14), width=10,
                   bg="#dc3545", fg="white", activebackground="#a71d2a", activeforeground="white")

btn_yes.pack(pady=5)
btn_no.pack(pady=5)

# =============== 功能逻辑 ===============
audio_data, sr = None, None
is_playing = False
current_thread = None

def load_spectrogram(filename):
    """加载语谱图"""
    spec_path = os.path.join(SPEC_DIR, os.path.splitext(filename)[0] + ".png")
    if not os.path.exists(spec_path):
        canvas.delete("all")
        canvas.create_text(canvas.winfo_width()//2, canvas.winfo_height()//2,
                           text="⚠ 未找到对应语谱图", fill="white", font=("Arial", 16))
        return

    img = Image.open(spec_path)
    # 调整大小适应显示区域（保持高清）
    w, h = canvas.winfo_width(), canvas.winfo_height()
    img = img.resize((w, h), Image.LANCZOS)
    img_tk = ImageTk.PhotoImage(img)
    canvas.image = img_tk
    canvas.delete("all")
    canvas.create_image(w // 2, h // 2, image=img_tk)

def load_audio(filename):
    """加载音频"""
    global audio_data, sr
    path = os.path.join(AUDIO_DIR, filename)
    audio_data, sr = sf.read(path)
    progress.set(0)

def update_progress(duration):
    """更新播放进度条"""
    start_time = time.time()
    global is_playing
    while is_playing and time.time() - start_time <= duration:
        elapsed = time.time() - start_time
        progress.set((elapsed / duration) * 100)
        time.sleep(0.1)
    progress.set(100)
    is_playing = False
    btn_play.config(text="▶ 播放", bg="#4CAF50")

def play_audio():
    """播放或暂停音频"""
    global is_playing, current_thread
    if not selected_file.get():
        return
    if not is_playing:
        load_audio(selected_file.get())
        is_playing = True
        sd.play(audio_data, sr)
        btn_play.config(text="⏸ 暂停", bg="#f39c12")
        current_thread = threading.Thread(target=update_progress, args=(len(audio_data)/sr,))
        current_thread.start()
    else:
        sd.stop()
        is_playing = False
        btn_play.config(text="▶ 播放", bg="#4CAF50")

def save_label(value):
    """保存标注到 CSV"""
    filename = selected_file.get()
    if not filename:
        return
    exists = os.path.exists(OUTPUT_FILE)
    with open(OUTPUT_FILE, mode='a', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["filename", "label"])
        writer.writerow([filename, value])
    print(f"✅ 保存：{filename} -> {value}")

# =============== 事件绑定 ===============
btn_play.config(command=play_audio)
btn_yes.config(command=lambda: save_label(1))
btn_no.config(command=lambda: save_label(0))
combo.bind("<<ComboboxSelected>>", lambda e: load_spectrogram(selected_file.get()))

# 默认加载第一个语谱图
if audio_files:
    load_spectrogram(audio_files[0])

# =============== 启动界面 ===============
root.mainloop()