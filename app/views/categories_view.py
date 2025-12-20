from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QLineEdit, QComboBox, QDialog, 
                               QFormLayout, QScrollArea, QFrame, QGridLayout, QColorDialog)
from PySide6.QtCore import Qt
from app.controllers.category_controller import CategoryController

class CategoryDialog(QDialog):
    def __init__(self, parent=None, category=None):
        super().__init__(parent)
        self.setWindowTitle("Thêm Danh Mục" if not category else "Sửa Danh Mục")
        self.setFixedWidth(400)
        self.category = category
        self.selected_color = category.get('color', '#4CAF50') if category else '#4CAF50'
        
        layout = QFormLayout(self)
        
        self.name_input = QLineEdit()
        self.type_input = QComboBox()
        self.type_input.addItems(["Thu Nhập", "Chi Tiêu"])
        
        self.icon_input = QLineEdit()
        self.icon_input.setPlaceholderText("Biểu tượng (emoji, ví dụ: 🍔)")
        
        # Color Picker Button
        self.color_btn = QPushButton()
        self.color_btn.setFixedSize(50, 30)
        self.update_color_btn()
        self.color_btn.clicked.connect(self.pick_color)
        
        if category:
            self.name_input.setText(category.get('name', ''))
            type_text = "Thu Nhập" if category.get('type') == 'income' else "Chi Tiêu"
            self.type_input.setCurrentText(type_text)
            self.icon_input.setText(category.get('icon', ''))
            
        layout.addRow("Tên Danh Mục:", self.name_input)
        layout.addRow("Loại:", self.type_input)
        layout.addRow("Biểu Tượng:", self.icon_input)
        layout.addRow("Màu Sắc:", self.color_btn)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Lưu")
        save_btn.setProperty("class", "PrimaryButton")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Hủy")
        cancel_btn.setProperty("class", "SecondaryButton")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addRow(btn_layout)

    def pick_color(self):
        color = QColorDialog.getColor(initial=Qt.white, parent=self, title="Chọn Màu")
        if color.isValid():
            self.selected_color = color.name()
            self.update_color_btn()

    def update_color_btn(self):
        self.color_btn.setStyleSheet(f"background-color: {self.selected_color}; border: 1px solid #555; border-radius: 4px;")

    def get_data(self):
        return {
            "name": self.name_input.text(),
            "type_": "income" if self.type_input.currentText() == "Thu Nhập" else "expense",
            "icon": self.icon_input.text(),
            "color": self.selected_color
        }

class CategoriesView(QWidget):
    def __init__(self, controller: CategoryController):
        super().__init__()
        self.controller = controller
        self.controller.categories_changed.connect(self.refresh_categories)
        
        self.layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Danh Mục")
        title.setProperty("class", "SectionHeader")
        add_btn = QPushButton("+ Thêm Danh Mục")
        add_btn.setProperty("class", "PrimaryButton")
        add_btn.clicked.connect(self.open_add_dialog)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(add_btn)
        self.layout.addLayout(header_layout)
        
        # Scroll Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll)
        
        self.refresh_categories()

    def refresh_categories(self):
        # Clear existing
        for i in range(self.scroll_layout.count()):
            item = self.scroll_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
        
        categories = self.controller.get_all_categories()
        
        # Group by type
        income_cats = [c for c in categories if c['type'] == 'income']
        expense_cats = [c for c in categories if c['type'] == 'expense']
        
        if income_cats:
            self.add_category_section("Thu Nhập", income_cats)
        if expense_cats:
            self.add_category_section("Chi Tiêu", expense_cats)

    def add_category_section(self, title, categories):
        section_label = QLabel(title)
        section_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #AAAAAA; margin-top: 20px;")
        self.scroll_layout.addWidget(section_label)
        
        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setSpacing(16)
        
        row, col = 0, 0
        for cat in categories:
            card = self.create_category_card(cat)
            grid.addWidget(card, row, col)
            col += 1
            if col > 3: # 4 columns
                col = 0
                row += 1
        
        self.scroll_layout.addWidget(grid_widget)

    def create_category_card(self, category):
        card = QFrame()
        card.setProperty("class", "Card")
        card.setFixedSize(200, 120)
        
        layout = QVBoxLayout(card)
        
        # Icon & Name
        top_layout = QHBoxLayout()
        icon_label = QLabel(category.get('icon', ''))
        icon_label.setStyleSheet("font-size: 24px;")
        name_label = QLabel(category.get('name', 'Unknown'))
        name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        top_layout.addWidget(icon_label)
        top_layout.addWidget(name_label)
        top_layout.addStretch()
        
        # Color indicator
        color_indicator = QFrame()
        color_indicator.setFixedSize(12, 12)
        color_indicator.setStyleSheet(f"background-color: {category.get('color', '#4CAF50')}; border-radius: 6px;")
        top_layout.addWidget(color_indicator)
        
        layout.addLayout(top_layout)
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        edit_btn = QPushButton("Sửa")
        edit_btn.setProperty("class", "SecondaryButton")
        edit_btn.clicked.connect(lambda: self.open_edit_dialog(category))
        
        delete_btn = QPushButton("Xóa")
        delete_btn.setProperty("class", "DangerButton")
        delete_btn.clicked.connect(lambda: self.controller.delete_category(category['_id']))
        
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        layout.addLayout(btn_layout)
        
        return card

    def open_add_dialog(self):
        dialog = CategoryDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            self.controller.add_category(**data)

    def open_edit_dialog(self, category):
        dialog = CategoryDialog(self, category)
        if dialog.exec():
            data = dialog.get_data()
            self.controller.update_category(category['_id'], **data)
