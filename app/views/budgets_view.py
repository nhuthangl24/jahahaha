from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QSpinBox, QDoubleSpinBox, QProgressBar, QFrame , QLineEdit)
from PySide6.QtCore import Qt, QDate
from app.controllers.budget_controller import BudgetController
class BudgetsView(QWidget):
    def __init__(self, controller: BudgetController):
        super().__init__()
        self.controller = controller
        self.controller.budget_changed.connect(self.refresh_budget)
        
        self.layout = QVBoxLayout(self)
        
        # Header & Controls
        header_layout = QHBoxLayout()
        title = QLabel("Ngân Sách")
        title.setProperty("class", "SectionHeader")
        
        self.month_selector = QSpinBox()
        self.month_selector.setRange(1, 12)
        self.month_selector.setValue(QDate.currentDate().month())
        self.month_selector.setPrefix("Tháng: ")
        self.month_selector.valueChanged.connect(self.refresh_budget)
        
        self.year_selector = QSpinBox()
        self.year_selector.setRange(2000, 2100)
        self.year_selector.setValue(QDate.currentDate().year())
        self.year_selector.setPrefix("Năm: ")
        self.year_selector.valueChanged.connect(self.refresh_budget)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.month_selector)
        header_layout.addWidget(self.year_selector)
        self.layout.addLayout(header_layout)
        
        # Budget Setting
        setting_layout = QHBoxLayout()
        setting_layout.addWidget(QLabel("Ngân Sách Tháng:"))
        self.budget_input = QLineEdit()
        self.budget_input.setPlaceholderText("0")
        self.budget_input.textChanged.connect(self.format_amount)
        
        save_btn = QPushButton("Đặt Ngân Sách")
        save_btn.setProperty("class", "PrimaryButton")
        save_btn.clicked.connect(self.save_budget)
        
        setting_layout.addWidget(self.budget_input)
        setting_layout.addWidget(save_btn)
        setting_layout.addStretch()
        self.layout.addLayout(setting_layout)
        
        self.layout.addSpacing(20)
        
        # Overview Card
        self.overview_card = QFrame()
        self.overview_card.setProperty("class", "Card")
        card_layout = QVBoxLayout(self.overview_card)
        
        self.spent_label = QLabel("Đã Chi: 0 ₫")
        self.spent_label.setStyleSheet("font-size: 18px;")
        self.remaining_label = QLabel("Còn Lại: 0 ₫")
        self.remaining_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #333;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 20px;
            }
        """)
        
        card_layout.addWidget(self.spent_label)
        card_layout.addWidget(self.remaining_label)
        card_layout.addWidget(self.progress_bar)
        
        self.layout.addWidget(self.overview_card)
        self.layout.addStretch()
        
        self.refresh_budget()


    def format_amount(self, text):
        if not text:
            return
            
        # Remove commas and non-digits
        clean_text = ''.join(filter(str.isdigit, text))
        
        if clean_text:
            # Format with commas
            formatted = "{:,}".format(int(clean_text))
            
            if text != formatted:
                self.budget_input.blockSignals(True)
                self.budget_input.setText(formatted)
                # Move cursor to end
                self.budget_input.setCursorPosition(len(formatted))
                self.budget_input.blockSignals(False)

    def save_budget(self):
        month = self.month_selector.value()
        year = self.year_selector.value()
        
        # Lấy giá trị từ QLineEdit và bỏ dấu phẩy
        amount_text = self.budget_input.text().replace(",", "")
        amount = float(amount_text or 0)
        
        self.controller.set_budget(month, year, amount)

    def refresh_budget(self):
        month = self.month_selector.value()
        year = self.year_selector.value()
        
        data = self.controller.get_budget_status(month, year)
        
        # Hiển thị lại giá trị có dấu phẩy
        self.budget_input.setText(f"{data['total_budget']:,.0f}")
        
        self.spent_label.setText(f"Đã Chi: {data['total_spent']:,.0f} ₫")
        self.remaining_label.setText(f"Còn Lại: {data['remaining']:,.0f} ₫")
        
        percent = min(100, max(0, int(data['percentage'])))
        self.progress_bar.setValue(percent)
        
        if data['remaining'] < 0:
            self.remaining_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #CF6679;")
            self.progress_bar.setStyleSheet(self.progress_bar.styleSheet().replace("#4CAF50", "#CF6679"))
        else:
            self.remaining_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50;")
            self.progress_bar.setStyleSheet(self.progress_bar.styleSheet().replace("#CF6679", "#4CAF50"))
