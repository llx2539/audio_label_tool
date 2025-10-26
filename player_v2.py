import sys
import os
import librosa
import sounddevice as sd
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class AudioPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("音频播放器 + 语谱图查看")
        self.setGeometry(300, 200, 600, 500)

        self.layout = QVBoxLayout()
        self.label = QLabel("请选择一个音频文件")
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)

        self.btn_open = QPushButton("打开音频")
        self.btn_open.clicked.connect(self.open_file)
        self.layout.addWidget(self.btn_open)

        self.btn_play = QPushButton("播放音频")
        self.btn_play.clicked.connect(self.play_audio)
        self.layout.addWidget(self.btn_play)

        self.setLayout(self.layout)
        self.audio_data = None
        self.sr = None

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择音频文件", "", "音频文件 (*.wav *.mp3)")
        if file_path:
            # 读取音频
            self.audio_data, self.sr = librosa.load(file_path, sr=None)

            # 自动查找对应的语谱图文件
            spectrogram_path = self.find_spectrogram(file_path)
            if spectrogram_path and os.path.exists(spectrogram_path):
                self.show_spectrogram(spectrogram_path)
            else:
                self.label.setText("未找到对应的语谱图文件！")

    def find_spectrogram(self, audio_path):
        """
        通过音频路径推测语谱图路径
        例如 audio/song1.wav → spectrogram/song1.png
        """
        folder_audio = os.path.dirname(audio_path)
        parent_folder = os.path.dirname(folder_audio)
        folder_spectrogram = os.path.join(parent_folder, "spectrogram")

        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        spectrogram_path = os.path.join(folder_spectrogram, base_name + ".png")
        return spectrogram_path

    def show_spectrogram(self, image_path):
        pixmap = QPixmap(image_path)
        self.label.setPixmap(pixmap.scaled(550, 300, Qt.KeepAspectRatio))

    def play_audio(self):
        if self.audio_data is not None:
            sd.play(self.audio_data, self.sr)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AudioPlayer()
    window.show()
    sys.exit(app.exec_())