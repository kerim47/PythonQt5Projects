import sys
import numpy as np
import pandas as pd
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import pyqtgraph as pg
from datetime import datetime, timedelta
from binance.client import Client
from ta.trend import SMAIndicator, EMAIndicator
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands

class BinanceAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        # Binance API bağlantısı
        self.api_key = 'YOUR_API_KEY'  # Binance API anahtarınız
        self.api_secret = 'YOUR_API_SECRET'  # Binance API gizli anahtarınız
        self.client = Client(self.api_key, self.api_secret)
        
        self.setWindowTitle("Binance Borsa Analiz Platformu")
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a2e;
            }
            QLabel, QComboBox, QPushButton {
                color: #e6e6ff;
                font-size: 14px;
                padding: 8px;
                background-color: #16213e;
                border-radius: 5px;
                margin: 3px;
            }
            QPushButton {
                background-color: #4d79ff;
                border: none;
            }
            QPushButton:hover {
                background-color: #3366ff;
            }
            QTableWidget {
                background-color: #16213e;
                color: #e6e6ff;
                gridline-color: #4d79ff;
                border: none;
            }
            QHeaderView::section {
                background-color: #2d4373;
                color: #e6e6ff;
                padding: 5px;
            }
            QStatusBar {
                background-color: #16213e;
                color: #e6e6ff;
            }
        """)
        
        self.setup_ui()
        self.stock_data = pd.DataFrame()
        self.setup_timer()
        self.update_data()
        self.setMinimumSize(1200, 800)

    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        self.create_top_panel()
        self.create_graph_widget()
        self.create_indicators_table()
        self.create_signals_panel()
        
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

    def create_top_panel(self):
        self.top_panel = QHBoxLayout()
        
        # Market tipi seçimi (Spot/Futures)
        self.market_type_combo = QComboBox()
        self.market_type_combo.addItems(['SPOT', 'FUTURES'])
        self.market_type_combo.currentTextChanged.connect(self.update_symbol_list)
        self.top_panel.addWidget(QLabel("Market:"))
        self.top_panel.addWidget(self.market_type_combo)
        
        # Sembol seçimi
        self.symbol_combo = QComboBox()
        self.symbol_combo.setEditable(True)
        self.symbol_combo.setInsertPolicy(QComboBox.InsertPolicy.InsertAlphabetically)
        self.top_panel.addWidget(QLabel("Sembol:"))
        self.top_panel.addWidget(self.symbol_combo)
        
        # Zaman aralığı seçimi
        self.interval_combo = QComboBox()
        self.interval_combo.addItems(['1m', '5m', '15m', '1h', '4h', '1d'])
        self.top_panel.addWidget(QLabel("Periyot:"))
        self.top_panel.addWidget(self.interval_combo)
        
        # Analiz türü seçimi
        self.analysis_combo = QComboBox()
        self.analysis_combo.addItems(['SMA', 'EMA', 'RSI', 'Bollinger'])
        self.top_panel.addWidget(QLabel("Analiz:"))
        self.top_panel.addWidget(self.analysis_combo)
        
        # Yenile butonu
        self.refresh_btn = QPushButton("Yenile")
        self.refresh_btn.clicked.connect(self.update_data)
        self.top_panel.addWidget(self.refresh_btn)
        
        self.layout.addLayout(self.top_panel)
        self.update_symbol_list(self.market_type_combo.currentText())

    def update_symbol_list(self, market_type):
        try:
            self.symbol_combo.clear()
            if market_type == 'SPOT':
                # Spot piyasa sembollerini al
                exchange_info = self.client.get_exchange_info()
                symbols = [s['symbol'] for s in exchange_info['symbols'] 
                          if s['status'] == 'TRADING' and s['quoteAsset'] in ['USDT', 'BTC']]
            else:
                # Vadeli işlem sembollerini al
                futures_exchange_info = self.client.futures_exchange_info()
                symbols = [s['symbol'] for s in futures_exchange_info['symbols'] 
                          if s['status'] == 'TRADING']
            
            symbols.sort()
            self.symbol_combo.addItems(symbols)
            
        except Exception as e:
            self.statusBar.showMessage(f"Sembol listesi güncelleme hatası: {str(e)}", 5000)

    def fetch_binance_data(self):
        try:
            symbol = self.symbol_combo.currentText()
            interval = self.interval_combo.currentText()
            market_type = self.market_type_combo.currentText()
            
            # Zaman aralığını hesapla
            end_time = int(datetime.now().timestamp() * 1000)
            if interval == '1m':
                start_time = end_time - (1000 * 60 * 500)  # Son 500 dakika
            elif interval == '5m':
                start_time = end_time - (1000 * 60 * 5 * 500)  # Son 500 5-dakika
            elif interval == '15m':
                start_time = end_time - (1000 * 60 * 15 * 500)  # Son 500 15-dakika
            elif interval == '1h':
                start_time = end_time - (1000 * 60 * 60 * 500)  # Son 500 saat
            elif interval == '4h':
                start_time = end_time - (1000 * 60 * 60 * 4 * 500)  # Son 500 4-saat
            else:  # 1d
                start_time = end_time - (1000 * 60 * 60 * 24 * 500)  # Son 500 gün
            
            # Veri çekme
            if market_type == 'SPOT':
                klines = self.client.get_klines(
                    symbol=symbol,
                    interval=interval,
                    startTime=start_time,
                    endTime=end_time
                )
            else:
                klines = self.client.futures_klines(
                    symbol=symbol,
                    interval=interval,
                    startTime=start_time,
                    endTime=end_time
                )
            
            # Verileri DataFrame'e dönüştür
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Sayısal sütunları dönüştür
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            self.stock_data = df
            self.statusBar.showMessage(f"Veri başarıyla güncellendi: {symbol}", 5000)
            return True
            
        except Exception as e:
            self.statusBar.showMessage(f"Veri çekme hatası: {str(e)}", 5000)
            return False

    def calculate_indicators(self):
        if len(self.stock_data) == 0:
            return
        
        try:
            # SMA hesaplama
            sma = SMAIndicator(close=self.stock_data['close'], window=20)
            self.stock_data['SMA20'] = sma.sma_indicator()
            
            # EMA hesaplama
            ema = EMAIndicator(close=self.stock_data['close'], window=20)
            self.stock_data['EMA20'] = ema.ema_indicator()
            
            # RSI hesaplama
            rsi = RSIIndicator(close=self.stock_data['close'], window=14)
            self.stock_data['RSI'] = rsi.rsi()
            
            # Bollinger Bands hesaplama
            bollinger = BollingerBands(close=self.stock_data['close'], window=20)
            self.stock_data['BB_upper'] = bollinger.bollinger_hband()
            self.stock_data['BB_lower'] = bollinger.bollinger_lband()
            
        except Exception as e:
            self.statusBar.showMessage(f"İndikatör hesaplama hatası: {str(e)}", 5000)

    def update_graph(self):
        try:
            self.graph_widget.clear()
            
            timestamps = [i for i in range(len(self.stock_data))]
            
            # Mum grafiği
            for i in range(len(self.stock_data)):
                row = self.stock_data.iloc[i]
                if row['close'] >= row['open']:
                    color = '#00ff00'  # Yeşil mum
                else:
                    color = '#ff0000'  # Kırmızı mum
                
                # Gövde
                self.graph_widget.plot(
                    x=[i, i],
                    y=[row['open'], row['close']],
                    pen=pg.mkPen(color=color, width=3)
                )
                # Fitil
                self.graph_widget.plot(
                    x=[i, i],
                    y=[row['low'], row['high']],
                    pen=pg.mkPen(color=color, width=1)
                )
            
            # Seçili indikatör
            analysis_type = self.analysis_combo.currentText()
            if analysis_type == 'SMA':
                self.graph_widget.plot(
                    x=timestamps,
                    y=self.stock_data['SMA20'].values,
                    pen=pg.mkPen(color='#ffff00', width=2),
                    name='SMA20'
                )
            elif analysis_type == 'EMA':
                self.graph_widget.plot(
                    x=timestamps,
                    y=self.stock_data['EMA20'].values,
                    pen=pg.mkPen(color='#ffff00', width=2),
                    name='EMA20'
                )
            elif analysis_type == 'RSI':
                rsi_widget = pg.ViewBox()
                p1 = self.graph_widget.plotItem
                p1.scene().addItem(rsi_widget)
                p1.getAxis('right').linkToView(rsi_widget)
                rsi_widget.setXLink(p1)
                
                pg.PlotDataItem(
                    x=timestamps,
                    y=self.stock_data['RSI'].values,
                    pen=pg.mkPen(color='#ffff00', width=2)
                )
            elif analysis_type == 'Bollinger':
                self.graph_widget.plot(
                    x=timestamps,
                    y=self.stock_data['BB_upper'].values,
                    pen=pg.mkPen(color='#ffff00', width=1),
                    name='Bollinger Üst'
                )
                self.graph_widget.plot(
                    x=timestamps,
                    y=self.stock_data['BB_lower'].values,
                    pen=pg.mkPen(color='#ffff00', width=1),
                    name='Bollinger Alt'
                )
            
            # Grafik başlığı
            self.graph_widget.setTitle(
                f"{self.symbol_combo.currentText()} - {self.interval_combo.currentText()}",
                color='w',
                size='20pt'
            )
            
            self.graph_widget.addLegend()
            
        except Exception as e:
            self.statusBar.showMessage(f"Grafik güncelleme hatası: {str(e)}", 5000)

    def create_graph_widget(self):
        self.graph_widget = pg.PlotWidget()
        self.graph_widget.setBackground('#1a1a2e')
        self.graph_widget.showGrid(x=True, y=True, alpha=0.3)
        
        self.graph_widget.setTitle("Fiyat Grafiği", color='w', size='20pt')
        styles = {'color': '#e6e6ff', 'font-size': '14px'}
        self.graph_widget.setLabel('left', 'Fiyat', **styles)
        self.graph_widget.setLabel('bottom', 'Zaman', **styles)
        
        self.layout.addWidget(self.graph_widget)

    def create_indicators_table(self):
        self.indicators_table = QTableWidget()
        self.indicators_table.setColumnCount(7)
        self.indicators_table.setHorizontalHeaderLabels([
            'Tarih', 'Açılış', 'Yüksek', 'Düşük', 'Kapanış', 'RSI', 'Hacim'
        ])
        self.indicators_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.indicators_table.setMaximumHeight(200)
        self.layout.addWidget(self.indicators_table)

    def update_table(self):
        try:
            self.indicators_table.setRowCount(min(10, len(self.stock_data)))
            
            for i in range(min(10, len(self.stock_data))):
                row = self.stock_data.iloc[-(i+1)]
                date_str = row.name.strftime('%Y-%m-%d %H:%M')
                
                # Verileri tabloya yerleştir
                self.indicators_table.setItem(i, 0, QTableWidgetItem(date_str))
                self.indicators_table.setItem(i, 1, QTableWidgetItem(f"{float(row['open']):.2f}"))
                self.indicators_table.setItem(i, 2, QTableWidgetItem(f"{float(row['high']):.2f}"))
                self.indicators_table.setItem(i, 3, QTableWidgetItem(f"{float(row['low']):.2f}"))
                self.indicators_table.setItem(i, 4, QTableWidgetItem(f"{float(row['close']):.2f}"))
                self.indicators_table.setItem(i, 5, QTableWidgetItem(f"{float(row['RSI']):.2f}"))
                self.indicators_table.setItem(i, 6, QTableWidgetItem(f"{float(row['volume']):.2f}"))
                
                # Renklendirme
                if row['close'] > row['open']:
                    for col in range(1, 5):
                        self.indicators_table.item(i, col).setForeground(QColor('#00ff00'))  # Yeşil
                else:
                    for col in range(1, 5):
                        self.indicators_table.item(i, col).setForeground(QColor('#ff0000'))  # Kırmızı
                
                if row['RSI'] > 70:
                    self.indicators_table.item(i, 5).setForeground(QColor('#ff0000'))
                elif row['RSI'] < 30:
                    self.indicators_table.item(i, 5).setForeground(QColor('#00ff00'))
                
        except Exception as e:
            self.statusBar.showMessage(f"Tablo güncelleme hatası: {str(e)}", 5000)

    def create_signals_panel(self):
        self.signals_group = QGroupBox("Alım/Satım Sinyalleri")
        self.signals_group.setStyleSheet("""
            QGroupBox {
                color: #e6e6ff;
                border: 2px solid #4d79ff;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
        """)
        
        signals_layout = QVBoxLayout()
        self.signals_text = QTextEdit()
        self.signals_text.setReadOnly(True)
        self.signals_text.setStyleSheet("""
            QTextEdit {
                background-color: #16213e;
                color: #e6e6ff;
                font-size: 14px;
                padding: 5px;
            }
        """)
        signals_layout.addWidget(self.signals_text)
        self.signals_group.setLayout(signals_layout)
        self.signals_group.setMaximumHeight(150)
        
        self.layout.addWidget(self.signals_group)

    def update_signals(self):
        try:
            if len(self.stock_data) < 2:
                return
                
            signals = []
            last_row = self.stock_data.iloc[-1]
            prev_row = self.stock_data.iloc[-2]
            
            # RSI Sinyalleri
            if last_row['RSI'] < 30:
                signals.append("💹 RSI Aşırı Satım (< 30) - Alım Fırsatı Olabilir")
            elif last_row['RSI'] > 70:
                signals.append("📉 RSI Aşırı Alım (> 70) - Satış Fırsatı Olabilir")
            
            # SMA Sinyalleri
            if last_row['close'] > last_row['SMA20'] and prev_row['close'] <= prev_row['SMA20']:
                signals.append("💚 SMA-20 Yukarı Kırılım - Alım Sinyali")
            elif last_row['close'] < last_row['SMA20'] and prev_row['close'] >= prev_row['SMA20']:
                signals.append("❌ SMA-20 Aşağı Kırılım - Satış Sinyali")
            
            # Bollinger Sinyalleri
            if last_row['close'] <= last_row['BB_lower']:
                signals.append("📈 Fiyat Bollinger Alt Bandında - Potansiyel Alım Bölgesi")
            elif last_row['close'] >= last_row['BB_upper']:
                signals.append("📉 Fiyat Bollinger Üst Bandında - Potansiyel Satış Bölgesi")
            
            # Hacim Analizi
            volume_ma = self.stock_data['volume'].rolling(window=20).mean()
            if last_row['volume'] > 2 * volume_ma.iloc[-1]:
                signals.append("📊 Yüksek Hacim Tespit Edildi - Dikkatli Olun!")
            
            # Trend Analizi
            short_term_trend = self.stock_data['close'].tail(5).pct_change().mean() * 100
            if short_term_trend > 1:
                signals.append(f"📈 Kısa Vadeli Yükseliş Trendi ({short_term_trend:.1f}%)")
            elif short_term_trend < -1:
                signals.append(f"📉 Kısa Vadeli Düşüş Trendi ({short_term_trend:.1f}%)")
            
            # Fiyat Değişimi
            price_change = ((last_row['close'] - last_row['open']) / last_row['open']) * 100
            signals.append(f"💫 24s Değişim: {price_change:.2f}%")
            
            # Sinyalleri güncelle
            self.signals_text.clear()
            if signals:
                self.signals_text.setText("\n".join(signals))
            else:
                self.signals_text.setText("🔍 Şu anda aktif sinyal bulunmuyor.")
            
        except Exception as e:
            self.statusBar.showMessage(f"Sinyal güncelleme hatası: {str(e)}", 5000)

    def setup_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        
        # Seçili periyoda göre güncelleme sıklığını ayarla
        interval_map = {
            '1m': 10000,    # 10 saniye
            '5m': 30000,    # 30 saniye
            '15m': 60000,   # 1 dakika
            '1h': 300000,   # 5 dakika
            '4h': 600000,   # 10 dakika
            '1d': 3600000   # 1 saat
        }
        current_interval = self.interval_combo.currentText()
        self.timer.start(interval_map.get(current_interval, 60000))

    def update_data(self):
        """Tüm verileri ve göstergeleri güncelle"""
        if self.fetch_binance_data():
            self.calculate_indicators()
            self.update_graph()
            self.update_table()
            self.update_signals()
            
            current_time = datetime.now().strftime('%H:%M:%S')
            self.statusBar.showMessage(
                f"Son güncelleme: {current_time} - {self.symbol_combo.currentText()}", 
                5000
            )

def main():
    app = QApplication(sys.argv)
    font = QFont("Arial", 10)
    app.setFont(font)
    app.setStyle("Fusion")
    
    window = BinanceAnalyzer()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()