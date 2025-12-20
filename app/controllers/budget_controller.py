from PySide6.QtCore import QObject, Signal
from app.models.budget_model import BudgetModel
from app.models.transaction_model import TransactionModel

class BudgetController(QObject):
    budget_changed = Signal()

    def __init__(self):
        super().__init__()
        self.model = BudgetModel()
        self.transaction_model = TransactionModel()

    def get_budget_status(self, month, year):
        budget_data = self.model.get_budget(month, year)
        total_budget = budget_data['total_budget'] if budget_data else 0.0
        
        transactions = self.transaction_model.get_transactions_by_month(month, year)
        total_spent = sum(t['amount'] for t in transactions if t['type'] == 'expense')
        total_income = sum(t['amount'] for t in transactions if t['type'] == 'income')
        
        return {
            "total_budget": total_budget,
            "total_income": total_income,
            "total_spent": total_spent,
            "remaining": total_budget + total_income - total_spent,
            "percentage": (total_spent / (total_budget + total_income) * 100) if (total_budget + total_income) > 0 else 0
        }

    def set_budget(self, month, year, amount):
        self.model.set_budget(month, year, amount)
        self.budget_changed.emit()
