import sys
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QFrame, QGridLayout)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont
import pyqtgraph as pg
from datetime import datetime

class StylishLabel(QLabel):
    def __init__(self, text=''):
        super().__init__(text)
        self.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border-radius: 5px;
                padding: 5px;
                color: #2c3e50;
            }
        """)

class CurrencyWidget(QFrame):
    def __init__(self, currency):
        super().__init__()
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #ddd;
            }
        """)
        
        layout = QGridLayout(self)
        
        title = QLabel(f"{currency}")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        
        self.value_label = StylishLabel('0.00')
        self.value_label.setFont(QFont("Arial", 11))
        self.value_label.setAlignment(Qt.AlignRight)
        
        self.trend_label = QLabel('➡')
        self.trend_label.setFont(QFont("Arial", 14))
        
        self.high_label = StylishLabel('En Yüksek: 0.00')
        self.low_label = StylishLabel('En Düşük: 0.00')
        self.avg_label = StylishLabel('Ortalama: 0.00')
        
        layout.addWidget(title, 0, 0)
        layout.addWidget(self.value_label, 0, 1)
        layout.addWidget(self.trend_label, 0, 2)
        layout.addWidget(self.high_label, 1, 0, 1, 3)
        layout.addWidget(self.low_label, 2, 0, 1, 3)
        layout.addWidget(self.avg_label, 3, 0, 1, 3)

class BorsaTakip(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Borsa Takip")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("background-color: #f0f2f5;")
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)
        
        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)
        self.left_layout.setSpacing(20)
        
        self.currency_widgets = {}
        self.currency_data = {
            'USD': {'values': [], 'times': [], 'last_value': 0},
            'EUR': {'values': [], 'times': [], 'last_value': 0},
            'GBP': {'values': [], 'times': [], 'last_value': 0},
        }
        
        for currency in self.currency_data.keys():
            widget = CurrencyWidget(currency)
            self.currency_widgets[currency] = widget
            self.left_layout.addWidget(widget)

        # Güncel tarihi göstermek için QLabel ekleyin
        self.date_label = QLabel()
        self.date_label.setStyleSheet("font-size: 14px; color: #2c3e50;")
        self.left_layout.addWidget(self.date_label)
        
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)
        
        self.graph_widget = pg.PlotWidget()
        self.setup_graph()
        self.right_layout.addWidget(self.graph_widget)
        
        self.stats_panel = QFrame()
        self.stats_panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #ddd;
                padding: 10px;
            }
        """)
        self.stats_layout = QHBoxLayout(self.stats_panel)
        
        self.current_stats = QLabel()
        self.current_stats.setStyleSheet("font-size: 12px; color: #2c3e50;")
        self.stats_layout.addWidget(self.current_stats)
        
        self.right_layout.addWidget(self.stats_panel)
        
        self.layout.addWidget(self.left_panel, 1)
        self.layout.addWidget(self.right_panel, 2)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1000)  # Update every 1 second
        
        self.active_currency = 'USD'
        self.update_data()

    def update_data(self):
        try:
            # Update the API URL with your actual API key
            url = 'https://v6.exchangerate-api.com/v6/dac92d78d8c1d4a2893eff4d/latest/USD'
            response = requests.get(url)
            response.raise_for_status()  # Raises an error for bad responses
            
            data = response.json()  # Assuming the response is in JSON format
            
            current_time = datetime.now()
            
            # Güncel tarihi ayarla
            self.date_label.setText(current_time.strftime('%Y-%m-%d %H:%M:%S'))

            # Get the USD to TRY exchange rate
            usd_to_try = float(data['conversion_rates']['TRY'])

            for currency in self.currency_data.keys():
                if currency in data['conversion_rates']:
                    # Convert the current value to TRY
                    current_value = float(data['conversion_rates'][currency]) * usd_to_try
                    
                    # Update data
                    self.currency_data[currency]['values'].append(current_value)
                    self.currency_data[currency]['times'].append(current_time)
                    
                    if len(self.currency_data[currency]['values']) > 50:
                        self.currency_data[currency]['values'].pop(0)
                        self.currency_data[currency]['times'].pop(0)
                    
                    # Update widgets
                    widget = self.currency_widgets[currency]
                    widget.value_label.setText(f'{current_value:.2f} TRY')  # Display in TRY
                    
                    # Calculate and update statistics
                    values = self.currency_data[currency]['values']
                    widget.high_label.setText(f'En Yüksek: {max(values):.2f} TRY')
                    widget.low_label.setText(f'En Düşük: {min(values):.2f} TRY')
                    widget.avg_label.setText(f'Ortalama: {sum(values)/len(values):.2f} TRY')
                    
                    # Update trend arrow
                    last_value = self.currency_data[currency]['last_value']
                    if current_value > last_value:
                        widget.trend_label.setText('⬆')
                        widget.trend_label.setStyleSheet('color: #2ecc71;')
                    elif current_value < last_value:
                        widget.trend_label.setText('⬇')
                        widget.trend_label.setStyleSheet('color: #e74c3c;')
                    else:
                        widget.trend_label.setText('➡')
                        widget.trend_label.setStyleSheet('color: #2c3e50;')
                    
                    self.currency_data[currency]['last_value'] = current_value
            
            self.update_graph()
            
        except Exception as e:
            print(f"Veri güncelleme hatası: {e}")

    def setup_graph(self):
        self.graph_widget.setBackground('w')
        self.graph_widget.showGrid(x=True, y=True, alpha=0.3)
        styles = {'color':'#2c3e50', 'font-size':'12px'}
        self.graph_widget.setLabel('left', 'Değer (TRY)', **styles)
        self.graph_widget.setLabel('bottom', 'Zaman', **styles)
        self.graph_widget.addLegend()
        self.graph_widget.setAutoVisible(y=True)
        self.pen = pg.mkPen(color='#2196F3', width=2)
    
    def update_graph(self):
        self.graph_widget.clear()
        
        colors = {'USD': '#2196F3', 'EUR': '#4CAF50', 'GBP': '#9C27B0'}
        
        for currency, data in self.currency_data.items():
            values = data['values']
            
            if values:
                # Zaman indeksini oluştur
                times = list(range(len(values)))  # Basit bir indeks kullanıyoruz
                
                pen = pg.mkPen(color=colors[currency], width=2)
                self.graph_widget.plot(times, values, name=currency, pen=pen, symbol='o',
                                       symbolSize=5, symbolBrush=colors[currency])
        
        self.graph_widget.setTitle('Döviz Kurları Karşılaştırma', color='#2c3e50', size='14pt')
        
        # İstatistikleri güncelle
        stats_text = ""
        for currency in self.currency_data.keys():
            values = self.currency_data[currency]['values']
            if values:
                # Yüzde değişimi göster
                change_percent = ((values[-1] - values[0]) / values[0] * 100) if values[0] != 0 else 0
                stats_text += f"{currency}: {values[-1]:.2f} TRY ({change_percent:.2f}%)\n"
        
        self.current_stats.setText(stats_text.strip())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BorsaTakip()
    window.show()
    sys.exit(app.exec_())