from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QSpinBox, QProgressBar, QFrame, QLineEdit,
                               QDialog, QFormLayout, QDialogButtonBox, QScrollArea, QComboBox, QMessageBox)
from PySide6.QtCore import Qt, QDate
from app.controllers.budget_controller import BudgetController

class BudgetDialog(QDialog):
    def __init__(self, parent=None, current_amount=0.0, title="Đặt Ngân Sách"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedWidth(350)
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("0")
        self.amount_input.setText(f"{int(current_amount):,}")
        self.amount_input.textChanged.connect(self.format_amount)
        
        form_layout.addRow("Số Tiền:", self.amount_input)
        layout.addLayout(form_layout)
        
        # Buttons
        btn_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.validate_and_accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)
        
    def format_amount(self, text):
        if not text: return
        clean = ''.join(filter(str.isdigit, text))
        if clean:
            formatted = "{:,}".format(int(clean))
            if text != formatted:
                self.amount_input.blockSignals(True)
                self.amount_input.setText(formatted)
                self.amount_input.setCursorPosition(len(formatted))
                self.amount_input.blockSignals(False)

    def validate_and_accept(self):
        amount_text = self.amount_input.text().replace(",", "")
        try:
            amount = float(amount_text)
            if amount < 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập số tiền hợp lệ.")
            self.amount_input.setFocus()
            return
        self.accept()

    def get_amount(self):
        text = self.amount_input.text().replace(",", "")
        return float(text) if text else 0.0

class CategoryBudgetDialog(BudgetDialog):
    def __init__(self, parent=None, all_categories=[], current_cat_id=None, current_amount=0.0):
        super().__init__(parent, current_amount, "Đặt Ngân Sách Danh Mục")
        self.all_categories = all_categories
        
        self.type_input = QComboBox()
        self.type_input.addItem("Chi Tiêu", "expense")
        self.type_input.addItem("Đi vay / Cho vay", "incurdebt")
        
        self.category_input = QComboBox()
        
        layout = self.layout()
        form_layout = layout.itemAt(0).layout()
        
        form_layout.insertRow(0, "Danh Mục:", self.category_input)
        form_layout.insertRow(0, "Loại:", self.type_input)
        
        self.type_input.currentIndexChanged.connect(self.update_categories)
        self.update_categories()
            
        if current_cat_id:
            # Find the category to set initial state
            cat_data = next((c for c in all_categories if c['_id'] == current_cat_id), None)
            if cat_data:
                # Set Type
                type_index = self.type_input.findData(cat_data['type'])
                if type_index >= 0:
                    self.type_input.setCurrentIndex(type_index)
                
                # Set Category
                cat_index = self.category_input.findData(current_cat_id)
                if cat_index >= 0:
                    self.category_input.setCurrentIndex(cat_index)
            
            self.type_input.setEnabled(False)
            self.category_input.setEnabled(False)

    def update_categories(self):
        current_type = self.type_input.currentData()
        self.category_input.clear()
        
        filtered_cats = [c for c in self.all_categories if c['type'] == current_type]
        for cat in filtered_cats:
            self.category_input.addItem(f"{cat.get('icon', '')} {cat['name']}", cat['_id'])

    def validate_and_accept(self):
        if not self.category_input.currentData():
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn danh mục.")
            self.category_input.setFocus()
            return
        super().validate_and_accept()

    def get_category_id(self):
        return self.category_input.currentData()

class BudgetsView(QWidget):
    def __init__(self, controller: BudgetController):
        super().__init__()
        self.controller = controller
        self.controller.budget_changed.connect(self.refresh_budget)
        
        self.layout = QVBoxLayout(self)
        
        # Header & Controls
        header_layout = QHBoxLayout()
        title = QLabel("Quản Lý Ngân Sách")
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
        
        # Scroll Area for Content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(20)
        self.content_layout.setAlignment(Qt.AlignTop)
        
        scroll.setWidget(self.content_widget)
        self.layout.addWidget(scroll)
        
        self.refresh_budget()

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

    def refresh_budget(self):
        # Clear existing content
        self.clear_layout(self.content_layout)
            
        month = self.month_selector.value()
        year = self.year_selector.value()
        
        data = self.controller.get_budget_status(month, year)
        
        # 1. Total Budget Card
        total_card = self.create_total_budget_card(data)
        self.content_layout.addWidget(total_card)
        
        # 2. Category Budgets Header
        cat_header = QHBoxLayout()
        cat_title = QLabel("Chi Tiết Theo Danh Mục")
        cat_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #AAA; margin-top: 20px;")
        
        add_btn = QPushButton("+ Thêm Ngân Sách Danh Mục")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(lambda: self.open_category_budget_dialog())
        
        cat_header.addWidget(cat_title)
        cat_header.addStretch()
        cat_header.addWidget(add_btn)
        self.content_layout.addLayout(cat_header)
        
        # 3. Category List
        if not data['categories']:
            empty_lbl = QLabel("Chưa có ngân sách danh mục nào.")
            empty_lbl.setAlignment(Qt.AlignCenter)
            empty_lbl.setStyleSheet("color: #666; padding: 20px;")
            self.content_layout.addWidget(empty_lbl)
        else:
            for cat_data in data['categories']:
                card = self.create_category_card(cat_data)
                self.content_layout.addWidget(card)

    def create_total_budget_card(self, data):
        card = QFrame()
        card.setProperty("class", "Card")
        layout = QVBoxLayout(card)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("Tổng Ngân Sách Tháng")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        edit_btn = QPushButton("Sửa")
        edit_btn.setFixedSize(60, 30)
        edit_btn.clicked.connect(lambda: self.open_total_budget_dialog(data['total_budget_limit']))
        
        header.addWidget(title)
        header.addStretch()
        header.addWidget(edit_btn)
        layout.addLayout(header)
        
        # Info
        info_layout = QHBoxLayout()
        limit_lbl = QLabel(f"Hạn Mức: {data['total_budget_limit']:,.0f} ₫")
        spent_lbl = QLabel(f"Đã Chi: {data['total_spent']:,.0f} ₫")
        remaining_lbl = QLabel(f"Còn Lại: {data['total_remaining']:,.0f} ₫")
        
        remaining_lbl.setStyleSheet(f"color: {'#4CAF50' if data['total_remaining'] >= 0 else '#CF6679'}; font-weight: bold;")
        
        info_layout.addWidget(limit_lbl)
        info_layout.addStretch()
        info_layout.addWidget(spent_lbl)
        info_layout.addStretch()
        info_layout.addWidget(remaining_lbl)
        layout.addLayout(info_layout)
        
        # Progress Bar
        progress = QProgressBar()
        progress.setTextVisible(True)
        progress.setFormat("%p%")
        progress.setValue(min(100, max(0, int(data['total_percentage']))))
        
        color = "#4CAF50" if data['total_remaining'] >= 0 else "#CF6679"
        progress.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #444;
                border-radius: 5px;
                text-align: center;
                height: 20px;
                background-color: #222;
            }}
            QProgressBar::chunk {{
                background-color: {color};
            }}
        """)
        layout.addWidget(progress)
        
        return card

    def create_category_card(self, data):
        card = QFrame()
        card.setStyleSheet("background-color: #252526; border-radius: 8px; padding: 10px;")
        layout = QVBoxLayout(card)
        
        # Header
        header = QHBoxLayout()
        icon_lbl = QLabel(data['icon'])
        name_lbl = QLabel(data['name'])
        name_lbl.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        edit_btn = QPushButton("Sửa")
        edit_btn.setFixedSize(60, 35)
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setStyleSheet("background-color: green; border: none; color: white; border-radius: 4px;")
        edit_btn.clicked.connect(lambda: self.open_category_budget_dialog(data['id'], data['limit']))
        
        del_btn = QPushButton("Xóa")
        del_btn.setFixedSize(60, 35)
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.setStyleSheet("background-color: #C0392B; border: none; color: white; border-radius: 4px;")
        del_btn.clicked.connect(lambda: self.delete_category_budget(data['id']))
        
        header.addWidget(icon_lbl)
        header.addWidget(name_lbl)
        header.addStretch()
        header.addWidget(edit_btn)
        header.addWidget(del_btn)
        layout.addLayout(header)
        
        # Progress Bar
        progress = QProgressBar()
        progress.setTextVisible(False)
        progress.setValue(min(100, max(0, int(data['percentage']))))
        
        color = "#4CAF50"
        if data['percentage'] > 100: color = "#CF6679"
        elif data['percentage'] > 80: color = "#FF9800"
            
        progress.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 3px;
                background-color: #333;
                height: 6px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
        """)
        layout.addWidget(progress)
        
        # Details
        details = QHBoxLayout()
        details.addWidget(QLabel(f"Đã chi: {data['spent']:,.0f} ₫"))
        details.addStretch()
        
        limit_text = f" / {data['limit']:,.0f} ₫" if data['limit'] > 0 else " (Chưa đặt ngân sách)"
        limit_lbl = QLabel(limit_text)
        limit_lbl.setStyleSheet("color: #888;")
        details.addWidget(limit_lbl)
        
        layout.addLayout(details)
        
        return card

    def open_total_budget_dialog(self, current_amount):
        dialog = BudgetDialog(self, current_amount, "Đặt Tổng Ngân Sách")
        if dialog.exec():
            month = self.month_selector.value()
            year = self.year_selector.value()
            self.controller.set_total_budget(month, year, dialog.get_amount())

    def open_category_budget_dialog(self, cat_id=None, current_amount=0.0):
        categories = self.controller.get_all_categories()
        
        dialog = CategoryBudgetDialog(self, categories, cat_id, current_amount)
        if dialog.exec():
            month = self.month_selector.value()
            year = self.year_selector.value()
            selected_cat_id = dialog.get_category_id()
            amount = dialog.get_amount()
            
            if selected_cat_id:
                self.controller.set_category_budget(month, year, selected_cat_id, amount)

    def delete_category_budget(self, cat_id):
        month = self.month_selector.value()
        year = self.year_selector.value()
        self.controller.remove_category_budget(month, year, cat_id)
