from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QDialog, QFormLayout, QLineEdit, 
                               QComboBox, QDateEdit, QRadioButton, QButtonGroup, QMessageBox, QCheckBox)
from PySide6.QtCore import Qt, QDate
from app.controllers.transaction_controller import TransactionController

class TransactionDialog(QDialog):
    def __init__(self, controller, parent=None, transaction=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Thêm Giao Dịch" if not transaction else "Sửa Giao Dịch")
        self.setFixedWidth(450)
        self.transaction = transaction
        
        layout = QFormLayout(self)
        
        # Type
        self.type_group = QButtonGroup(self)
        self.income_radio = QRadioButton("Thu nhập")
        self.expense_radio = QRadioButton("Chi tiêu")
        self.expense_radio.setChecked(True)
        self.type_group.addButton(self.income_radio)
        self.type_group.addButton(self.expense_radio)
        
        type_layout = QHBoxLayout()
        type_layout.addWidget(self.income_radio)
        type_layout.addWidget(self.expense_radio)
        layout.addRow("Loại:", type_layout)
        
        # Date
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setDisplayFormat("dd/MM/yyyy")
        layout.addRow("Ngày:", self.date_input)
        
        # Amount
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("0")
        self.amount_input.textChanged.connect(self.format_amount)
        layout.addRow("Số Tiền:", self.amount_input)
        
        # Category
        self.category_input = QComboBox()
        self.categories = self.controller.get_categories()
        self.update_categories()
        
        # Connect radio buttons to update categories
        self.income_radio.toggled.connect(self.update_categories)
        layout.addRow("Danh Mục:", self.category_input)
        
        # Payment Method
        self.payment_input = QComboBox()
        self.payment_input.addItem("Tiền mặt", "cash")
        self.payment_input.addItem("Chuyển khoản", "bank")
        self.payment_input.addItem("Thẻ tín dụng", "credit")
        self.payment_input.addItem("Ví điện tử", "ewallet")
        layout.addRow("Phương Thức:", self.payment_input)
        
        # Note
        self.note_input = QLineEdit()
        layout.addRow("Ghi Chú:", self.note_input)
        
        # Tags
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("tag1, tag2")
        layout.addRow("Thẻ (Tags):", self.tags_input)
        
        # Pre-fill if editing
        if transaction:
            if transaction['type'] == 'income':
                self.income_radio.setChecked(True)
            else:
                self.expense_radio.setChecked(True)
            
            self.date_input.setDate(QDate.fromString(transaction['date'], "yyyy-MM-dd"))
            
            # Format amount with commas for display
            amount_val = int(transaction['amount'])
            self.amount_input.setText("{:,}".format(amount_val))
            
            # Find payment method index
            index = self.payment_input.findData(transaction['payment_method'])
            if index >= 0:
                self.payment_input.setCurrentIndex(index)
                
            self.note_input.setText(transaction.get('note', ''))
            self.tags_input.setText(", ".join(transaction.get('tags', [])))
            
            # Set category after updating list
            self.update_categories()
            index = self.category_input.findData(transaction.get('category_id'))
            if index >= 0:
                self.category_input.setCurrentIndex(index)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Lưu")
        self.save_btn.setProperty("class", "PrimaryButton")
        self.save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Hủy")
        cancel_btn.setProperty("class", "SecondaryButton")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(self.save_btn)
        layout.addRow(btn_layout)

    def format_amount(self, text):
        if not text:
            return
            
        # Remove commas and non-digits
        clean_text = ''.join(filter(str.isdigit, text))
        
        if clean_text:
            # Format with commas
            formatted = "{:,}".format(int(clean_text))
            
            if text != formatted:
                self.amount_input.blockSignals(True)
                self.amount_input.setText(formatted)
                # Move cursor to end
                self.amount_input.setCursorPosition(len(formatted))
                self.amount_input.blockSignals(False)

    def update_categories(self):
        current_type = "income" if self.income_radio.isChecked() else "expense"
        self.category_input.clear()
        found = False
        for cat in self.categories:
            if cat['type'] == current_type:
                self.category_input.addItem(f"{cat.get('icon', '')} {cat['name']}", cat['_id'])
                found = True
        
        if not found:
            self.category_input.addItem("⚠️ Chưa có danh mục", None)
            self.category_input.setToolTip("Vui lòng thêm danh mục ở tab Danh Mục trước")

    def get_data(self):
        # Strip commas from amount
        amount_text = self.amount_input.text().replace(",", "")
        
        return {
            "date": self.date_input.date().toString("yyyy-MM-dd"),
            "amount": float(amount_text or 0),
            "type": "income" if self.income_radio.isChecked() else "expense",
            "category_id": self.category_input.currentData(),
            "payment_method": self.payment_input.currentData(),
            "note": self.note_input.text(),
            "tags": [t.strip() for t in self.tags_input.text().split(",") if t.strip()]
        }
    
    def accept(self):
        # Validate category
        if self.category_input.currentData() is None:
            QMessageBox.warning(self, "Thiếu Danh Mục", "Vui lòng chọn danh mục hợp lệ. Nếu chưa có, hãy tạo danh mục mới.")
            return
        super().accept()

class TransactionsView(QWidget):
    def __init__(self, controller: TransactionController):
        super().__init__()
        self.controller = controller
        self.controller.transactions_changed.connect(self.refresh_transactions)
        
        self.layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Giao Dịch")
        title.setProperty("class", "SectionHeader")
        add_btn = QPushButton("+ Thêm Giao Dịch")
        add_btn.setProperty("class", "PrimaryButton")
        add_btn.clicked.connect(self.open_add_dialog)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(add_btn)
        self.layout.addLayout(header_layout)
        
        # Filter Section
        filter_layout = QHBoxLayout()
        
        self.filter_date_cb = QCheckBox("Lọc ngày")
        self.filter_date_cb.toggled.connect(self.toggle_date_filters)
        
        self.start_date_filter = QDateEdit()
        self.start_date_filter.setCalendarPopup(True)
        self.start_date_filter.setDisplayFormat("dd/MM/yyyy")
        self.start_date_filter.setDate(QDate.currentDate().addMonths(-1))
        self.start_date_filter.setEnabled(False)
        self.start_date_filter.dateChanged.connect(self.apply_filter)

        self.end_date_filter = QDateEdit()
        self.end_date_filter.setCalendarPopup(True)
        self.end_date_filter.setDisplayFormat("dd/MM/yyyy")
        self.end_date_filter.setDate(QDate.currentDate())
        self.end_date_filter.setEnabled(False)
        self.end_date_filter.dateChanged.connect(self.apply_filter)
        
        self.category_filter = QLineEdit()
        self.category_filter.setPlaceholderText("Tên danh mục...")
        self.category_filter.textChanged.connect(self.apply_filter)
        
        self.note_filter = QLineEdit()
        self.note_filter.setPlaceholderText("Ghi chú...")
        self.note_filter.textChanged.connect(self.apply_filter)
        
        clear_filter_btn = QPushButton("Xóa Lọc")
        clear_filter_btn.clicked.connect(self.clear_filter)
        
        filter_layout.addWidget(self.filter_date_cb)
        filter_layout.addWidget(self.start_date_filter)
        filter_layout.addWidget(QLabel("-"))
        filter_layout.addWidget(self.end_date_filter)
        filter_layout.addWidget(self.category_filter)
        filter_layout.addWidget(self.note_filter)
        filter_layout.addWidget(clear_filter_btn)
        
        self.layout.addLayout(filter_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Ngày", "Loại", "Danh Mục", "Số Tiền", "Thanh Toán", "Ghi Chú", "Hành Động"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        self.table.setColumnWidth(6, 120)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(50)
        self.layout.addWidget(self.table)
        
        self.refresh_transactions()

    def refresh_transactions(self):
        # Check if filters are active
        if self.filter_date_cb.isChecked() or self.category_filter.text().strip() or self.note_filter.text().strip():
            self.apply_filter()
        else:
            transactions = self.controller.get_all_transactions()
            self.update_table(transactions)

    def update_table(self, transactions):
        self.table.setRowCount(len(transactions))
        
        payment_map = {
            "cash": "Tiền mặt",
            "bank": "Chuyển khoản",
            "credit": "Thẻ tín dụng",
            "ewallet": "Ví điện tử"
        }
        
        for row, t in enumerate(transactions):
            # Date
            date_obj = QDate.fromString(t['date'], "yyyy-MM-dd")
            self.table.setItem(row, 0, QTableWidgetItem(date_obj.toString("dd/MM/yyyy")))
            
            # Type
            type_str = "Thu nhập" if t['type'] == 'income' else "Chi tiêu"
            self.table.setItem(row, 1, QTableWidgetItem(type_str))
            
            # Category
            cat_item = QTableWidgetItem(f"{t.get('category_icon', '')} {t.get('category_name', '')}")
            self.table.setItem(row, 2, cat_item)
            
            # Amount
            amount_str = f"{t['amount']:,.0f} ₫"
            amount_item = QTableWidgetItem(amount_str)
            if t['type'] == 'income':
                amount_item.setForeground(Qt.green)
            else:
                amount_item.setForeground(Qt.red)
            self.table.setItem(row, 3, amount_item)
            
            # Payment Method
            payment_display = payment_map.get(t['payment_method'], t['payment_method'])
            self.table.setItem(row, 4, QTableWidgetItem(payment_display))
            
            # Note
            self.table.setItem(row, 5, QTableWidgetItem(t.get('note', '')))
            
            # Actions
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(2, 2, 2, 2)
            action_layout.setSpacing(4)
            
            edit_btn = QPushButton("Sửa")
            edit_btn.setToolTip("Sửa")
            edit_btn.setCursor(Qt.PointingHandCursor)
            edit_btn.setFixedSize(50, 28)
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2C3E50;
                    color: white;
                    border: 1px solid #34495E;
                    border-radius: 4px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #34495E;
                }
            """)
            edit_btn.clicked.connect(lambda checked, tr=t: self.open_edit_dialog(tr))
            
            del_btn = QPushButton("Xóa")
            del_btn.setToolTip("Xóa")
            del_btn.setCursor(Qt.PointingHandCursor)
            del_btn.setFixedSize(50, 28)
            del_btn.setStyleSheet("""
                QPushButton {
                    background-color: #C0392B;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #E74C3C;
                }
            """)
            del_btn.clicked.connect(lambda checked, tr=t: self.controller.delete_transaction(tr['_id']))
            
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(del_btn)
            self.table.setCellWidget(row, 6, action_widget)

    def toggle_date_filters(self, checked):
        self.start_date_filter.setEnabled(checked)
        self.end_date_filter.setEnabled(checked)
        self.apply_filter()

    def apply_filter(self):
        start_date = None
        end_date = None
        
        if self.filter_date_cb.isChecked():
            start_date = self.start_date_filter.date().toString("yyyy-MM-dd")
            end_date = self.end_date_filter.date().toString("yyyy-MM-dd")
            
        category_name = self.category_filter.text().strip()
        note = self.note_filter.text().strip()
        
        transactions = self.controller.filter_transactions(start_date, end_date, category_name, note)
        self.update_table(transactions)

    def clear_filter(self):
        self.filter_date_cb.setChecked(False)
        self.category_filter.clear()
        self.note_filter.clear()
        self.refresh_transactions()

    def open_add_dialog(self):
        dialog = TransactionDialog(self.controller, self)
        if dialog.exec():
            data = dialog.get_data()
            # Map 'type' to 'type_' for controller method which avoids shadowing builtin type
            if 'type' in data:
                data['type_'] = data.pop('type')
            self.controller.add_transaction(**data)

    def open_edit_dialog(self, transaction):
        dialog = TransactionDialog(self.controller, self, transaction)
        if dialog.exec():
            data = dialog.get_data()
            self.controller.update_transaction(transaction['_id'], data)
