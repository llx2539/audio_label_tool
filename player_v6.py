import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import pandas as pd
import os
from PIL import Image, ImageTk
import pygame

# 初始化 pygame 播放模块
pygame.mixer.init()

root = tk.Tk()
root.title("音频标注工具")
root.geometry("1200x700")

# ========== 样式部分 ==========
style = ttk.Style()
style.theme_use('default')

# 让按钮文字在所有状态下都清晰显示
style.configure("TButton",
                font=("Arial", 14, "bold"),
                foreground="white",
                padding=6)

style.configure("Play.TButton", background="#28a745")
style.map("Play.TButton",
          background=[('active', '#218838'), ('pressed', '#1e7e34')],
          foreground=[('!disabled', 'white')])

style.configure("Prev.TButton", background="#17a2b8")
style.map("Prev.TButton",
          background=[('active', '#138496'), ('pressed', '#117a8b')],
          foreground=[('!disabled', 'white')])

style.configure("Next.TButton", background="#17a2b8")
style.map("Next.TButton",
          background=[('active', '#138496'), ('pressed', '#117a8b')],
          foreground=[('!disabled', 'white')])

style.configure("Yes.TButton", background="#007bff")
style.map("Yes.TButton",
          background=[('active', '#0069d9'), ('pressed', '#0056b3')],
          foreground=[('!disabled', 'white')])

style.configure("No.TButton", background="#dc3545")
style.map("No.TButton",
          background=[('active', '#c82333'), ('pressed', '#bd2130')],
          foreground=[('!disabled', 'white')])

# ========== 布局部分 ==========
frame_left = tk.Frame(root, width=800, height=700, bg="black")
frame_left.pack(side="left", fill="both", expand=True)

frame_right = tk.Frame(root, width=400, bg="#f8f9fa")
frame_right.pack(side="right", fill="y")

# 显示语谱图
label_img = tk.Label(frame_left, bg="black")
label_img.pack(fill="both", expand=True)

# 控制区：播放 + 上一首/下一首
frame_controls = tk.Frame(frame_left, bg="black")
frame_controls.pack(pady=10)

btn_prev = ttk.Button(frame_controls, text="⏮ 上一首", style="Prev.TButton")
btn_prev.grid(row=0, column=0, padx=15)

btn_play = ttk.Button(frame_controls, text="▶ 播放", style="Play.TButton")
btn_play.grid(row=0, column=1, padx=15)

btn_next = ttk.Button(frame_controls, text="下一首 ⏭", style="Next.TButton")
btn_next.grid(row=0, column=2, padx=15)

# 右侧标注区
tk.Label(frame_right, text="标注结果：", font=("Arial", 18), bg="#f8f9fa").pack(pady=40)

btn_yes = ttk.Button(frame_right, text="1", style="Yes.TButton")
btn_yes.pack(pady=10)

btn_no = ttk.Button(frame_right, text="0", style="No.TButton")
btn_no.pack(pady=10)

# 打开文件按钮（在右上角）
btn_open = ttk.Button(frame_right, text="📂 打开文件夹", style="Play.TButton")
btn_open.pack(pady=40)

root.mainloop()