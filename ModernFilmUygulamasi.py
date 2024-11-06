import sys
import os
import requests
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QListWidget, QTextEdit, QTabWidget, QGridLayout,
                            QScrollArea, QFrame, QMessageBox, QProgressBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QFont, QPalette, QColor


class MovieDetailsFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_style()
        
    def setup_style(self):
        self.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 10px;
            }
            QLabel {
                color: #ffffff;
                padding: 5px;
            }
            QLabel#titleLabel {
                font-size: 16px;
                font-weight: bold;
                color: #ffffff;
            }
            QLabel#headerLabel {
                color: #9e9e9e;
                font-size: 12px;
            }
            QLabel#valueLabel {
                color: #ffffff;
                font-weight: bold;
            }
            QTextEdit {
                background-color: #353535;
                color: #ffffff;
                border-radius: 5px;
                padding: 10px;
                border: 1px solid #555555;
            }
        """)
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Ana başlık
        title_label = QLabel("Film Detayları")
        title_label.setObjectName("titleLabel")
        layout.addWidget(title_label)
        
        # Detaylar için grid layout
        details_grid = QGridLayout()
        details_grid.setSpacing(10)
        
        # Orijinal Başlık
        self.add_detail_row(details_grid, 0, "Orijinal Başlık:", "")
        
        # Yayın Tarihi
        self.add_detail_row(details_grid, 1, "Yayın Tarihi:", "")
        
        # Puan
        self.add_detail_row(details_grid, 2, "Puan:", "")
        
        # Popülerlik
        self.add_detail_row(details_grid, 3, "Popülerlik:", "")
        
        layout.addLayout(details_grid)
        
        # Özet başlığı
        summary_header = QLabel("ÖZET")
        summary_header.setObjectName("titleLabel")
        layout.addWidget(summary_header)
        
        # Özet metni
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMinimumHeight(150)
        layout.addWidget(self.summary_text)
        
    def add_detail_row(self, grid, row, header, value=""):
        header_label = QLabel(header)
        header_label.setObjectName("headerLabel")
        value_label = QLabel(value)
        value_label.setObjectName("valueLabel")
        
        grid.addWidget(header_label, row, 0)
        grid.addWidget(value_label, row, 1)
        
    def update_details(self, movie):
        """Film detaylarını güncelle"""
        try:
            # Grid'deki değerleri güncelle
            grid = self.findChild(QGridLayout)

            # Orijinal başlık
            grid.itemAtPosition(0, 1).widget().setText(movie['original_title'])

            # Yayın tarihi
            try:
                release_date = datetime.strptime(movie['release_date'], '%Y-%m-%d').strftime('%d.%m.%Y')
            except Exception:
                release_date = "Belirtilmemiş"
            grid.itemAtPosition(1, 1).widget().setText(release_date)

            # Puan
            vote_text = f"{movie['vote_average']:.1f}/10 ({movie['vote_count']} oy)"
            grid.itemAtPosition(2, 1).widget().setText(vote_text)

            # Popülerlik
            popularity_text = f"{movie['popularity']:.1f}"
            grid.itemAtPosition(3, 1).widget().setText(popularity_text)

            # Özet
            self.summary_text.setText(movie['overview'])

        except Exception as e:
            print(f"Film detayları güncellenirken hata oluştu: {e}")

class MovieFetcher(QThread):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, api_key, base_url, endpoint, params):
        super().__init__()
        self.api_key = api_key
        self.base_url = base_url
        self.endpoint = endpoint
        self.params = params
        
    def run(self):
        try:
            url = f"{self.base_url}{self.endpoint}"
            self.params['api_key'] = self.api_key
            response = requests.get(url, params=self.params)
            response.raise_for_status()
            self.finished.emit(response.json()['results'])
        except Exception as e:
            self.error.emit(str(e))

class ModernFilmUygulamasi(QMainWindow):
    def __init__(self):
        super().__init__()
        self.api_key = "d8d61d9f42c52e3374f633edaf6bba81"
        self.base_url = "https://api.themoviedb.org/3"
        self.image_base_url = "https://image.tmdb.org/t/p/w500"
        
        self.setWindowTitle("Film Uygulaması")
        self.setGeometry(100, 100, 1200, 800)
        self.setup_ui()
        self.setup_style()
        
    def setup_style(self):
        # Modern koyu tema renkleri
        palette = QPalette()
        # Ana renkler
        palette.setColor(QPalette.Window, QColor("#1e1e1e"))
        palette.setColor(QPalette.WindowText, QColor("#ffffff"))
        palette.setColor(QPalette.Base, QColor("#2d2d2d"))
        palette.setColor(QPalette.AlternateBase, QColor("#353535"))
        palette.setColor(QPalette.Text, QColor("#ffffff"))
        palette.setColor(QPalette.Button, QColor("#0d47a1"))
        palette.setColor(QPalette.ButtonText, QColor("#ffffff"))
        palette.setColor(QPalette.Highlight, QColor("#1976d2"))
        palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
        self.setPalette(palette)
        
        # Font ayarları
        self.setFont(QFont("Segoe UI", 10))
        
        # Stil sayfası
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 10px;
            }
            QLabel {
                color: #ffffff;
                padding: 5px;
            }
            QLineEdit {
                padding: 8px;
                border-radius: 5px;
                background-color: #353535;
                color: #ffffff;
                border: 1px solid #555555;
            }
            QPushButton {
                background-color: #0d47a1;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                border: none;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
            QListWidget {
                background-color: #353535;
                border-radius: 5px;
                padding: 5px;
                color: #ffffff;
                border: 1px solid #555555;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 3px;
            }
            QListWidget::item:selected {
                background-color: #1976d2;
            }
            QTextEdit {
                background-color: #353535;
                color: #ffffff;
                border-radius: 5px;
                padding: 10px;
                border: 1px solid #555555;
            }
            QProgressBar {
                border: 2px solid #555555;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #1976d2;
            }
        """)
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Sol panel
        left_panel = QFrame()
        left_panel.setMinimumWidth(300)
        left_panel.setMaximumWidth(400)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(15)
        
        # Arama bölümü
        search_frame = QFrame()
        search_layout = QVBoxLayout(search_frame)
        search_layout.setSpacing(10)
        
        # Arama başlığı
        search_title = QLabel("Film Ara")
        search_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        search_layout.addWidget(search_title)
        
        # Arama kutusu ve butonu
        search_input_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Film adını yazın...")
        self.search_button = QPushButton("Ara")
        self.search_button.clicked.connect(self.search_movies)
        search_input_layout.addWidget(self.search_input)
        search_input_layout.addWidget(self.search_button)
        search_layout.addLayout(search_input_layout)
        
        left_layout.addWidget(search_frame)
        
        # Popüler filmler butonu
        popular_button = QPushButton("Popüler Filmler")
        popular_button.setFont(QFont("Segoe UI", 10))
        popular_button.clicked.connect(self.show_popular_movies)
        left_layout.addWidget(popular_button)
        
        # Film listesi başlığı
        list_title = QLabel("Film Listesi")
        list_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        left_layout.addWidget(list_title)
        
        # Film listesi
        self.movie_list = QListWidget()
        self.movie_list.itemClicked.connect(self.on_movie_select)
        left_layout.addWidget(self.movie_list)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        left_layout.addWidget(self.progress)
        
        # Sağ panel
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(20)
        
        # Film başlığı
        self.movie_title = QLabel()
        self.movie_title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.movie_title.setWordWrap(True)
        right_layout.addWidget(self.movie_title)
        
        # Poster ve detaylar
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # Poster frame
        poster_frame = QFrame()
        poster_layout = QVBoxLayout(poster_frame)
        self.poster_label = QLabel()
        self.poster_label.setFixedSize(300, 450)
        self.poster_label.setAlignment(Qt.AlignCenter)
        self.poster_label.setStyleSheet("background-color: #353535; border-radius: 10px;")
        poster_layout.addWidget(self.poster_label)
        content_layout.addWidget(poster_frame)
        
        # Film detayları frame'i (yeni eklenen kısım)
        self.details_frame = MovieDetailsFrame()
        content_layout.addWidget(self.details_frame)
        
        right_layout.addLayout(content_layout)
        
        # Ana layout'a panelleri ekle
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, 2)
        
    def search_movies(self):
        query = self.search_input.text()
        if not query:
            return
            
        self.progress.setVisible(True)
        params = {
            'language': 'tr-TR',
            'query': query,
            'page': 1
        }
        
        self.fetcher = MovieFetcher(self.api_key, self.base_url, "/search/movie", params)
        self.fetcher.finished.connect(self.update_movie_list)
        self.fetcher.error.connect(self.show_error)
        self.fetcher.start()
        
    def show_popular_movies(self):
        self.progress.setVisible(True)
        params = {
            'language': 'tr-TR',
            'page': 1
        }
        
        self.fetcher = MovieFetcher(self.api_key, self.base_url, "/movie/popular", params)
        self.fetcher.finished.connect(self.update_movie_list)
        self.fetcher.error.connect(self.show_error)
        self.fetcher.start()
        
    def update_movie_list(self, movies):
        self.progress.setVisible(False)
        self.movie_list.clear()
        self.movies = movies
        
        for movie in movies:
            try:
                release_year = movie['release_date'][:4] if movie['release_date'] else "N/A"
                title = f"{movie['title']} ({release_year})"
                self.movie_list.addItem(title)
            except:
                self.movie_list.addItem(movie['title'])
        
    def on_movie_select(self, item):
        index = self.movie_list.row(item)
        movie = self.movies[index]
        self.show_movie_details(movie)
        

    # Ayrıca show_movie_details metodunu da güncellememiz gerekiyor:
    def show_movie_details(self, movie):
        # Başlık güncelle
        self.movie_title.setText(movie['title'])
        
        # Film detaylarını güncelle
        self.details_frame.update_details(movie)
        
        # Poster'ı göster
        if movie.get('poster_path'):
            poster_url = f"{self.image_base_url}{movie['poster_path']}"
            try:
                response = requests.get(poster_url)
                image = QImage()
                image.loadFromData(response.content)
                pixmap = QPixmap(image).scaled(300, 450, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.poster_label.setPixmap(pixmap)
            except:
                self.poster_label.setText("Poster yüklenemedi")
                self.poster_label.setStyleSheet("background-color: #353535; color: #ffffff;")
        else:
            self.poster_label.setText("Poster yok")
            self.poster_label.setStyleSheet("background-color: #353535; color: #ffffff;")
                
    def show_error(self, message):
        self.progress.setVisible(False)
        QMessageBox.critical(self, "Hata", f"Bir hata oluştu: {message}")

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = ModernFilmUygulamasi()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
