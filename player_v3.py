import sys
import os
import librosa
import sounddevice as sd
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
    QFileDialog, QSlider, QHBoxLayout
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer


class AudioPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎵 音频播放器 + 语谱图查看")
        self.setGeometry(300, 200, 600, 550)

        # 界面布局
        self.layout = QVBoxLayout()
        self.label = QLabel("请选择一个音频文件")
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)

        # 语谱图显示区域
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.image_label)

        # 控制按钮区
        control_layout = QHBoxLayout()
        self.btn_open = QPushButton("打开音频")
        self.btn_open.clicked.connect(self.open_file)
        control_layout.addWidget(self.btn_open)

        self.btn_play = QPushButton("▶ 播放")
        self.btn_play.clicked.connect(self.play_audio)
        control_layout.addWidget(self.btn_play)

        self.btn_pause = QPushButton("⏸ 暂停")
        self.btn_pause.clicked.connect(self.pause_audio)
        control_layout.addWidget(self.btn_pause)

        self.btn_stop = QPushButton("⏹ 停止")
        self.btn_stop.clicked.connect(self.stop_audio)
        control_layout.addWidget(self.btn_stop)

        self.layout.addLayout(control_layout)

        # 进度条
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setEnabled(False)
        self.slider.sliderPressed.connect(self.pause_audio)
        self.slider.sliderReleased.connect(self.seek_audio)
        self.layout.addWidget(self.slider)

        self.setLayout(self.layout)

        # 音频数据变量
        self.audio_data = None
        self.sr = None
        self.position = 0
        self.is_playing = False
        self.stream = None

        # 定时器更新播放进度
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_slider)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择音频文件", "", "音频文件 (*.wav *.mp3)")
        if file_path:
            self.audio_data, self.sr = librosa.load(file_path, sr=None)
            self.duration = len(self.audio_data) / self.sr
            self.slider.setMaximum(int(self.duration))
            self.slider.setEnabled(True)

            # 自动加载语谱图
            spectrogram_path = self.find_spectrogram(file_path)
            if spectrogram_path and os.path.exists(spectrogram_path):
                self.show_spectrogram(spectrogram_path)
            else:
                self.image_label.setText("未找到对应的语谱图文件！")

            self.label.setText(os.path.basename(file_path))
            self.stop_audio()

    def find_spectrogram(self, audio_path):
        folder_audio = os.path.dirname(audio_path)
        parent_folder = os.path.dirname(folder_audio)
        folder_spectrogram = os.path.join(parent_folder, "spectrogram")
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        spectrogram_path = os.path.join(folder_spectrogram, base_name + ".png")
        return spectrogram_path

    def show_spectrogram(self, image_path):
        pixmap = QPixmap(image_path)
        self.image_label.setPixmap(pixmap.scaled(550, 300, Qt.KeepAspectRatio))

    def play_audio(self):
        if self.audio_data is not None and not self.is_playing:
            start = int(self.position * self.sr)
            sd.play(self.audio_data[start:], self.sr)
            self.is_playing = True
            self.timer.start(200)  # 每0.2秒更新一次进度条

    def pause_audio(self):
        if self.is_playing:
            sd.stop()
            self.is_playing = False
            self.timer.stop()

    def stop_audio(self):
        sd.stop()
        self.position = 0
        self.slider.setValue(0)
        self.is_playing = False
        self.timer.stop()

    def seek_audio(self):
        if self.audio_data is not None:
            self.position = self.slider.value()
            sd.stop()
            self.is_playing = False
            self.play_audio()

    def update_slider(self):
        if self.is_playing:
            self.position += 0.2
            if self.position >= self.duration:
                self.stop_audio()
            else:
                self.slider.setValue(int(self.position))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AudioPlayer()
    window.show()
    sys.exit(app.exec_())