from PySide6.QtCore import QObject
from app.models.transaction_model import TransactionModel
from app.models.budget_model import BudgetModel
from app.models.category_model import CategoryModel

class DashboardController(QObject):
    def __init__(self):
        super().__init__()
        self.transaction_model = TransactionModel()
        self.budget_model = BudgetModel()
        self.category_model = CategoryModel()

    def get_dashboard_data(self, month, year):
        transactions = self.transaction_model.get_transactions_by_month(month, year)
        budget_data = self.budget_model.get_budget(month, year)
        total_budget = budget_data['total_budget'] if budget_data else 0.0
        
        total_income = sum(t['amount'] for t in transactions if t['type'] == 'income')
        total_expense = sum(t['amount'] for t in transactions if t['type'] == 'expense')
        net_result = total_income - total_expense
        remaining_budget = total_budget + total_income - total_expense
        
        # Category breakdown
        category_expenses = {}
        for t in transactions:
            if t['type'] == 'expense':
                cat_id = str(t.get('category_id'))
                if cat_id not in category_expenses:
                    category_expenses[cat_id] = 0
                category_expenses[cat_id] += t['amount']
        
        categories = []
        for cat_id, amount in category_expenses.items():
            cat_details = self.category_model.get_category_by_id(cat_id)
            categories.append({
                "name": cat_details['name'] if cat_details else "Uncategorized",
                "icon": cat_details['icon'] if cat_details else "❓",
                "amount": amount
            })
            
        categories.sort(key=lambda x: x['amount'], reverse=True)
        
        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "net_result": net_result,
            "total_budget": total_budget,
            "remaining_budget": remaining_budget,
            "categories": categories
        }
