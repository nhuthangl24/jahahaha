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
        total_budget = budget_data.get('total_budget', 0.0) if budget_data else 0.0
        
        total_income = sum(t['amount'] for t in transactions if t['type'] == 'income')
        total_expense = sum(t['amount'] for t in transactions if t['type'] == 'expense')
        total_debt = sum(t['amount'] for t in transactions if t['type'] == 'incurdebt')
        
        net_result = total_income - total_expense
        remaining_budget = total_budget + total_income - total_expense
        
        # Category breakdown
        category_expenses = {}
        category_incomes = {}
        category_debts = {}
        
        for t in transactions:
            cat_id = str(t.get('category_id'))
            amount = t['amount']
            
            if t['type'] == 'expense':
                category_expenses[cat_id] = category_expenses.get(cat_id, 0) + amount
            elif t['type'] == 'income':
                category_incomes[cat_id] = category_incomes.get(cat_id, 0) + amount
            elif t['type'] == 'incurdebt':
                category_debts[cat_id] = category_debts.get(cat_id, 0) + amount
        
        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "total_debt": total_debt,
            "net_result": net_result,
            "total_budget": total_budget,
            "remaining_budget": remaining_budget,
            "expense_categories": self._process_categories(category_expenses),
            "income_categories": self._process_categories(category_incomes),
            "debt_categories": self._process_categories(category_debts)
        }

    def _process_categories(self, category_dict):
        result = []
        for cat_id, amount in category_dict.items():
            cat_details = self.category_model.get_category_by_id(cat_id)
            result.append({
                "name": cat_details['name'] if cat_details else "Uncategorized",
                "icon": cat_details['icon'] if cat_details else "❓",
                "amount": amount
            })
        result.sort(key=lambda x: x['amount'], reverse=True)
        return result
