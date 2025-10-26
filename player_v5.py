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

# ================= 路径初始化 =================
AUDIO_DIR = None  # 初始为空，由用户选择
SPEC_DIR = None
OUTPUT_FILE = "annotations.csv"

# ================= 主窗口 =================
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
frame_right = tk.Frame(root, bg="#fafafa", width=300)
frame_right.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

# 选择文件夹按钮
btn_open_folder = tk.Button(frame_right, text="打开音频文件夹", width=20, bg="#4CAF50", fg="white", font=("Arial",12))
btn_open_folder.pack(pady=10)

# 音频选择 Combobox
label_info = tk.Label(frame_right, text="选择音频文件：", bg="#fafafa", font=("Arial", 12))
label_info.pack(pady=5)
selected_file = tk.StringVar()
combo = ttk.Combobox(frame_right, textvariable=selected_file, values=[], width=25)
combo.pack(pady=5)

# 播放控制
btn_play = tk.Button(frame_right, text="▶ 播放", width=10, bg="#007bff", fg="white", font=("Arial",12))
btn_play.pack(pady=10)

# 进度条
progress = ttk.Scale(frame_right, from_=0, to=100, orient="horizontal", length=200)
progress.pack(pady=10)

# 标注按钮
label_tag = tk.Label(frame_right, text="标注结果：", bg="#fafafa", font=("Arial", 12))
label_tag.pack(pady=15)
btn_yes = tk.Button(frame_right, text="1", width=10, bg="#007bff", fg="white", font=("Arial",14), activebackground="#0056b3")
btn_no = tk.Button(frame_right, text="0", width=10, bg="#dc3545", fg="white", font=("Arial",14), activebackground="#a71d2a")
btn_yes.pack(pady=5)
btn_no.pack(pady=5)

# 上一首 / 下一首按钮
btn_prev = tk.Button(frame_right, text="⬅ 上一首", width=10, bg="#6c757d", fg="white", font=("Arial",12))
btn_next = tk.Button(frame_right, text="下一首 ➡", width=10, bg="#6c757d", fg="white", font=("Arial",12))
btn_prev.pack(pady=10)
btn_next.pack(pady=5)

# ================= 音频播放逻辑 =================
audio_files = []
audio_data, sr = None, None
is_playing = False
current_index = 0
current_thread = None

def load_spectrogram(filename):
    """加载语谱图"""
    if not SPEC_DIR:
        return
    spec_path = os.path.join(SPEC_DIR, os.path.splitext(filename)[0] + ".png")
    canvas.delete("all")
    if not os.path.exists(spec_path):
        canvas.create_text(canvas.winfo_width()//2, canvas.winfo_height()//2,
                           text="⚠ 未找到对应语谱图", fill="white", font=("Arial", 16))
        return
    img = Image.open(spec_path)
    w, h = canvas.winfo_width(), canvas.winfo_height()
    img = img.resize((w, h), Image.LANCZOS)
    img_tk = ImageTk.PhotoImage(img)
    canvas.image = img_tk
    canvas.create_image(w//2, h//2, image=img_tk)

def load_audio(filename):
    """加载音频"""
    global audio_data, sr
    path = os.path.join(AUDIO_DIR, filename)
    audio_data, sr = sf.read(path)
    progress.set(0)

def update_progress(duration):
    """更新播放进度条"""
    global is_playing
    start_time = time.time()
    while is_playing and time.time() - start_time <= duration:
        elapsed = time.time() - start_time
        progress.set((elapsed / duration) * 100)
        time.sleep(0.1)
    progress.set(100)
    is_playing = False
    btn_play.config(text="▶ 播放", bg="#007bff")

def play_audio():
    global is_playing, current_thread
    if not audio_files:
        return
    if not is_playing:
        load_audio(audio_files[current_index])
        is_playing = True
        sd.play(audio_data, sr)
        btn_play.config(text="⏸ 暂停", bg="#f39c12")
        current_thread = threading.Thread(target=update_progress, args=(len(audio_data)/sr,))
        current_thread.start()
    else:
        sd.stop()
        is_playing = False
        btn_play.config(text="▶ 播放", bg="#007bff")

def save_label(value):
    global current_index
    if not audio_files:
        return
    filename = audio_files[current_index]
    exists = os.path.exists(OUTPUT_FILE)
    with open(OUTPUT_FILE, mode='a', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["filename","label"])
        writer.writerow([filename, value])
    print(f"✅ 保存: {filename} -> {value}")
    next_file()  # 自动切换到下一首

def next_file():
    global current_index
    if audio_files and current_index < len(audio_files) -1:
        current_index +=1
        selected_file.set(audio_files[current_index])
        load_spectrogram(audio_files[current_index])

def prev_file():
    global current_index
    if audio_files and current_index >0:
        current_index -=1
        selected_file.set(audio_files[current_index])
        load_spectrogram(audio_files[current_index])

def open_folder():
    global AUDIO_DIR, SPEC_DIR, audio_files, current_index
    AUDIO_DIR = filedialog.askdirectory(title="选择音频文件夹")
    if not AUDIO_DIR:
        return
    SPEC_DIR = os.path.join(os.path.dirname(AUDIO_DIR),"spectrogram")
    audio_files = sorted([f for f in os.listdir(AUDIO_DIR) if f.lower().endswith((".wav",".mp3"))])
    if not audio_files:
        return
    current_index = 0
    selected_file.set(audio_files[0])
    combo['values'] = audio_files
    load_spectrogram(audio_files[0])

# ================= 绑定事件 =================
btn_play.config(command=play_audio)
btn_yes.config(command=lambda: save_label(1))
btn_no.config(command=lambda: save_label(0))
btn_next.config(command=next_file)
btn_prev.config(command=prev_file)
btn_open_folder.config(command=open_folder)
combo.bind("<<ComboboxSelected>>", lambda e: load_spectrogram(selected_file.get()))

root.mainloop()