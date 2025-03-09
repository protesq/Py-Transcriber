import sys
import os
import time
import tempfile
import speech_recognition as sr
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QTextEdit, 
                            QFileDialog, QProgressBar, QMessageBox, QComboBox,
                            QSlider, QSpinBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QPixmap, QImage, QIcon
from datetime import datetime
import pyaudio
import wave
import numpy as np

class AudioTranscriptionThread(QThread):
    update_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    
    def __init__(self, device_index, language="tr-TR", record_seconds=2, energy_threshold=300):
        super().__init__()
        self.device_index = device_index
        self.language = language
        self.running = True
        self.recognizer = sr.Recognizer()
        
        # Konuşma tanıma ayarları
        self.recognizer.energy_threshold = energy_threshold  # Ses algılama eşiği
        self.recognizer.dynamic_energy_threshold = True  # Dinamik ses eşiği
        self.recognizer.pause_threshold = 0.5  # Konuşma arasındaki duraklama süresi (daha kısa)
        self.recognizer.phrase_threshold = 0.3  # Cümle algılama eşiği (daha düşük)
        
        # PyAudio nesnesi
        self.p = pyaudio.PyAudio()
        
        # Seçilen cihazın bilgilerini al
        self.selected_device = self.p.get_device_info_by_index(self.device_index)
        
        # Cihazın kanal sayısını kontrol et
        self.max_input_channels = int(self.selected_device['maxInputChannels'])
        
        # Kanal sayısını ayarla (cihazın desteklediği kanal sayısını kullan)
        self.channels = min(2, self.max_input_channels)  # En fazla 2 kanal kullan
        
        # Ses kayıt ayarları
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.rate = 16000
        self.record_seconds = record_seconds  # Daha kısa kayıt süresi
        
        # Önceki transkript parçası
        self.previous_text = ""
        
    def run(self):
        try:
            # Geçici dosya için dizin
            temp_dir = tempfile.gettempdir()
            
            # Sonsuz döngü içinde ses kaydı yap ve transkript et
            while self.running:
                self.progress_signal.emit(10)  # İlerleme: %10
                
                # Geçici WAV dosyası oluştur
                temp_wav = os.path.join(temp_dir, "temp_system_audio.wav")
                
                try:
                    # Ses kaydı yap
                    stream = self.p.open(format=self.format,
                                    channels=self.channels,
                                    rate=self.rate,
                                    input=True,
                                    frames_per_buffer=self.chunk,
                                    input_device_index=self.device_index)
                    
                    self.update_signal.emit("Ses kaydediliyor...")
                    self.progress_signal.emit(30)  # İlerleme: %30
                    
                    frames = []
                    
                    for i in range(0, int(self.rate / self.chunk * self.record_seconds)):
                        if not self.running:
                            break
                            
                        try:
                            data = stream.read(self.chunk, exception_on_overflow=False)
                            frames.append(data)
                        except Exception as e:
                            self.error_signal.emit(f"Okuma hatası: {e}")
                            continue
                    
                    stream.stop_stream()
                    stream.close()
                    
                    self.progress_signal.emit(50)  # İlerleme: %50
                    
                    # WAV dosyasına kaydet
                    wf = wave.open(temp_wav, 'wb')
                    wf.setnchannels(self.channels)
                    wf.setsampwidth(self.p.get_sample_size(self.format))
                    wf.setframerate(self.rate)
                    wf.writeframes(b''.join(frames))
                    wf.close()
                    
                    self.progress_signal.emit(70)  # İlerleme: %70
                    
                    # Transkript için Google Speech Recognition kullan
                    try:
                        with sr.AudioFile(temp_wav) as source:
                            audio = self.recognizer.record(source)
                            text = self.recognizer.recognize_google(audio, language=self.language)
                            
                            # Boş metin kontrolü
                            if not text.strip():
                                continue
                                
                            # Zaman damgası ekle
                            timestamp = datetime.now().strftime("%H:%M:%S")
                            
                            # Önceki metinle birleştir (cümle tamamlama)
                            if self.previous_text and not self.previous_text.endswith(('.', '!', '?')):
                                # Önceki metin bir cümle sonu işaretiyle bitmiyorsa, yeni metinle birleştir
                                combined_text = f"{self.previous_text} {text}"
                                transcript_chunk = f"[{timestamp}] {combined_text}\n\n"
                                self.update_signal.emit(transcript_chunk)
                                self.previous_text = combined_text
                            else:
                                # Yeni bir cümle başlat
                                transcript_chunk = f"[{timestamp}] {text}\n\n"
                                self.update_signal.emit(transcript_chunk)
                                self.previous_text = text
                            
                    except sr.UnknownValueError:
                        # Konuşma algılanamadı, sessiz bir bölüm olabilir
                        pass
                    except sr.RequestError as e:
                        self.error_signal.emit(f"API hatası: {e}")
                    except Exception as e:
                        self.error_signal.emit(f"Transkript hatası: {e}")
                    
                    self.progress_signal.emit(90)  # İlerleme: %90
                    
                    # Geçici dosyayı temizle
                    try:
                        os.remove(temp_wav)
                    except:
                        pass
                        
                except Exception as e:
                    self.error_signal.emit(f"Kayıt hatası: {e}")
                    time.sleep(0.5)  # Hata durumunda biraz bekle
                
                self.progress_signal.emit(100)  # İlerleme: %100
                
                # Çok kısa bir bekleme (CPU kullanımını azaltmak için)
                time.sleep(0.1)
                
        except Exception as e:
            self.error_signal.emit(f"Kritik hata: {e}")
        finally:
            # PyAudio nesnesini temizle
            if hasattr(self, 'p'):
                self.p.terminate()
    
    def stop(self):
        self.running = False


class AudioTranscriberApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistem Sesi Transkript Uygulaması")
        self.setGeometry(100, 100, 800, 600)
        
        self.transcription_thread = None
        self.audio_devices = self.get_audio_devices()
        
        # Ayarlar
        self.record_seconds = 2  # Varsayılan kayıt süresi
        self.energy_threshold = 300  # Varsayılan ses algılama eşiği
        
        self.init_ui()
        
    def get_audio_devices(self):
        """Kullanılabilir ses cihazlarını listeler"""
        devices = []
        
        try:
            p = pyaudio.PyAudio()
            info = p.get_host_api_info_by_index(0)
            numdevices = info.get('deviceCount')
            
            for i in range(0, numdevices):
                device_info = p.get_device_info_by_index(i)
                # Sadece giriş kanalı olan cihazları ekle
                if device_info.get('maxInputChannels') > 0:
                    devices.append((i, device_info['name'], device_info['maxInputChannels']))
            
            p.terminate()
            
        except Exception as e:
            print(f"Ses cihazları listelenirken hata oluştu: {e}")
            
        return devices
        
    def init_ui(self):
        # Ana widget ve layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Üst panel - Kontroller
        top_panel = QVBoxLayout()
        
        # Cihaz seçimi
        device_group = QHBoxLayout()
        device_label = QLabel("Ses Kaynağı:")
        self.device_combo = QComboBox()
        
        # Cihazları ekle
        for idx, name, channels in self.audio_devices:
            self.device_combo.addItem(f"{name} (Kanallar: {channels})", idx)
        
        device_group.addWidget(device_label)
        device_group.addWidget(self.device_combo, 1)
        
        # Dil seçimi
        lang_group = QHBoxLayout()
        lang_label = QLabel("Dil:")
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("Türkçe", "tr-TR")
        self.lang_combo.addItem("İngilizce", "en-US")
        self.lang_combo.addItem("Almanca", "de-DE")
        self.lang_combo.addItem("Fransızca", "fr-FR")
        self.lang_combo.addItem("İspanyolca", "es-ES")
        
        lang_group.addWidget(lang_label)
        lang_group.addWidget(self.lang_combo, 1)
        
        # Kayıt süresi ayarı
        record_time_group = QHBoxLayout()
        record_time_label = QLabel("Kayıt Süresi (sn):")
        self.record_time_spin = QSpinBox()
        self.record_time_spin.setRange(1, 30)
        self.record_time_spin.setValue(self.record_seconds)
        self.record_time_spin.valueChanged.connect(self.update_record_seconds)
        
        record_time_group.addWidget(record_time_label)
        record_time_group.addWidget(self.record_time_spin)
        
        # Ses algılama eşiği ayarı
        threshold_group = QHBoxLayout()
        threshold_label = QLabel("Ses Algılama Eşiği:")
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setRange(100, 1000)
        self.threshold_slider.setValue(self.energy_threshold)
        self.threshold_slider.valueChanged.connect(self.update_energy_threshold)
        
        threshold_group.addWidget(threshold_label)
        threshold_group.addWidget(self.threshold_slider, 1)
        
        # Butonlar
        button_group = QHBoxLayout()
        
        self.start_btn = QPushButton("Transkript Başlat")
        self.start_btn.clicked.connect(self.start_transcription)
        
        self.stop_btn = QPushButton("Durdur")
        self.stop_btn.clicked.connect(self.stop_transcription)
        self.stop_btn.setEnabled(False)
        
        self.save_btn = QPushButton("Transkripti Kaydet")
        self.save_btn.clicked.connect(self.save_transcript)
        self.save_btn.setEnabled(False)
        
        self.clear_btn = QPushButton("Temizle")
        self.clear_btn.clicked.connect(self.clear_transcript)
        
        button_group.addWidget(self.start_btn)
        button_group.addWidget(self.stop_btn)
        button_group.addWidget(self.save_btn)
        button_group.addWidget(self.clear_btn)
        
        # Üst paneli düzenle
        top_panel.addLayout(device_group)
        top_panel.addLayout(lang_group)
        top_panel.addLayout(record_time_group)
        top_panel.addLayout(threshold_group)
        top_panel.addLayout(button_group)
        
        main_layout.addLayout(top_panel)
        
        # İlerleme çubuğu
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)
        
        # Transkript metni
        self.transcript_text = QTextEdit()
        self.transcript_text.setReadOnly(True)
        self.transcript_text.setPlaceholderText("Transkript burada görüntülenecek...")
        main_layout.addWidget(self.transcript_text)
        
        # Durum çubuğu
        self.statusBar().showMessage("Hazır")
        
        # Cihaz kontrolü
        if not self.audio_devices:
            self.show_no_devices_warning()
    
    def update_record_seconds(self, value):
        """Kayıt süresini güncelle"""
        self.record_seconds = value
    
    def update_energy_threshold(self, value):
        """Ses algılama eşiğini güncelle"""
        self.energy_threshold = value
    
    def show_no_devices_warning(self):
        """Ses cihazı bulunamadığında uyarı göster"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Uyarı")
        msg.setText("Kullanılabilir ses cihazı bulunamadı.")
        msg.setInformativeText("Lütfen bir mikrofon veya ses giriş cihazı bağlayın.")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    
    def start_transcription(self):
        # Cihaz kontrolü
        if self.device_combo.count() == 0:
            QMessageBox.warning(self, "Uyarı", "Kullanılabilir ses cihazı bulunamadı.")
            return
            
        # Seçilen cihaz ve dil
        selected_device = self.device_combo.currentData()
        selected_language = self.lang_combo.currentData()
        
        # Transkript thread'ini başlat
        self.transcription_thread = AudioTranscriptionThread(
            device_index=selected_device,
            language=selected_language,
            record_seconds=self.record_seconds,
            energy_threshold=self.energy_threshold
        )
        self.transcription_thread.update_signal.connect(self.update_transcript)
        self.transcription_thread.error_signal.connect(self.show_error)
        self.transcription_thread.progress_signal.connect(self.update_progress)
        self.transcription_thread.start()
        
        # UI güncellemeleri
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.save_btn.setEnabled(True)
        self.device_combo.setEnabled(False)
        self.lang_combo.setEnabled(False)
        self.record_time_spin.setEnabled(False)
        self.threshold_slider.setEnabled(False)
        self.statusBar().showMessage("Transkript işlemi başladı...")
    
    def stop_transcription(self):
        if self.transcription_thread and self.transcription_thread.isRunning():
            self.transcription_thread.stop()
            self.transcription_thread.wait()
        
        # UI güncellemeleri
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.device_combo.setEnabled(True)
        self.lang_combo.setEnabled(True)
        self.record_time_spin.setEnabled(True)
        self.threshold_slider.setEnabled(True)
        self.statusBar().showMessage("Transkript işlemi durduruldu")
    
    def update_transcript(self, text):
        self.transcript_text.append(text)
        # Otomatik kaydırma
        cursor = self.transcript_text.textCursor()
        cursor.movePosition(cursor.End)
        self.transcript_text.setTextCursor(cursor)
    
    def update_progress(self, value):
        self.progress_bar.setValue(value)
    
    def show_error(self, error_message):
        self.statusBar().showMessage(error_message)
        QMessageBox.warning(self, "Hata", error_message)
    
    def save_transcript(self):
        if not self.transcript_text.toPlainText():
            QMessageBox.warning(self, "Uyarı", "Kaydedilecek transkript yok!")
            return
            
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(
            self, "Transkripti Kaydet", "", "Metin Dosyaları (*.txt);;Tüm Dosyalar (*)"
        )
        
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.transcript_text.toPlainText())
            self.statusBar().showMessage(f"Transkript kaydedildi: {file_path}")
    
    def clear_transcript(self):
        self.transcript_text.clear()
        self.statusBar().showMessage("Transkript temizlendi")
    
    def closeEvent(self, event):
        if self.transcription_thread and self.transcription_thread.isRunning():
            self.transcription_thread.stop()
            self.transcription_thread.wait()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AudioTranscriberApp()
    window.show()
    sys.exit(app.exec_()) 