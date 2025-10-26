import sys
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import io

class AudioPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("音频播放器 + 语谱图")
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
            self.audio_data, self.sr = librosa.load(file_path, sr=None)
            self.show_spectrogram(file_path)
    
    def show_spectrogram(self, file_path):
        plt.figure(figsize=(6, 3))
        D = librosa.amplitude_to_db(np.abs(librosa.stft(self.audio_data)), ref=np.max)
        librosa.display.specshow(D, sr=self.sr, x_axis='time', y_axis='log')
        plt.colorbar(format='%+2.0f dB')
        plt.title("语谱图")
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        
        pixmap = QPixmap()
        pixmap.loadFromData(buf.read())
        self.label.setPixmap(pixmap.scaled(550, 300, Qt.KeepAspectRatio))
    
    def play_audio(self):
        if self.audio_data is not None:
            sd.play(self.audio_data, self.sr)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AudioPlayer()
    window.show()
    sys.exit(app.exec_())