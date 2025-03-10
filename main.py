import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QMessageBox, QComboBox, QLineEdit,
    QTextEdit, QScrollArea, QFrame, QInputDialog
)
from PyQt5.QtCore import Qt
from datetime import datetime

# 配置Matplotlib以在GUI中显示图形 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class DataAnalysisTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data  Analysis Tool")
        self.setGeometry(100, 100, 1200, 800)
        self.data = None
        self.current_plot = None

        # 创建主布局 
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # 添加功能按钮 
        button_layout = QHBoxLayout()
        self.load_button = QPushButton("Load Data")
        self.load_button.clicked.connect(self.load_data)
        button_layout.addWidget(self.load_button)

        self.clean_button = QPushButton("Clean Data")
        self.clean_button.clicked.connect(self.clean_data)
        button_layout.addWidget(self.clean_button)

        self.analyze_button = QPushButton("Analyze Data")
        self.analyze_button.clicked.connect(self.analyze_data)
        button_layout.addWidget(self.analyze_button)

        self.export_button = QPushButton("Export Data")
        self.export_button.clicked.connect(self.export_data)
        button_layout.addWidget(self.export_button)

        main_layout.addLayout(button_layout)

        # 添加数据预览区域 
        preview_frame = QFrame()
        preview_frame.setFrameShape(QFrame.Panel)
        preview_frame.setFrameShadow(QFrame.Raised)
        preview_layout = QVBoxLayout(preview_frame)

        self.preview_label = QLabel("Data Preview:")
        preview_layout.addWidget(self.preview_label)

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        preview_layout.addWidget(self.preview_text)

        main_layout.addWidget(preview_frame)

        # 添加图表显示区域 
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        main_layout.addWidget(self.canvas)

    def load_data(self):
        """加载数据文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Data", "",
            "Files (*.csv *.xlsx *.json)"
        )
        if not file_path:
            return

        try:
            if file_path.endswith('.csv'):
                self.data = pd.read_csv(file_path)
            elif file_path.endswith('.xlsx'):
                self.data = pd.read_excel(file_path)
            elif file_path.endswith('.json'):
                self.data = pd.read_json(file_path)

                # 更新数据预览
            self.preview_text.setPlainText(str(self.data.head(10)))

            # 更新字段类型识别 
            self.identify_field_types()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load data: {str(e)}")

    def identify_field_types(self):
        """自动识别字段类型"""
        if self.data is None:
            return

        field_types = {}
        for column in self.data.columns:
            dtype = self.data[column].dtype
            if dtype == 'object':
                unique_values = self.data[column].nunique()
                if unique_values <= 10:
                    field_types[column] = 'categorical'
                else:
                    field_types[column] = 'string'
            elif dtype in ['int64', 'float64']:
                field_types[column] = 'numeric'
            elif dtype == 'datetime64[ns]':
                field_types[column] = 'datetime'

        print("Field Types:")
        print(field_types)

    def clean_data(self):
        """数据清理"""
        if self.data is None:
            return

            # 处理缺失值
        self.handle_missing_values()

        # 删除重复值 
        self.remove_duplicates()

        # 检测异常值 
        self.detect_outliers()

    def handle_missing_values(self):
        """处理缺失值"""
        methods = ['mean', 'median', 'mode', 'custom']
        method, ok = QInputDialog.getItem(
            self, 'Missing Value Handling', 'Select Method:', methods, 0, False
        )
        if ok:
            if method == 'custom':
                fill_value, ok = QInputDialog.getText(
                    self, 'Custom Fill Value', 'Enter Fill Value:'
                )
                if ok:
                    for col in self.data.columns:
                        if self.data[col].dtype in ['int64', 'float64']:
                            self.data[col].fillna(float(fill_value), inplace=True)
                        else:
                            self.data[col].fillna(str(fill_value), inplace=True)
            else:
                for col in self.data.columns:
                    if self.data[col].dtype in ['int64', 'float64']:
                        if method == 'mean':
                            self.data[col].fillna(self.data[col].mean(), inplace=True)
                        elif method == 'median':
                            self.data[col].fillna(self.data[col].median(), inplace=True)
                        elif method == 'mode':
                            mode_val = self.data[col].mode().iloc[0]
                            self.data[col].fillna(mode_val, inplace=True)

    def remove_duplicates(self):
        """删除重复值"""
        strategy = ['first', 'last', 'all']
        strat, ok = QInputDialog.getItem(
            self, 'Remove Duplicates', 'Select Strategy:', strategy, 0, False
        )
        if ok:
            if strat == 'all':
                self.data.drop_duplicates(inplace=True)
            else:
                self.data.drop_duplicates(keep=strat, inplace=True)

    def detect_outliers(self):
        """检测异常值"""
        columns = self.data.select_dtypes(include=['int64', 'float64']).columns.tolist()
        column, ok = QInputDialog.getItem(
            self, 'Detect Outliers', 'Select Column:', columns, 0, False
        )
        if ok:
            z_scores = (self.data[column] - self.data[column].mean()) / self.data[column].std()
            threshold, ok = QInputDialog.getDouble(
                self, 'Outlier Threshold', 'Enter Z-Score Threshold:', 3.0
            )
            if ok:
                outliers = self.data[np.abs(z_scores) > threshold]
                print("Detected Outliers:")
                print(outliers)

    def analyze_data(self):
        """数据分析与可视化"""
        if self.data is None:
            return

            # 统计分析
        self.perform_statistical_analysis()

        # 数据可视化 
        self.visualize_data()

    def perform_statistical_analysis(self):
        """统计分析"""
        stats = self.data.describe()
        print("Basic Statistics:")
        print(stats)

    def visualize_data(self):
        """数据可视化"""
        chart_types = ['bar', 'line', 'pie', 'scatter', 'heatmap']
        chart_type, ok = QInputDialog.getItem(
            self, 'Chart Type', 'Select Chart Type:', chart_types, 0, False
        )
        if ok:
            columns = self.data.columns.tolist()
            x_col, ok = QInputDialog.getItem(
                self, 'X Axis', 'Select X Column:', columns, 0, False
            )
            y_col, ok = QInputDialog.getItem(
                self, 'Y Axis', 'Select Y Column:', columns, 0, False
            )

            if chart_type == 'bar':
                plt.figure(figsize=(10, 6))
                sns.barplot(x=x_col, y=y_col, data=self.data)
            elif chart_type == 'line':
                plt.figure(figsize=(10, 6))
                sns.lineplot(x=x_col, y=y_col, data=self.data)
            elif chart_type == 'pie':
                plt.figure(figsize=(10, 6))
                counts = self.data[y_col].value_counts()
                plt.pie(counts, labels=counts.index, autopct='%1.1f%%')
            elif chart_type == 'scatter':
                plt.figure(figsize=(10, 6))
                sns.scatterplot(x=x_col, y=y_col, data=self.data)
            elif chart_type == 'heatmap':
                plt.figure(figsize=(10, 6))
                corr = self.data.corr()
                sns.heatmap(corr, annot=True, cmap='coolwarm')

            plt.title(f"{chart_type.capitalize()}  Plot of {x_col} vs {y_col}")
            plt.tight_layout()
            plt.show()

    def export_data(self):
        """导出数据"""
        if self.data is None:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Data", "", "CSV Files (*.csv);;Excel Files (*.xlsx)"
        )
        if not file_path:
            return

        try:
            if file_path.endswith('.csv'):
                self.data.to_csv(file_path, index=False)
            elif file_path.endswith('.xlsx'):
                self.data.to_excel(file_path, index=False)

            QMessageBox.information(self, "Success", "Data exported successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export data: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DataAnalysisTool()
    window.show()
    sys.exit(app.exec_()) 