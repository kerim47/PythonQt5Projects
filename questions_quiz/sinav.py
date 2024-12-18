from PyQt5.QtWidgets import QTextBrowser
import sys
import random
from datetime import datetime
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import (
    QDialog,
    QMainWindow,
    QScrollArea,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QLineEdit,
    QMessageBox,
    QButtonGroup,
    QGroupBox,
)
from PyQt5.QtCore import Qt, QTimer
from python_quiz_db import PythonQuizDatabase

class ExamApp(QMainWindow):
    def __init__(self):
        self.pythonQuizDatabase = PythonQuizDatabase()
        super().__init__()
        self.setWindowTitle("Python Sınavı")
        self.setGeometry(100, 100, 800, 600)

        # Sınav verileri
        self.current_question = 0
        self.score = 0
        self.highest_score = 0
        self.answers = {}
        self.remaining_time = 60  # Her soru için 60 saniye
        self.total_time = 30 * 60  # Toplam 30 dakika
        self.joker_used = False  # Joker kullanım durumu
        self.test_questions = self.pythonQuizDatabase.get_random_questions('test_questions')
        self.bonus_questions = self.pythonQuizDatabase.get_random_questions('bonus_questions')
        self.open_questions = self.pythonQuizDatabase.get_random_questions('open_questions')

        self.initialize_questions()
        self.init_ui()

    def initialize_questions(self):
        # Tüm soruları karıştır
        self.all_questions = self.test_questions + self.open_questions
        print(len(self.all_questions))
        random.shuffle(self.all_questions)
        # self.all_questions.append(self.bonus_question[0])  # Bonus soruyu sona ekle

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout()  # Merkez widget için layout oluştur
        self.central_widget.setLayout(self.main_layout)

        # Başlangıç ekranı
        self.init_welcome_screen()

    def init_welcome_screen(self):
        self.welcome_widget = QWidget()
        self.welcome_widget.setStyleSheet("""
            background-color: #f0f4f8;
            border-radius: 10px;
            padding: 20px;
        """)

        welcome_layout = QVBoxLayout()

        # Başlık
        title_label = QLabel("Python Sınavına Hoş Geldiniz")
        title_label.setAlignment(Qt.AlignCenter)  # Doğru kullanım
        title_label.setStyleSheet("font-size: 24px; margin: 20px;")

        # Kullanıcı bilgileri
        info_group = QGroupBox("Öğrenci Bilgileri")
        info_layout = QVBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ad Soyad")
        self.student_id = QLineEdit()
        self.student_id.setPlaceholderText("Öğrenci No")
        self.department = QLineEdit()
        self.department.setPlaceholderText("Bölüm")

        info_layout.addWidget(self.name_input)
        info_layout.addWidget(self.student_id)
        info_layout.addWidget(self.department)

        info_group.setLayout(info_layout)

        # En yüksek skor
        score_label = QLabel(f"En Yüksek Skor: {self.highest_score}")
        score_label.setAlignment(Qt.AlignCenter)

        # Başlat butonu
        start_button = QPushButton("Sınavı Başlat")
        start_button.clicked.connect(self.start_exam)
        # Butonlar için stil
        start_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 8px;
                padding: 12px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)

        welcome_layout.addWidget(title_label)
        welcome_layout.addWidget(info_group)
        welcome_layout.addWidget(score_label)
        welcome_layout.addWidget(start_button)

        self.welcome_widget.setLayout(welcome_layout)
        self.main_layout.addWidget(self.welcome_widget)

    def finish_exam(self):
        self.timer.stop()
        self.question_timer.stop()
        self.save_current_answer()

        # Eğer son soruya gelindiğinde otomatik sonuç ekranı göster

        if self.current_question == len(self.all_questions) - 1:
            self.show_results()
            return

        # Sonuç ekranını gösterme onayı
        msg = QMessageBox()
        msg.setWindowTitle("Sınavı Bitir")
        msg.setText("Sınavı bitirmek istediğinize emin misiniz?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        if msg.exec_() == QMessageBox.Yes:
            self.show_results()
        else:
            self.timer.start()
            self.question_timer.start()

    def start_exam(self):
        # Kullanıcı bilgilerini kontrol et
        if not all([
            self.name_input.text(),
            self.student_id.text(),
            self.department.text(),
        ]):
            QMessageBox.warning(self, "Hata", "Lütfen tüm bilgileri doldurun!")
            return

        self.welcome_widget.hide()
        self.init_exam_screen()

    def init_exam_screen(self):
        self.exam_widget = QWidget()
        exam_layout = QVBoxLayout()

        # Üst bilgi çubuğu
        info_layout = QHBoxLayout()
        self.time_label = QLabel(
            f"Kalan Süre: {self.total_time // 60}:{self.total_time % 60:02d}"
        )
        self.question_time_label = QLabel(f"Soru Süresi: {self.remaining_time}")
        info_layout.addWidget(self.time_label)
        info_layout.addWidget(self.question_time_label)

        # Soru alanı
        self.question_label = QLabel()
        self.question_label.setWordWrap(True)

        # Cevap alanı
        self.answer_group = QGroupBox()
        self.answer_layout = QVBoxLayout()
        self.answer_group.setLayout(self.answer_layout)

        # Kontrol butonları
        control_layout = QHBoxLayout()
        self.prev_button = QPushButton("Önceki")
        self.next_button = QPushButton("Sonraki")
        self.joker_button = QPushButton("Joker")
        self.pass_button = QPushButton("Pas")
        self.finish_button = QPushButton("Bitir")

        self.prev_button.clicked.connect(self.prev_question)
        self.next_button.clicked.connect(self.next_question)
        self.joker_button.clicked.connect(self.use_joker)
        self.pass_button.clicked.connect(self.pass_question)
        self.finish_button.clicked.connect(self.finish_exam)

        control_layout.addWidget(self.prev_button)
        control_layout.addWidget(self.next_button)
        control_layout.addWidget(self.joker_button)
        control_layout.addWidget(self.pass_button)
        control_layout.addWidget(self.finish_button)

        exam_layout.addLayout(info_layout)
        exam_layout.addWidget(self.question_label)
        exam_layout.addWidget(self.answer_group)
        exam_layout.addLayout(control_layout)

        self.exam_widget.setLayout(exam_layout)
        self.main_layout.addWidget(self.exam_widget)

        # Zamanlayıcıları başlat
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        self.question_timer = QTimer()
        self.question_timer.timeout.connect(self.update_question_time)
        self.question_timer.start(1000)

        self.show_question()

    def show_question(self):
        question_data = self.all_questions[self.current_question]
        self.question_label.setText(
            f"Soru {self.current_question + 1}: {question_data['question']}"
        )

        # Önceki cevap seçeneklerini temizle
        for i in reversed(range(self.answer_layout.count())):
            self.answer_layout.itemAt(i).widget().setParent(None)

        if "options" in question_data:  # Test sorusu
            self.button_group = QButtonGroup()
            for i, option in enumerate(question_data["options"]):
                radio = QRadioButton(option)
                self.answer_layout.addWidget(radio)
                self.button_group.addButton(radio, i)

                # Önceden verilmiş cevap varsa işaretle
                if self.current_question in self.answers:
                    if option == self.answers[self.current_question]:
                        radio.setChecked(True)
        else:  # Açık uçlu soru
            self.answer_input = QLineEdit()
            if self.current_question in self.answers:
                self.answer_input.setText(self.answers[self.current_question])
            self.answer_layout.addWidget(self.answer_input)

        # Soru süresini sıfırla
        self.remaining_time = 60

    def update_time(self):
        self.total_time -= 1
        if self.total_time <= 0:
            self.finish_exam()
        self.time_label.setText(
            f"Kalan Süre: {self.total_time // 60}:{self.total_time % 60:02d}"
        )

    def update_question_time(self):
        self.remaining_time -= 1
        if self.remaining_time <= 0:
            self.next_question()
        self.question_time_label.setText(f"Soru Süresi: {self.remaining_time}")

    def save_current_answer(self):
        question_data = self.all_questions[self.current_question]
        if "options" in question_data:  # Test sorusu
            selected_button = self.button_group.checkedButton()
            if selected_button:
                self.answers[self.current_question] = selected_button.text()
        else:  # Açık uçlu soru
            answer_text = self.answer_input.text().strip()
            if answer_text:
                self.answers[self.current_question] = answer_text

    def prev_question(self):
        self.save_current_answer()
        if self.current_question > 0:
            self.current_question -= 1
            self.show_question()

    def next_question(self):
        self.save_current_answer()
        if self.current_question < len(self.all_questions) - 1:
            self.current_question += 1
            self.show_question()

    def use_joker(self):
        question_data = self.all_questions[self.current_question]
        if "options" in question_data:  # Sadece test sorularında joker kullanılabilir
            correct = question_data["correct"]
            # İki yanlış seçeneği kaldır
            options_to_remove = [
                opt for opt in question_data["options"] if opt != correct
            ]
            random.shuffle(options_to_remove)
            for i, option in enumerate(question_data["options"]):
                if option in options_to_remove[:2]:
                    self.button_group.button(i).setEnabled(False)
        self.joker_button.setEnabled(False)

    def pass_question(self):
        self.next_question()

    def show_results(self):
        # Sonuç penceresi oluştur
        results_dialog = QDialog(self)
        results_dialog.setWindowTitle("Sınav Sonuçları")
        results_dialog.setGeometry(100, 100, 1200, 800)  # Daha geniş bir pencere
        
        # Ana layout
        main_layout = QVBoxLayout()
        results_dialog.setLayout(main_layout)

        # Üst başlık çubuğu
        header_widget = QWidget()
        header_layout = QHBoxLayout()
        header_widget.setLayout(header_layout)
        
        # Başlık etiketi
        title_label = QLabel("Sınav Sonuç Raporu")
        title_label.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold; 
            color: #2c3e50;
            padding: 10px;
        """)
        header_layout.addWidget(title_label)
        
        # Boşluk ekle
        header_layout.addStretch()
        
        main_layout.addWidget(header_widget)

        # Alt ana içerik
        content_widget = QWidget()
        content_layout = QHBoxLayout()
        content_widget.setLayout(content_layout)

        # Sol taraf - Kullanıcı Bilgileri
        user_info_widget = QWidget()
        user_info_layout = QVBoxLayout()
        user_info_widget.setLayout(user_info_layout)
        user_info_widget.setStyleSheet("""
            background-color: #f0f4f8;
            border-radius: 10px;
            padding: 20px;
        """)

        # Kullanıcı bilgileri etiketleri
        user_info_labels = [
            f"Ad Soyad: {self.name_input.text()}",
            f"Öğrenci No: {self.student_id.text()}",
            f"Bölüm: {self.department.text()}",
            f"Sınav Tarihi: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        ]

        for label_text in user_info_labels:
            label = QLabel(label_text)
            label.setStyleSheet("""
                margin: 10px 0;
                font-size: 16px;
                color: #34495e;
            """)
            user_info_layout.addWidget(label)
        
        user_info_layout.addStretch()

        # Alt taraf - İstatistikler
        stats_widget = QWidget()
        stats_layout = QVBoxLayout()
        stats_widget.setLayout(stats_layout)
        stats_widget.setStyleSheet("""
            background-color: #e8f4f8;
            border-radius: 10px;
            padding: 20px;
        """)

        # Hesaplamalar
        total_questions = len(self.all_questions)
        correct_answers = sum(1 for i, q in enumerate(self.all_questions) 
                               if self.answers.get(i, "") == q.get("correct", ""))
        wrong_answers = total_questions - correct_answers
        total_score = sum(5 if i == len(self.all_questions)-1 else 2 
                          for i, q in enumerate(self.all_questions) 
                          if self.answers.get(i, "") == q.get("correct", ""))

        stats_labels = [
            f"Toplam Soru: {total_questions}",
            f"Doğru Sayısı: {correct_answers}",
            f"Yanlış Sayısı: {wrong_answers}",
            f"Başarı Yüzdesi: {(correct_answers / total_questions * 100):.1f}%",
            f"Toplam Puan: {total_score}"
        ]

        for label_text in stats_labels:
            label = QLabel(label_text)
            label.setStyleSheet("""
                margin: 10px 0;
                font-size: 16px;
                color: #34495e;
            """)
            stats_layout.addWidget(label)
        
        stats_layout.addStretch()

        # Sağ taraf - Soru Detayları
        questions_widget = QWidget()
        questions_layout = QVBoxLayout()
        questions_widget.setLayout(questions_layout)
        
        # Soru detayları scroll area
        questions_scroll = QScrollArea()
        questions_scroll.setWidgetResizable(True)
        
        questions_container = QWidget()
        questions_container_layout = QVBoxLayout()
        questions_container.setLayout(questions_container_layout)

        # Her soru için kart oluştur
        for i, question_data in enumerate(self.all_questions):
            question_card = QWidget()
            question_card_layout = QVBoxLayout()
            question_card.setLayout(question_card_layout)
            question_card.setStyleSheet("""
                background-color: #f9f9f9;
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
                border: 1px solid #e1e4e8;
            """)

            # Soru metni
            question_label = QLabel(f"Soru {i+1}: {question_data['question']}")
            question_label.setWordWrap(True)
            question_label.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
            question_card_layout.addWidget(question_label)

            # Kullanıcı cevabı
            user_answer = self.answers.get(i, "Boş")
            correct_answer = question_data.get("correct", "")
            
            # Cevap durumunu belirle
            if user_answer == correct_answer:
                status = "Doğru"
                status_color = "#2ecc71"
            elif user_answer == "Boş":
                status = "Boş"
                status_color = "#f39c12"
            else:
                status = "Yanlış"
                status_color = "#e74c3c"

            # Cevap detayları
            answer_label = QLabel(f"""
            <b>Sizin Cevabınız:</b> <font color="{status_color}">{user_answer}</font><br>
            <b>Doğru Cevap:</b> {correct_answer}<br>
            <b>Durum:</b> <font color="{status_color}">{status}</font>
            """)
            answer_label.setStyleSheet("margin-top: 10px;")
            question_card_layout.addWidget(answer_label)

            questions_container_layout.addWidget(question_card)

        questions_scroll.setWidget(questions_container)
        questions_layout.addWidget(questions_scroll)

        # Layout'ları düzenle
        content_layout.addWidget(user_info_widget, 1)
        content_layout.addWidget(stats_widget, 1)
        content_layout.addWidget(questions_widget, 2)

        main_layout.addWidget(content_widget)

        # Yeni sınav butonu
        new_exam_button = QPushButton("Yeni Sınav")
        new_exam_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        new_exam_button.clicked.connect(lambda: self.restart_exam(results_dialog))
        main_layout.addWidget(new_exam_button)

        # Pencere kapatma olayını özelleştir
        results_dialog.closeEvent = lambda event: self.handle_results_dialog_close(event, results_dialog)

        # Pencereyi göster
        results_dialog.exec_()

    def restart_exam(self, results_dialog=None):
        """Yeni sınav başlatma metodu"""
        # Mevcut widget'ları temizle
        for i in reversed(range(self.main_layout.count())):
            self.main_layout.itemAt(i).widget().setParent(None)

        # Değişkenleri sıfırla
        self.current_question = 0
        self.score = 0
        self.answers = {}
        self.remaining_time = 60
        self.total_time = 30 * 60
        self.joker_used = False

        # Soruları yeniden karıştır
        self.initialize_questions()

        # Başlangıç ekranını göster
        self.init_welcome_screen()

        # Eğer results_dialog varsa onu da kapat
        if results_dialog:
            results_dialog.accept()  # Dialog'u kapat

    def handle_results_dialog_close(self, event, results_dialog):
        """Sonuç ekranı kapatılırken tüm pencereleri kapatır"""
        # Tüm widget'ları temizle
        for i in reversed(range(self.main_layout.count())):
            self.main_layout.itemAt(i).widget().setParent(None)

        # Uygulamayı kapat
        self.close()
        results_dialog.accept()

        self.pythonQuizDatabase.close_connection()
    def show_results_back(self):
        self.exam_widget.hide()
        results_widget = QWidget()
        results_layout = QVBoxLayout()
        results_widget.setStyleSheet("""
            background-color: #f4f7f9;
            font-family: 'Segoe UI', Arial, sans-serif;
        """)

        # Sonuçları hesapla
        total_score = 0
        correct_answers = 0
        wrong_answers = 0
        empty_answers = 0

        # Sonuçları içerecek ana widget
        results_container = QWidget()
        results_container_layout = QVBoxLayout()
        results_container.setStyleSheet("""
            background-color: white;
            border-radius: 12px;
            padding: 20px;
            margin: 20px;
        """)

        # Öğrenci Bilgileri Bölümü
        student_info_widget = QWidget()
        student_info_layout = QVBoxLayout()
        student_info_widget.setStyleSheet("""
            background-color: #e6f2ff;
            border-radius: 10px;
            padding: 15px;
        """)

        # Öğrenci bilgileri etiketleri
        student_name_label = QLabel(f"<h2 style='color: #2c3e50; margin-bottom: 10px;'>📝 {self.name_input.text()}</h2>")
        student_id_label = QLabel(f"🆔 Öğrenci No: {self.student_id.text()}")
        department_label = QLabel(f"🏫 Bölüm: {self.department.text()}")
        exam_date_label = QLabel(f"📅 Sınav Tarihi: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

        student_info_labels = [
            student_name_label, 
            student_id_label, 
            department_label, 
            exam_date_label
        ]

        for label in student_info_labels:
            label.setStyleSheet("color: #34495e; margin: 5px 0;")
            student_info_layout.addWidget(label)

        student_info_widget.setLayout(student_info_layout)
        results_container_layout.addWidget(student_info_widget)

        # Sorular için scroll area
        questions_scroll = QScrollArea()
        questions_widget = QWidget()
        questions_layout = QVBoxLayout()

        # Her soru için sonuç kartı
        for i, question_data in enumerate(self.all_questions):
            user_answer = self.answers.get(i, "Boş")
            correct_answer = question_data.get("correct", "")
            points = 5 if i == len(self.all_questions) - 1 else 2

            question_card = QWidget()
            question_card.setStyleSheet("""
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
                border: 1px solid #e1e4e8;
            """)
            question_card_layout = QVBoxLayout()

            # Soru başlığı
            question_title = QLabel(f"Soru {i + 1}")
            question_title.setStyleSheet("font-weight: bold; font-size: 16px; color: #2c3e50;")
            question_card_layout.addWidget(question_title)

            # Soru metni
            question_text = QLabel(question_data["question"])
            question_text.setWordWrap(True)
            question_card_layout.addWidget(question_text)

            # Cevap bilgileri
            if user_answer == correct_answer:
                total_score += points
                correct_answers += 1
                status = "Doğru"
                status_color = "#2ecc71"
            elif user_answer == "Boş":
                empty_answers += 1
                status = "Boş"
                status_color = "#f39c12"
            else:
                wrong_answers += 1
                status = "Yanlış"
                status_color = "#e74c3c"

            # Cevap detayları
            answer_details = QLabel(f"""
            <b>Sizin Cevabınız:</b> <font color="{status_color}">{user_answer}</font><br>
            <b>Doğru Cevap:</b> {correct_answer}<br>
            <b>Durum:</b> <font color="{status_color}">{status}</font><br>
            <b>Puan:</b> {points if status == 'Doğru' else 0}/{points}
            """)
            answer_details.setStyleSheet("margin-top: 10px;")
            question_card_layout.addWidget(answer_details)

            question_card.setLayout(question_card_layout)
            questions_layout.addWidget(question_card)

        questions_widget.setLayout(questions_layout)
        questions_scroll.setWidget(questions_widget)
        questions_scroll.setWidgetResizable(True)
        questions_scroll.setMinimumHeight(300)
        results_container_layout.addWidget(questions_scroll)

        # İstatistikler
        stats_widget = QWidget()
        stats_layout = QVBoxLayout()
        stats_widget.setStyleSheet("""
            background-color: #e8f4f8;
            border-radius: 10px;
            padding: 15px;
        """)

        total_questions = len(self.all_questions)
        stats_labels = [
            f"Toplam Soru: {total_questions}",
            f"Doğru Sayısı: {correct_answers}",
            f"Yanlış Sayısı: {wrong_answers}",
            f"Boş Sayısı: {empty_answers}",
            f"Başarı Yüzdesi: {(correct_answers / total_questions * 100):.1f}%",
            f"Toplam Puan: {total_score}"
        ]

        for stat in stats_labels:
            label = QLabel(stat)
            label.setStyleSheet("margin: 5px 0; color: #2c3e50;")
            stats_layout.addWidget(label)

        stats_widget.setLayout(stats_layout)
        results_container_layout.addWidget(stats_widget)

        # Yeni sınav butonu
        new_exam_button = QPushButton("Yeni Sınav")
        new_exam_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        new_exam_button.clicked.connect(self.restart_exam)
        results_container_layout.addWidget(new_exam_button)

        results_container.setLayout(results_container_layout)

        # Ana layout'a ekle
        results_layout.addWidget(results_container)
        results_widget.setLayout(results_layout)
        self.main_layout.addWidget(results_widget)

    def show_results_org(self):
        self.exam_widget.hide()
        results_widget = QWidget()
        results_layout = QVBoxLayout()

        # Sonuçları hesapla
        total_score = 0
        results_text = ""
        correct_answers = 0
        wrong_answers = 0
        empty_answers = 0

        # Öğrenci bilgileri
        student_info = f"""
        <h2 style="color: #333;">Sınav Sonuç Raporu</h2>
        <p>
        <b>Ad Soyad:</b> {self.name_input.text()}<br>
        <b>Öğrenci No:</b> {self.student_id.text()}<br>
        <b>Bölüm:</b> {self.department.text()}<br>
        <b>Sınav Tarihi:</b> {datetime.now().strftime("%d/%m/%Y %H:%M")}
        </p>
        """

        results_text += student_info

        # Her soru için sonuçları değerlendir
        for i, question_data in enumerate(self.all_questions):
            user_answer = self.answers.get(i, "Boş")
            correct_answer = question_data.get("correct", "")

            # Bonus soru için 5 puan, diğerleri için 2 puan
            points = 5 if i == len(self.all_questions) - 1 else 2

            # Soru türünü belirle
            question_type = (
                "Test Sorusu" if "options" in question_data else "Açık Uçlu Soru"
            )

            results_text += f'<div style="margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">'
            results_text += f"<h3>Soru {i + 1} ({question_type})</h3>"
            results_text += f'<p><b>Soru:</b> {question_data["question"]}</p>'

            if user_answer == correct_answer:
                total_score += points
                correct_answers += 1
                status_color = "#4CAF50"  # Yeşil
                status = "Doğru"
            elif user_answer == "Boş":
                empty_answers += 1
                status_color = "#FFC107"  # Sarı
                status = "Boş Bırakıldı"
            else:
                wrong_answers += 1
                status_color = "#F44336"  # Kırmızı
                status = "Yanlış"

            results_text += f"""
            <p><b>Sizin cevabınız:</b> <span style="color: {status_color}">{user_answer}</span></p>
            <p><b>Doğru cevap:</b> {correct_answer}</p>
            <p><b>Durum:</b> <span style="color: {status_color}">{status}</span></p>
            <p><b>Puan:</b> {points if status == "Doğru" else 0}/{points}</p>
            </div>
            """

        # İstatistikler
        total_questions = len(self.all_questions)
        stats = f"""
        <div style="background-color: #f5f5f5; padding: 15px; margin: 15px 0; border-radius: 5px;">
            <h3>Sınav İstatistikleri</h3>
            <p><b>Toplam Soru:</b> {total_questions}</p>
            <p><b>Doğru Sayısı:</b> {correct_answers}</p>
            <p><b>Yanlış Sayısı:</b> {wrong_answers}</p>
            <p><b>Boş Sayısı:</b> {empty_answers}</p>
            <p><b>Başarı Yüzdesi:</b> {(correct_answers / total_questions * 100):.1f}%</p>
            <h2 style="color: #2196F3;">Toplam Puan: {total_score}</h2>
        </div>
        """
        results_text += stats

        # En yüksek skoru güncelle
        if total_score > self.highest_score:
            self.highest_score = total_score
            results_text += (
                '<p style="color: #4CAF50; font-weight: bold;">Yeni En Yüksek Skor!</p>'
            )

        # Sonuçları göster
        results_label = QLabel(results_text)
        results_label.setTextFormat(Qt.RichText)
        results_label.setWordWrap(True)

        # Scroll area ekle
        scroll = QScrollArea()
        scroll.setWidget(results_label)
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(400)

        # Yeni sınav başlatma butonu
        new_exam_button = QPushButton("Yeni Sınav")
        new_exam_button.clicked.connect(self.restart_exam)
        new_exam_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)

        results_layout.addWidget(scroll)
        results_layout.addWidget(new_exam_button)

        results_widget.setLayout(results_layout)
        self.main_layout.addWidget(results_widget)

    def restart_exam_org(self):
        """Yeni sınav başlatma metodu"""
        # Mevcut widget'ları temizle
        for i in reversed(range(self.main_layout.count())):
            self.main_layout.itemAt(i).widget().setParent(None)

        # Değişkenleri sıfırla
        self.current_question = 0
        self.score = 0
        self.answers = {}
        self.remaining_time = 60
        self.total_time = 30 * 60
        self.joker_used = False

        # Soruları yeniden karıştır
        self.initialize_questions()

        # Başlangıç ekranını göster
        self.init_welcome_screen()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = ExamApp()
    ex.show()
    sys.exit(app.exec_())
