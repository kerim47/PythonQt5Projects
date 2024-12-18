import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import math

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QLabel, QLineEdit, QPushButton, 
                             QTableWidget, QTableWidgetItem, 
                             QMessageBox, QGridLayout, QTabWidget,
                             QFileDialog, QCheckBox, QHBoxLayout, QProgressBar, QScrollArea
                             )
from PyQt5.QtGui import QFont, QPixmap, QImage
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class MetricsCalculationThread(QThread):
    """Thread for calculating metrics to prevent UI freezing"""
    metrics_ready = pyqtSignal(list)
    visualizations_ready = pyqtSignal(object)

    def __init__(self, tp, fp, fn, tn):
        super().__init__()
        self.tp = tp
        self.fp = fp
        self.fn = fn
        self.tn = tn

    def run(self):
        analyzer = ConfusionMatrixAnalyzer()
        metrics = analyzer.calculate_performance_metrics(self.tp, self.fp, self.fn, self.tn)
        
        # Create a temporary figure for visualizations
        cm = np.array([[self.tp, self.fn], [self.fp, self.tn]])
        visualizations = []
        viz_methods = [
            analyzer.create_confusion_matrix_heatmap,
            analyzer.create_confusion_matrix_percentage,
            analyzer.create_precision_recall_bar,
            analyzer.create_roc_curve_like_plot
        ]
        
        for method in viz_methods:
            try:
                fig = method(cm)
                visualizations.append(fig)
            except Exception as e:
                print(f"Visualization error: {e}")
        
        self.metrics_ready.emit(metrics)
        self.visualizations_ready.emit(visualizations)

class ConfusionMatrixAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Confusion Matrix Analyzer")
        self.setGeometry(100, 100, 1200, 900)
        self.showMaximized()
        
        # Dark and Light Theme Styles
        self.dark_theme = """
            QMainWindow { background-color: #2b2b2b; color: white; }
            QLabel { color: white; }
            QLineEdit { 
                background-color: #3c3f41; 
                color: white; 
                border: 1px solid #5a5a5a; 
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QTableWidget {
                background-color: #3c3f41;
                color: white;
                alternate-background-color: #2b2b2b;
            }
        """
        
        self.light_theme = """
            QMainWindow { background-color: #f4f4f4; }
            QLabel { color: #333; }
            QLineEdit { 
                background-color: white; 
                border: 1px solid #ccc; 
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
            }
            QTableWidget {
                background-color: white;
                alternate-background-color: #f0f0f0;
            }
        """
        
        self.current_theme = 'light'
        self.setup_ui()

    def setup_ui(self):
        # Apply current theme
        self.setStyleSheet(self.light_theme)
        
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Theme Toggle Section
        theme_layout = QHBoxLayout()
        self.theme_toggle = QCheckBox("Karanlik Tema")
        self.theme_toggle.stateChanged.connect(self.toggle_theme)
        theme_layout.addWidget(self.theme_toggle)
        theme_layout.addStretch()
        
        # Import CSV Button
        self.import_csv_btn = QPushButton("CSV Yukle")
        self.import_csv_btn.clicked.connect(self.import_csv)
        theme_layout.addWidget(self.import_csv_btn)
        
        main_layout.addLayout(theme_layout)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        main_layout.addWidget(self.progress_bar)

        # Confusion Matrix Input Section
        input_section = QWidget()
        input_layout = QGridLayout()
        input_section.setLayout(input_layout)

        # Input fields
        input_labels = [
            "True Positive (TP)", 
            "False Positive (FP)", 
            "False Negative (FN)", 
            "True Negative (TN)"
        ]

        # Initialize input_fields dictionary
        self.input_fields = {}
        for i, label in enumerate(input_labels):
            # Label
            lbl = QLabel(label + ":")
            lbl.setStyleSheet("font-weight: bold;")
            
            # Input field
            input_field = QLineEdit()
            input_field.setPlaceholderText("Negatif olmayan deger gir")
            input_field.textChanged.connect(self.validate_input)
            
            # Add to layout
            input_layout.addWidget(lbl, i, 0)
            input_layout.addWidget(input_field, i, 1)
            
            # Store reference
            self.input_fields[label] = input_field

        # Calculate Button
        self.calculate_btn = QPushButton("Metrikleri Hesapla")
        self.calculate_btn.clicked.connect(self.calculate_metrics)
        self.calculate_btn.setEnabled(False)  # Initially disabled
        input_layout.addWidget(self.calculate_btn, len(input_labels), 1)

        # Tab Widget for Metrics and Visualizations
        self.tab_widget = QTabWidget()
        
        # Metrics Tab
        metrics_tab = QWidget()
        metrics_layout = QVBoxLayout()
        metrics_tab.setLayout(metrics_layout)
        
        # Metrics Table
        self.metrics_table = QTableWidget(15, 3)  # Increased rows for more metrics
        self.metrics_table.setHorizontalHeaderLabels(["Metrik", "Deger", "Formul"])
        self.metrics_table.horizontalHeader().setStretchLastSection(True)
        self.metrics_table.setAlternatingRowColors(True)
        metrics_layout.addWidget(self.metrics_table)
        
        # Visualization Tab
        viz_tab = QWidget()
        viz_layout = QVBoxLayout()
        viz_tab.setLayout(viz_layout)
        
        # Scrollable visualization area
        self.viz_widget = QWidget()
        self.viz_layout = QVBoxLayout()
        self.viz_widget.setLayout(self.viz_layout)
        viz_layout.addWidget(self.viz_widget)

        self.tab_widget.addTab(metrics_tab, "Metrikler")
        self.tab_widget.addTab(viz_tab, "Görselleştirmeler")

        # Ana düzeni ekleyin
        main_layout.addWidget(QLabel("Karmaşıklık Matrisi Girdileri:"))

        main_layout.addWidget(input_section)
        main_layout.addWidget(self.tab_widget)

        # Setup tooltips
        self.setup_tooltips()

    def toggle_theme(self, state):
        """Toggle between dark and light themes"""
        self.current_theme = 'karanlik' if state == 2 else 'acik'
        self.setStyleSheet(self.dark_theme if self.current_theme == 'karanlik' else self.light_theme)

    def import_csv(self):
        """Import CSV with true and predicted labels"""
        file_name, _ = QFileDialog.getOpenFileName(self, 
                                                   "Open CSV File", 
                                                   "", 
                                                   "CSV Files (*.csv)")
        if file_name:
            try:
                df = pd.read_csv(file_name)
                # Assuming columns are 'true_label' and 'predicted_label'
                self.calculate_confusion_matrix_from_csv(df)
            except Exception as e:
                QMessageBox.warning(self, "Import Error", str(e))

    def calculate_confusion_matrix_from_csv(self, df):
        """Calculate confusion matrix from DataFrame"""
        from sklearn.metrics import confusion_matrix
        
        cm = confusion_matrix(df['true_label'], df['predicted_label'])
        
        # Handling multi-class scenario
        if cm.ndim > 1 and cm.shape[0] > 2:
            QMessageBox.information(self, "Multi-Class Detection", 
                                    "Multi-class confusion matrix detected!")
            # Future enhancement: Multi-class visualization
        else:
            # For binary classification
            tn, fp, fn, tp = cm.ravel()
            
            # Populate input fields
            self.input_fields["True Positive (TP)"].setText(str(tp))
            self.input_fields["False Positive (FP)"].setText(str(fp))
            self.input_fields["False Negative (FN)"].setText(str(fn))
            self.input_fields["True Negative (TN)"].setText(str(tn))
            
            # Trigger metrics calculation
            self.calculate_metrics()

    def setup_tooltips(self):
        """Add descriptive tooltips for metrics and UI elements"""
        tooltips = {
            "True Positive (TP)": "Doğru bir şekilde pozitif örneklerin tahmin edilmesi",
            "False Positive (FP)": "Negatif örneklerin yanlış bir şekilde pozitif olarak tahmin edilmesi",
            "False Negative (FN)": "Pozitif örneklerin yanlış bir şekilde negatif olarak tahmin edilmesi",
            "True Negative (TN)": "Doğru bir şekilde negatif örneklerin tahmin edilmesi"
        }
        
        for label, tooltip in tooltips.items():
            self.input_fields[label].setToolTip(tooltip)

    def validate_input(self):
        """Validate input fields and enable/disable calculate button"""
        try:
            # Check if all fields are non-negative integers
            inputs_valid = all(
                input_field.text().strip() and 
                int(input_field.text()) >= 0 
                for input_field in self.input_fields.values()
            )
            self.calculate_btn.setEnabled(inputs_valid)
        except ValueError:
            self.calculate_btn.setEnabled(False)

    def calculate_metrics(self):
        """Calculate metrics in a separate thread"""
        try:
            # Get input values
            tp = int(self.input_fields["True Positive (TP)"].text())
            fp = int(self.input_fields["False Positive (FP)"].text())
            fn = int(self.input_fields["False Negative (FN)"].text())
            tn = int(self.input_fields["True Negative (TN)"].text())

            # Check for zero total
            if tp + fp + fn + tn == 0:
                QMessageBox.warning(self, "Input Error", 
                    "At least one value must be non-zero.")
                return

            # Start metrics calculation in a separate thread
            self.progress_bar.show()
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            
            self.calc_thread = MetricsCalculationThread(tp, fp, fn, tn)
            self.calc_thread.metrics_ready.connect(self.update_metrics_table)
            self.calc_thread.visualizations_ready.connect(self.update_visualizations)
            self.calc_thread.finished.connect(self.calculation_complete)
            
            self.calc_thread.start()

        except ValueError:
            QMessageBox.warning(self, "Input Error", 
                "Please enter valid non-negative integer values for all fields.")

    def calculation_complete(self):
        """Called when metrics calculation is complete"""
        self.progress_bar.hide()
        self.progress_bar.setRange(0, 100)

    def update_metrics_table(self, metrics):
        """Update the metrics table with calculated values and formulas"""
        self.metrics_table.setRowCount(len(metrics))
        for i, (name, value, formula) in enumerate(metrics):
            # Metric name
            name_item = QTableWidgetItem(name)
            name_font = name_item.font()
            name_font.setBold(True)
            name_item.setFont(name_font)
            
            # Value - format differently for integers and floats
            if isinstance(value, int):
                value_item = QTableWidgetItem(str(value))
            else:
                value_item = QTableWidgetItem(f"{value:.4f}")
            
            # Formula
            formula_item = QTableWidgetItem(formula)
            
            self.metrics_table.setItem(i, 0, name_item)
            self.metrics_table.setItem(i, 1, value_item)
            self.metrics_table.setItem(i, 2, formula_item)
        
        # Auto-resize columns
        self.metrics_table.resizeColumnsToContents()

    def update_visualizations(self, visualizations):
        """Update visualization area with generated plots in a grid layout"""
        # Clear previous visualizations
        for i in reversed(range(self.viz_layout.count())): 
            widget = self.viz_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Create a scrollable area for visualizations
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # Create grid layout for visualizations inside the scrollable area
        grid_widget = QWidget()
        grid_layout = QGridLayout()
        grid_widget.setLayout(grid_layout)
        
        # Add visualizations to grid
        for i, fig in enumerate(visualizations):
            label = self.matplotlib_figure_to_qlabel(fig)
            row = i // 2  # Two visualizations per row
            col = i % 2
            grid_layout.addWidget(label, row, col)

        # Apply stretching to rows and columns to allow better resizing
        for row in range((len(visualizations) + 1) // 2):  # Number of rows
            grid_layout.setRowStretch(row, 1)

        grid_layout.setColumnStretch(0, 1)  # Allow column 1 to stretch
        grid_layout.setColumnStretch(1, 1)  # Allow column 2 to stretch
        
        # Set grid layout as the scrollable area widget
        scroll_area.setWidget(grid_widget)
        
        # Add scrollable area to main visualization layout
        self.viz_layout.addWidget(scroll_area)

    def calculate_performance_metrics(self, tp, fp, fn, tn):
        """enhanced performance metrics calculation"""
        def safe_division(numerator, denominator):
            return numerator / denominator if denominator != 0 else 0

        # total samples
        p = tp + fn  # positive samples
        n = tn + fp  # negative samples
        total = p + n

        # additional metrics
        balanced_accuracy = (safe_division(tp, p) + safe_division(tn, n)) / 2
        
        # cohen's kappa score
        observed_accuracy = (tp + tn) / total
        expected_accuracy = ((tp + fn) * (tp + fp) + (tn + fp) * (tn + fn)) / (total ** 2)
        kappa_score = (observed_accuracy - expected_accuracy) / (1 - expected_accuracy)

        metrics = [
            ("total samples", total, "p + n"),
            ("sensitivity (tpr)", safe_division(tp, p), "tp / (tp + fn)"),
            ("specificity (spc)", safe_division(tn, n), "tn / (tn + fp)"),
            ("precision (ppv)", safe_division(tp, tp + fp), "tp / (tp + fp)"),
            ("negative predictive value (npv)", safe_division(tn, tn + fn), "tn / (tn + fn)"),
            ("false positive rate (fpr)", safe_division(fp, n), "fp / (fp + tn)"),
            ("false negative rate (fnr)", safe_division(fn, p), "fn / (tp + fn)"),
            ("false discovery rate (fdr)", safe_division(fp, tp + fp), "fp / (fp + tp)"),
            ("accuracy (acc)", safe_division(tp + tn, total), "(tp + tn) / (p + n)"),
            ("f1 score", safe_division(2 * tp, 2 * tp + fp + fn), "2tp / (2tp + fp + fn)"),
            ("matthews correlation coefficient (mcc)", safe_division(tp * tn - fp * fn, math.sqrt((tp+fp)*(tp+fn)*(tn+fp)*(tn+fn))), "(tp*tn - fp*fn) / sqrt((tp+fp)(tp+fn)(tn+fp)(tn+fn))"),
            ("balanced accuracy", balanced_accuracy, "(tp / (tp + fn) + tn / (tn + fp)) / 2"),
            ("kappa score", kappa_score, "(observed_accuracy - expected_accuracy) / (1 - expected_accuracy)"),

        ]
        return metrics

    def create_visualizations(self, tp, fp, fn, tn):
        """Create multiple visualizations"""
        # Clear previous visualizations
        for i in reversed(range(self.viz_layout.count())): 
            widget = self.viz_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Confusion Matrix Data
        cm = np.array([[tp, fn], [fp, tn]])

        # Create visualizations
        for method in self.viz_methods:
            try:
                # Create figure and convert to QLabel
                fig = method(cm)
                label = self.matplotlib_figure_to_qlabel(fig)
                self.viz_layout.addWidget(label)
                plt.close(fig)  # Close the matplotlib figure to free memory
            except Exception as e:
                print(f"Visualization error: {e}")

    def create_confusion_matrix_heatmap(self, cm):
        """Create a basic heatmap of the confusion matrix"""
        plt.figure(figsize=(8, 6))
        plt.title('Karışıklık Matrisi - Ham Sayılar')
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=['Tahmin Edilen Pozitif', 'Tahmin Edilen Negatif'],
                    yticklabels=['Gerçek Pozitif', 'Gerçek Negatif'])
        plt.xlabel('Tahmin Edilen Etiket')
        plt.ylabel('Gerçek Etiket')
        plt.tight_layout()
        return plt.gcf()

    def create_confusion_matrix_percentage(self, cm):
        """Create a percentage heatmap of the confusion matrix"""
        total = np.sum(cm)
        cm_percent = cm / total * 100
        plt.figure(figsize=(8, 6))
        plt.title('Karışıklık Matrisi - Yüzde')
        sns.heatmap(cm_percent, annot=True, fmt='.2f', cmap='YlGnBu', 
                    xticklabels=['Tahmin Edilen Pozitif', 'Tahmin Edilen Negatif'],
                    yticklabels=['Gerçek Pozitif', 'Gerçek Negatif'])
        plt.xlabel('Tahmin Edilen Etiket')
        plt.ylabel('Gerçek Etiket')

        plt.tight_layout()
        return plt.gcf()

    def create_precision_recall_bar(self, cm):
        """Create a bar plot comparing precision and recall"""
        tp, fn, fp, tn = cm.ravel()
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        
        plt.figure(figsize=(8, 6))
        bars = plt.bar(['Hassasiyet', 'Duyarlılık'], [precision, recall], color=['blue', 'green'])
        plt.title('Hassasiyet ve Duyarlılık Karşılaştırması')
        plt.ylim(0, 1)
        plt.ylabel('Puan')

        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                     f'{height:.2f}', ha='center', va='bottom')
        
        plt.tight_layout()
        return plt.gcf()

    def create_roc_curve_like_plot(self, cm):
        """Create a ROC curve-like visualization"""
        tp, fn, fp, tn = cm.ravel()
        
        # Calculate rates
        tpr = tp / (tp + fn)  # True Positive Rate
        fpr = fp / (fp + tn)  # False Positive Rate
        
        plt.figure(figsize=(8, 6))
        plt.plot([0, fpr, 1], [0, tpr, 1], marker='o')
        plt.title('ROC Eğrisi Benzeri Görselleştirme')
        plt.xlabel('Yanlış Pozitif Oranı')
        plt.ylabel('Doğru Pozitif Oranı')
        plt.xlim(0, 1)
        plt.ylim(0, 1)
        plt.grid(True, linestyle='--')
        
        # Annotate points
        plt.annotate(f'(FPR, TPR)\n({fpr:.2f}, {tpr:.2f})', 
                     xy=(fpr, tpr), xytext=(0.5, 0.5),
                     arrowprops=dict(facecolor='black', shrink=0.05))
        
        plt.tight_layout()
        return plt.gcf()

    def matplotlib_figure_to_qlabel(self, figure):
        canvas = FigureCanvas(figure)
        canvas.draw()
        width, height = canvas.get_width_height()
        
        # DPI'yi arttırarak çözünürlüğü iyileştirme
        img = QImage(canvas.buffer_rgba(), width, height, QImage.Format_RGBA8888)
        label = QLabel()
        label.setPixmap(QPixmap.fromImage(img).scaled(width, height, Qt.KeepAspectRatio))
        return label


def main():
    app = QApplication(sys.argv)
    
    # Set application-wide font
    font = QFont()
    font.setFamily('Arial')
    font.setPointSize(10)
    app.setFont(font)
    
    main_window = ConfusionMatrixAnalyzer()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
