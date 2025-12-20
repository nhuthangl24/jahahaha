import csv
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFileDialog, QMessageBox)
from app.models.transaction_model import TransactionModel
from app.models.category_model import CategoryModel

class ImportExportView(QWidget):
    def __init__(self):
        super().__init__()
        self.transaction_model = TransactionModel()
        self.category_model = CategoryModel()
        
        self.layout = QVBoxLayout(self)
        
        # Header
        title = QLabel("Nhập / Xuất Dữ Liệu")
        title.setProperty("class", "SectionHeader")
        self.layout.addWidget(title)
        
        # Import Section
        import_lbl = QLabel("Nhập Giao Dịch (CSV)")
        import_lbl.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 20px;")
        self.layout.addWidget(import_lbl)
        
        import_desc = QLabel("Định dạng cột CSV: date, amount, type, category_name, payment_method, note, tags")
        import_desc.setStyleSheet("color: #AAAAAA; margin-bottom: 10px;")
        self.layout.addWidget(import_desc)
        
        import_btn = QPushButton("Chọn File CSV")
        import_btn.setProperty("class", "PrimaryButton")
        import_btn.clicked.connect(self.import_csv)
        self.layout.addWidget(import_btn)
        
        # Export Section
        export_lbl = QLabel("Xuất Giao Dịch")
        export_lbl.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 40px;")
        self.layout.addWidget(export_lbl)
        
        export_btn = QPushButton("Xuất ra CSV")
        export_btn.setProperty("class", "SecondaryButton")
        export_btn.clicked.connect(self.export_csv)
        self.layout.addWidget(export_btn)
        
        self.layout.addStretch()

    def import_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Mở CSV", "", "CSV Files (*.csv)")
        if not file_path:
            return
            
        try:
            count = 0
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Basic validation
                    if not all(k in row for k in ['date', 'amount', 'type']):
                        continue
                        
                    # Try to find category by name
                    cat_id = None
                    if 'category_name' in row and row['category_name']:
                        # This is a bit inefficient, but works for local app
                        cats = self.category_model.get_all_categories()
                        for c in cats:
                            if c['name'].lower() == row['category_name'].lower():
                                cat_id = c['_id']
                                break
                    
                    self.transaction_model.add_transaction(
                        date=row['date'],
                        amount=float(row['amount']),
                        type_=row['type'],
                        category_id=cat_id,
                        payment_method=row.get('payment_method', 'cash'),
                        note=row.get('note', ''),
                        tags=row.get('tags', '').split(',') if row.get('tags') else []
                    )
                    count += 1
            
            QMessageBox.information(self, "Thành Công", f"Đã nhập thành công {count} giao dịch.")
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Nhập CSV thất bại: {str(e)}")

    def export_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Lưu CSV", "transactions.csv", "CSV Files (*.csv)")
        if not file_path:
            return
            
        try:
            transactions = self.transaction_model.get_all_transactions()
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['date', 'amount', 'type', 'category_id', 'payment_method', 'note', 'tags'])
                
                for t in transactions:
                    writer.writerow([
                        t['date'],
                        t['amount'],
                        t['type'],
                        str(t.get('category_id', '')),
                        t['payment_method'],
                        t.get('note', ''),
                        ",".join(t.get('tags', []))
                    ])
            
            QMessageBox.information(self, "Thành Công", "Xuất giao dịch thành công.")
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Xuất CSV thất bại: {str(e)}")
