from PySide6.QtCore import QObject, Signal
from app.models.transaction_model import TransactionModel
from app.models.category_model import CategoryModel

class TransactionController(QObject):
    transactions_changed = Signal()

    def __init__(self):
        super().__init__()
        self.model = TransactionModel()
        self.category_model = CategoryModel()

    def get_all_transactions(self):
        transactions = self.model.get_all_transactions()
        return self._enrich_transactions(transactions)

    def get_transactions_by_month(self, month, year):
        transactions = self.model.get_transactions_by_month(month, year)
        return self._enrich_transactions(transactions)

    def _enrich_transactions(self, transactions):
        # Helper to add category details to transactions
        for t in transactions:
            if t.get('category_id'):
                category = self.category_model.get_category_by_id(t['category_id'])
                t['category_name'] = category['name'] if category else "Unknown"
                t['category_icon'] = category['icon'] if category else "❓"
            else:
                t['category_name'] = "Uncategorized"
                t['category_icon'] = "❓"
        return transactions

    def add_transaction(self, date, amount, type_, category_id, payment_method, note, tags=None):
        self.model.add_transaction(date, amount, type_, category_id, payment_method, note, tags)
        self.transactions_changed.emit()

    def update_transaction(self, transaction_id, data):
        self.model.update_transaction(transaction_id, data)
        self.transactions_changed.emit()

    def delete_transaction(self, transaction_id):
        self.model.delete_transaction(transaction_id)
        self.transactions_changed.emit()
    
    def get_categories(self):
        return self.category_model.get_all_categories()
