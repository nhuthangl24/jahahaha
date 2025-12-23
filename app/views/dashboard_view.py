from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QSpinBox, QFrame, QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget)
from PySide6.QtCore import Qt, QDate
from app.controllers.dashboard_controller import DashboardController
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class CategorySummaryWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 0)
        
        # Chart
        self.figure = Figure(figsize=(5, 4), dpi=100, facecolor='#1E1E1E')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: #1E1E1E; border-radius: 12px;")
        layout.addWidget(self.canvas, 2)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Danh Mục", "Số Tiền"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("QTableWidget { border: none; background-color: #1E1E1E; }")
        layout.addWidget(self.table, 1)

    def update_data(self, categories, title_pie, title_bar, bar_color='#64B5F6'):
        self.figure.clear()
        
        # Pie Chart (Left)
        ax1 = self.figure.add_subplot(121)
        ax1.set_facecolor('#1E1E1E')
        
        # Bar Chart (Right)
        ax2 = self.figure.add_subplot(122)
        ax2.set_facecolor('#1E1E1E')
        
        cat_names = [c['name'] for c in categories[:5]]
        amounts = [c['amount'] for c in categories[:5]]
        
        if cat_names:
            # Pie Chart
            wedges, texts, autotexts = ax1.pie(amounts, labels=cat_names, autopct='%1.1f%%', startangle=90, 
                                              textprops=dict(color="w"))
            ax1.set_title(title_pie, color='#FFFFFF')
            plt.setp(autotexts, size=8, weight="bold")
            plt.setp(texts, size=9)
            
            # Bar Chart
            bars = ax2.bar(cat_names, amounts, color=bar_color)
            ax2.tick_params(axis='x', colors='#AAAAAA', rotation=45, labelsize=8)
            ax2.tick_params(axis='y', colors='#AAAAAA', labelsize=8)
            ax2.spines['bottom'].set_color('#333333')
            ax2.spines['top'].set_color('#333333') 
            ax2.spines['right'].set_color('#333333')
            ax2.spines['left'].set_color('#333333')
            ax2.set_title(title_bar, color='#FFFFFF')
        else:
            ax1.text(0.5, 0.5, "Không có dữ liệu", ha='center', va='center', color='#AAAAAA')
            ax2.text(0.5, 0.5, "Không có dữ liệu", ha='center', va='center', color='#AAAAAA')
            
        self.figure.tight_layout()
        self.canvas.draw()
        
        # Update Table
        self.table.setRowCount(len(categories))
        for row, cat in enumerate(categories):
            self.table.setItem(row, 0, QTableWidgetItem(f"{cat['icon']} {cat['name']}"))
            self.table.setItem(row, 1, QTableWidgetItem(f"{cat['amount']:,.0f} ₫"))

class DashboardView(QWidget):
    def __init__(self, controller: DashboardController):
        super().__init__()
        self.controller = controller
        
        self.layout = QVBoxLayout(self)
        
        # Header & Controls
        header_layout = QHBoxLayout()
        title = QLabel("Bảng Điều Khiển")
        title.setProperty("class", "SectionHeader")
        
        self.month_selector = QSpinBox()
        self.month_selector.setRange(1, 12)
        self.month_selector.setValue(QDate.currentDate().month())
        self.month_selector.setPrefix("Tháng: ")
        self.month_selector.valueChanged.connect(self.refresh_dashboard)
        
        self.year_selector = QSpinBox()
        self.year_selector.setRange(2000, 2100)
        self.year_selector.setValue(QDate.currentDate().year())
        self.year_selector.setPrefix("Năm: ")
        self.year_selector.valueChanged.connect(self.refresh_dashboard)
        
        refresh_btn = QPushButton("Làm Mới")
        refresh_btn.setProperty("class", "SecondaryButton")
        refresh_btn.clicked.connect(self.refresh_dashboard)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.month_selector)
        header_layout.addWidget(self.year_selector)
        header_layout.addWidget(refresh_btn)
        self.layout.addLayout(header_layout)
        
        # Metrics Cards
        self.metrics_layout = QHBoxLayout()
        self.income_card = self.create_metric_card("Tổng Thu Nhập", "0 ₫")
        self.expense_card = self.create_metric_card("Tổng Chi Tiêu", "0 ₫")
        self.net_card = self.create_metric_card("Kết Quả", "0 ₫")
        self.budget_card = self.create_metric_card("Ngân Sách Còn Lại", "0 ₫")
        
        self.metrics_layout.addWidget(self.income_card)
        self.metrics_layout.addWidget(self.expense_card)
        self.metrics_layout.addWidget(self.net_card)
        self.metrics_layout.addWidget(self.budget_card)
        self.layout.addLayout(self.metrics_layout)
        
        # Tabs for Charts
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 0; }
            QTabBar::tab { background: #333; color: #AAA; padding: 8px 16px; border-top-left-radius: 4px; border-top-right-radius: 4px; }
            QTabBar::tab:selected { background: #1E1E1E; color: #FFF; font-weight: bold; }
        """)
        
        self.expense_tab = CategorySummaryWidget()
        self.income_tab = CategorySummaryWidget()
        self.debt_tab = CategorySummaryWidget()
        
        self.tabs.addTab(self.expense_tab, "Chi Tiêu")
        self.tabs.addTab(self.income_tab, "Thu Nhập")
        self.tabs.addTab(self.debt_tab, "Đi vay / Cho vay")
        
        self.layout.addWidget(self.tabs)
        
        self.refresh_dashboard()

    def create_metric_card(self, title, value):
        card = QFrame()
        card.setProperty("class", "Card")
        layout = QVBoxLayout(card)
        
        title_lbl = QLabel(title)
        title_lbl.setProperty("class", "CardTitle")
        
        value_lbl = QLabel(value)
        value_lbl.setProperty("class", "CardValue")
        value_lbl.setObjectName("ValueLabel") # For easy finding later
        
        layout.addWidget(title_lbl)
        layout.addWidget(value_lbl)
        return card

    def update_metric_card(self, card, value, color=None):
        lbl = card.findChild(QLabel, "ValueLabel")
        lbl.setText(value)
        if color:
            lbl.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: bold; margin-top: 4px;")
        else:
            lbl.setStyleSheet("font-size: 24px; color: #FFFFFF; font-weight: bold; margin-top: 4px;")

    def refresh_dashboard(self):
        month = self.month_selector.value()
        year = self.year_selector.value()
        
        data = self.controller.get_dashboard_data(month, year)
        
        self.update_metric_card(self.income_card, f"{data['total_income']:,.0f} ₫")
        self.update_metric_card(self.expense_card, f"{data['total_expense']:,.0f} ₫")
        
        net_color = "#4CAF50" if data['net_result'] >= 0 else "#CF6679"
        self.update_metric_card(self.net_card, f"{data['net_result']:,.0f} ₫", net_color)
        
        self.update_metric_card(self.budget_card, f"{data['remaining_budget']:,.0f} ₫")
        
        # Update Tabs
        self.expense_tab.update_data(data['expense_categories'], "Tỷ Lệ Chi Tiêu", "Chi Tiêu Theo Danh Mục", "#EF5350")
        self.income_tab.update_data(data['income_categories'], "Tỷ Lệ Thu Nhập", "Thu Nhập Theo Danh Mục", "#66BB6A")
        self.debt_tab.update_data(data['debt_categories'], "Tỷ Lệ Vay/Nợ", "Vay/Nợ Theo Danh Mục", "#42A5F5")
