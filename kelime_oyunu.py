import sys
import random
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                           QMessageBox, QStackedWidget, QFrame, QScrollArea)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QValueAxis, QBarCategoryAxis

class GameStats:
    def __init__(self):
        self.correct_answers = []
        self.wrong_answers = []
        self.question_history = []
        self.time_per_question = []
        self.start_time = None
        
    def add_result(self, question, answer, user_answer, time_taken, is_correct):
        self.question_history.append({
            'question': question,
            'correct_answer': answer,
            'user_answer': user_answer,
            'time_taken': time_taken,
            'is_correct': is_correct
        })
        if is_correct:
            self.correct_answers.append(question)
        else:
            self.wrong_answers.append(question)
        self.time_per_question.append(time_taken)

    def get_summary(self):
        total_questions = len(self.question_history)
        if total_questions == 0:
            return "Henüz soru cevaplanmamış."
            
        accuracy = (len(self.correct_answers) / total_questions) * 100
        avg_time = sum(self.time_per_question) / len(self.time_per_question)
        
        return {
            'total_questions': total_questions,
            'correct_count': len(self.correct_answers),
            'wrong_count': len(self.wrong_answers),
            'accuracy': accuracy,
            'average_time': avg_time,
            'history': self.question_history
        }

class WordGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.stats = GameStats()
        self.initUI()
        self.initGame()
        
    def initGame(self):
        self.questions = {
            "Gökyüzünden yağan su damlacıkları": "yağmur",
            "Haftanın ilk günü": "pazartesi",
            "İnsanların yaşadığı gezegen": "dünya",
            "Gece gökyüzünde parlayan cisimler": "yıldız",
            "Denizde yaşayan omurgalı hayvan": "balık",
            "Yazın en sıcak ay": "temmuz",
            "Okullarda ders veren kişi": "öğretmen",
            "Kırtasiyede yazı yazmak için alınan araç": "kalem",
            "Evlerin üstünü örten yapı": "çatı",
            "İnsanların dinlenmek için kullandığı mobilya": "koltuk"
        }
        self.current_score = 100
        self.wrong_rights = 3
        self.joker_rights = 2
        self.pass_rights = 2
        self.time_left = 30
        self.question_start_time = None
        self.current_question = None
        self.current_answer = None
        self.question_history = []
        self.current_question_index = -1
        self.questions_list = list(self.questions.items())
        self.next_question()

    def initUI(self):
        self.setWindowTitle('Gelişmiş Kelime Oyunu')
        self.setGeometry(100, 100, 1000, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f5ff;
            }
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                min-width: 120px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #4a90e2;
                border-radius: 5px;
                font-size: 14px;
            }
            QLabel {
                color: #2c3e50;
            }
        """)

        # Ana widget ve layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        # Üst bilgi paneli
        self.create_info_panel()
        
        # Oyun ve sonuç ekranları için stacked widget
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)
        
        # Oyun ekranı
        self.game_widget = QWidget()
        self.game_layout = QVBoxLayout()
        self.game_widget.setLayout(self.game_layout)
        
        # Soru alanı
        self.create_question_area()
        
        # Cevap girişi
        self.create_answer_input()
        
        # Butonlar
        self.create_game_buttons()
        
        # Sonuç ekranı
        self.result_widget = QWidget()
        self.result_layout = QVBoxLayout()
        self.result_widget.setLayout(self.result_layout)
        
        # Stacked widget'a ekranları ekle
        self.stacked_widget.addWidget(self.game_widget)
        self.stacked_widget.addWidget(self.result_widget)
        
        # Zamanlayıcı
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

    def create_info_panel(self):
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        info_layout = QHBoxLayout()
        info_frame.setLayout(info_layout)
        
        self.score_label = QLabel(f'Puan: {100}')
        self.lives_label = QLabel(f'Kalan Hak: {3}')
        self.time_label = QLabel('Süre: 30')
        
        for label in [self.score_label, self.lives_label, self.time_label]:
            label.setFont(QFont('Arial', 12))
            label.setStyleSheet("padding: 5px;")
            info_layout.addWidget(label)
            
        self.main_layout.addWidget(info_frame)

    def create_question_area(self):
        question_frame = QFrame()
        question_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
                margin: 10px;
            }
        """)
        question_layout = QVBoxLayout()
        question_frame.setLayout(question_layout)
        
        self.question_label = QLabel()
        self.question_label.setFont(QFont('Arial', 16))
        self.question_label.setWordWrap(True)
        self.question_label.setAlignment(Qt.AlignCenter)
        self.question_label.setStyleSheet("color: #2c3e50;")
        
        question_layout.addWidget(self.question_label)
        self.game_layout.addWidget(question_frame)

    def create_answer_input(self):
        self.answer_input = QLineEdit()
        self.answer_input.setFont(QFont('Arial', 14))
        self.answer_input.setPlaceholderText("Cevabınızı buraya yazın...")
        self.answer_input.returnPressed.connect(self.check_answer)
        self.game_layout.addWidget(self.answer_input)

    def create_game_buttons(self):
        buttons_layout = QHBoxLayout()
        
        self.submit_btn = QPushButton('Cevapla')
        self.joker_btn = QPushButton('Joker Kullan')
        self.pass_btn = QPushButton('Pas Geç')
        self.previous_btn = QPushButton('Önceki Soru')
        self.quit_btn = QPushButton('Oyunu Bitir')

        for btn in [self.submit_btn, self.joker_btn, self.pass_btn, 
                   self.previous_btn, self.quit_btn]:
            btn.setFont(QFont('Arial', 12))
            buttons_layout.addWidget(btn)

        self.submit_btn.clicked.connect(self.check_answer)
        self.joker_btn.clicked.connect(self.use_joker)
        self.pass_btn.clicked.connect(self.pass_question)
        self.previous_btn.clicked.connect(self.previous_question)
        self.quit_btn.clicked.connect(self.quit_game)

        self.game_layout.addLayout(buttons_layout)

    def create_results_view(self):
        # Önce mevcut layout'taki tüm widget'ları temizle
        while self.result_layout.count():
            item = self.result_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        summary = self.stats.get_summary()
        
        # Başlık
        title = QLabel("Oyun Sonuç Raporu")
        title.setFont(QFont('Arial', 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        self.result_layout.addWidget(title)
        
        # İstatistikler
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
                margin: 10px;
            }
        """)
        stats_layout = QVBoxLayout()
        stats_frame.setLayout(stats_layout)
        
        stats_text = f"""
        Toplam Soru: {summary['total_questions']}
        Doğru Cevap: {summary['correct_count']}
        Yanlış Cevap: {summary['wrong_count']}
        Başarı Oranı: {summary['accuracy']:.1f}%
        Ortalama Süre: {summary['average_time']:.1f} saniye
        Final Puanı: {self.current_score}
        """
        
        stats_label = QLabel(stats_text)
        stats_label.setFont(QFont('Arial', 12))
        stats_layout.addWidget(stats_label)
        
        self.result_layout.addWidget(stats_frame)
        
        try:
            # Grafik
            self.create_performance_chart(summary)
        except Exception as e:
            print(f"Grafik oluşturulurken hata: {str(e)}")
            # Grafik oluşturulamazsa basit bir metin göster
            error_label = QLabel("Grafik gösterimi şu anda kullanılamıyor.")
            error_label.setAlignment(Qt.AlignCenter)
            self.result_layout.addWidget(error_label)
        
        # Soru geçmişi
        history_scroll = QScrollArea()
        history_widget = QWidget()
        history_layout = QVBoxLayout()
        
        for i, entry in enumerate(summary['history'], 1):
            entry_frame = QFrame()
            entry_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {'#e8f5e9' if entry['is_correct'] else '#ffebee'};
                    border-radius: 5px;
                    padding: 10px;
                    margin: 5px;
                }}
            """)
            entry_layout = QVBoxLayout()
            
            entry_text = f"""
            Soru {i}: {entry['question']}
            Doğru Cevap: {entry['correct_answer']}
            Sizin Cevabınız: {entry['user_answer']}
            Süre: {entry['time_taken']:.1f} saniye
            """
            
            entry_label = QLabel(entry_text)
            entry_label.setFont(QFont('Arial', 11))
            entry_layout.addWidget(entry_label)
            
            entry_frame.setLayout(entry_layout)
            history_layout.addWidget(entry_frame)
        
        history_widget.setLayout(history_layout)
        history_scroll.setWidget(history_widget)
        history_scroll.setWidgetResizable(True)
        
        self.result_layout.addWidget(history_scroll)
        
        # Yeniden oyna butonu
        replay_btn = QPushButton("Yeniden Oyna")
        replay_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        replay_btn.clicked.connect(self.restart_game)
        self.result_layout.addWidget(replay_btn)
        
        # Çıkış butonu
        quit_btn = QPushButton("Oyundan Çık")
        quit_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        quit_btn.clicked.connect(self.close)
        self.result_layout.addWidget(quit_btn)

    def create_performance_chart(self, summary):
        # Grafik oluştur
        chart = QChart()
        
        # Veri setleri
        correct_set = QBarSet("Doğru")
        wrong_set = QBarSet("Yanlış")
        
        correct_set.append(summary['correct_count'])
        wrong_set.append(summary['wrong_count'])
        
        # Seri oluştur
        series = QBarSeries()
        series.append(correct_set)
        series.append(wrong_set)
        
        chart.addSeries(series)
        chart.setTitle("Performans Özeti")
        
        # Eksenleri ayarla
        categories = ["Cevaplar"]
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setRange(0, max(summary['correct_count'], summary['wrong_count']) + 2)
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        
        # Grafik görünümü
        chart_view = QChartView(chart)
        from PyQt5.QtGui import QPainter
        chart_view.setRenderHint(QPainter.Antialiasing)  # Düzeltme burada
        chart_view.setMinimumHeight(300)
        
        self.result_layout.addWidget(chart_view)

    def show_final_results(self):
        if isinstance(self.stats.get_summary(), str):
            # Eğer özet bir string ise (henüz soru cevaplanmamışsa)
            QMessageBox.information(self, "Oyun Bitti", "Henüz hiç soru cevaplanmamış.")
            return
            
        self.timer.stop()
        self.create_results_view()
        self.stacked_widget.setCurrentWidget(self.result_widget)

    def next_question(self):
        if not self.questions_list:
            self.show_final_results()
            return

        self.current_question_index += 1
        if self.current_question_index >= len(self.questions_list):
            self.show_final_results()
            return

        question_tuple = self.questions_list[self.current_question_index]
        self.current_question = question_tuple[0]
        self.current_answer = question_tuple[1]
        self.question_label.setText(self.current_question)
        self.answer_input.clear()
        self.time_left = 30
        self.question_start_time = datetime.now()
        self.update_labels()
    def update_labels(self):
        """
        Oyun ekranındaki etiketleri günceller (puan, kalan hak ve süre)
        """
        # Puan, can ve süre bilgilerini güncelle
        self.score_label.setText(f'Puan: {self.current_score}')
        self.lives_label.setText(f'Kalan Hak: {self.wrong_rights}')
        self.time_label.setText(f'Süre: {self.time_left}')
        
        # Joker ve pas butonlarını güncelle
        self.joker_btn.setEnabled(self.joker_rights > 0)
        self.pass_btn.setEnabled(self.pass_rights > 0)
        
        # Önceki soru butonunu güncelle
        self.previous_btn.setEnabled(self.current_question_index > 0)
        
        # Süre azaldıkça renk değiştirme
        if self.time_left <= 10:
            self.time_label.setStyleSheet("color: red; font-weight: bold;")
        elif self.time_left <= 20:
            self.time_label.setStyleSheet("color: orange;")
        else:
            self.time_label.setStyleSheet("color: black;")

    def previous_question(self):
            if self.current_question_index > 0:
                self.current_question_index -= 1
                question_tuple = self.questions_list[self.current_question_index]
                self.current_question = question_tuple[0]
                self.current_answer = question_tuple[1]
                self.question_label.setText(self.current_question)
                self.answer_input.clear()
                self.time_left = 30
                self.question_start_time = datetime.now()
                self.update_labels()
            else:
                QMessageBox.information(self, "Bilgi", "Bu ilk soru!")

    def check_answer(self):
        if not self.question_start_time:
            return
            
        time_taken = (datetime.now() - self.question_start_time).total_seconds()
        user_answer = self.answer_input.text().lower().strip()
        
        is_correct = user_answer == self.current_answer
        
        self.stats.add_result(
            self.current_question,
            self.current_answer,
            user_answer,
            time_taken,
            is_correct
        )
        
        if is_correct:
            self.current_score += 10
            bonus = max(0, int((30 - time_taken) / 2))  # Hızlı cevap bonusu
            self.current_score += bonus
            
            QMessageBox.information(self, "Doğru!", 
                f"Tebrikler! Doğru cevap!\nHızlı cevap bonusu: +{bonus} puan")
            self.next_question()
        else:
            self.wrong_rights -= 1
            self.current_score -= 10
            
            if self.wrong_rights <= 0:
                self.game_over("Yanlış haklarınız bitti!")
            else:
                feedback = f"Yanlış cevap!\nKalan hakkınız: {self.wrong_rights}"
                if len(user_answer) != len(self.current_answer):
                    feedback += f"\nİpucu: Doğru cevap {len(self.current_answer)} harfli"
                QMessageBox.warning(self, "Yanlış!", feedback)
                
        self.update_labels()
    def use_joker(self):
        if self.joker_rights > 0:
            self.joker_rights -= 1
            self.current_score -= 5
            
            # Gelişmiş ipucu sistemi
            answer = self.current_answer
            hint_type = random.choice(['first_last', 'vowels', 'length_pattern'])
            
            if hint_type == 'first_last':
                hint = f"İpucu: Kelime '{answer[0]}' harfi ile başlayıp '{answer[-1]}' harfi ile bitiyor"
            elif hint_type == 'vowels':
                vowels = [c for c in answer if c in 'aeıioöuü']
                hint = f"İpucu: Kelimede şu sesli harfler var: {', '.join(vowels)}"
            else:  # length_pattern
                pattern = ['_' if i not in [0, len(answer)-1] else answer[i] 
                          for i in range(len(answer))]
                hint = f"İpucu: Kelime şablonu: {' '.join(pattern)}"
            
            QMessageBox.information(self, "Joker", hint)
            self.update_labels()
        else:
            QMessageBox.warning(self, "Uyarı", "Joker hakkınız kalmadı!")

    def pass_question(self):
        if self.pass_rights > 0:
            self.pass_rights -= 1
            self.current_score -= 5
            
            # Geçilen soruyu kaydedip sonra tekrar sorabilmek için
            missed_question = {
                'question': self.current_question,
                'answer': self.current_answer
            }
            self.stats.add_result(
                self.current_question,
                self.current_answer,
                "Pas Geçildi",
                0,
                False
            )
            
            self.next_question()
        else:
            QMessageBox.warning(self, "Uyarı", "Pas hakkınız kalmadı!")

    def update_timer(self):
        self.time_left -= 1
        self.time_label.setText(f'Süre: {self.time_left}')
        
        # Süre azaldıkça renk değiştirme
        if self.time_left <= 10:
            self.time_label.setStyleSheet("color: red; font-weight: bold;")
        elif self.time_left <= 20:
            self.time_label.setStyleSheet("color: orange;")
        else:
            self.time_label.setStyleSheet("color: black;")
            
        if self.time_left <= 0:
            self.wrong_rights -= 1
            self.current_score -= 10
            
            self.stats.add_result(
                self.current_question,
                self.current_answer,
                "Süre Doldu",
                30,  # Maksimum süre
                False
            )
            
            if self.wrong_rights <= 0:
                self.game_over("Süre bitti ve yanlış haklarınız tükendi!")
            else:
                QMessageBox.warning(self, "Süre Bitti!", 
                    f"Süre doldu! Doğru cevap: {self.current_answer}\nKalan hakkınız: {self.wrong_rights}")
                self.next_question()

    # def show_final_results(self):
    #     self.timer.stop()
    #     self.create_results_view()
    #     self.stacked_widget.setCurrentWidget(self.result_widget)

    def game_over(self, message):
        self.timer.stop()
        self.show_final_results()
        
        QMessageBox.information(self, "Oyun Bitti", 
            f"{message}\nToplam puanınız: {self.current_score}")
            
        replay = QMessageBox.question(self, "Yeniden Oyna", 
            "Tekrar oynamak ister misiniz?",
            QMessageBox.Yes | QMessageBox.No)
            
        if replay == QMessageBox.Yes:
            self.restart_game()
        else:
            self.close()

    def restart_game(self):
        self.stats = GameStats()
        self.stacked_widget.setCurrentWidget(self.game_widget)
        self.initGame()
        self.timer.start()

    def quit_game(self):
        reply = QMessageBox.question(self, "Oyunu Bitir", 
            "Oyunu bitirmek istediğinizden emin misiniz?",
            QMessageBox.Yes | QMessageBox.No)
            
        if reply == QMessageBox.Yes:
            self.game_over("Oyunu sonlandırdınız!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Uygulama stil ayarları
    app.setStyle('Fusion')
    
    # Ana pencere renk paleti
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(240, 245, 255))
    palette.setColor(QPalette.WindowText, QColor(44, 62, 80))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
    palette.setColor(QPalette.Button, QColor(74, 144, 226))
    palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    game = WordGame()
    game.show()
    sys.exit(app.exec_())