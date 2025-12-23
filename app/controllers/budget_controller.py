from PySide6.QtCore import QObject, Signal
from app.models.budget_model import BudgetModel
from app.models.transaction_model import TransactionModel
from app.models.category_model import CategoryModel

class BudgetController(QObject):
    budget_changed = Signal()

    def __init__(self):
        super().__init__()
        self.model = BudgetModel()
        self.transaction_model = TransactionModel()
        self.category_model = CategoryModel()

    def get_budget_status(self, month, year):
        budget_doc = self.model.get_budget(month, year)
        total_budget_limit = budget_doc.get('total_budget', 0.0) if budget_doc else 0.0
        category_budgets = budget_doc.get('category_budgets', {}) if budget_doc else {}
        
        transactions = self.transaction_model.get_transactions_by_month(month, year)
        
        # Calculate total spent (expense + incurdebt)
        total_spent = sum(t['amount'] for t in transactions if t['type'] in ['expense', 'incurdebt'])
        
        # Calculate spent by category (include expense and incurdebt)
        spent_by_category = {}
        for t in transactions:
            if t['type'] in ['expense', 'incurdebt']:
                cat_id = str(t.get('category_id'))
                if cat_id not in spent_by_category:
                    spent_by_category[cat_id] = 0
                spent_by_category[cat_id] += t['amount']
        
        category_status_list = []
        all_category_ids = set(category_budgets.keys())
        
        for cat_id in all_category_ids:
            if not cat_id or cat_id == 'None': continue
            
            cat_info = self.category_model.get_category_by_id(cat_id)
            name = cat_info['name'] if cat_info else "Unknown"
            icon = cat_info['icon'] if cat_info else "❓"
            
            limit = category_budgets.get(cat_id, 0.0)
            spent = spent_by_category.get(cat_id, 0.0)
            
            category_status_list.append({
                "id": cat_id,
                "name": name,
                "icon": icon,
                "limit": limit,
                "spent": spent,
                "remaining": limit - spent,
                "percentage": (spent / limit * 100) if limit > 0 else (100 if spent > 0 else 0)
            })
            
        category_status_list.sort(key=lambda x: x['percentage'], reverse=True)

        return {
            "total_budget_limit": total_budget_limit,
            "total_spent": total_spent,
            "total_remaining": total_budget_limit - total_spent,
            "total_percentage": (total_spent / total_budget_limit * 100) if total_budget_limit > 0 else 0,
            "categories": category_status_list
        }

    def set_total_budget(self, month, year, amount):
        self.model.set_total_budget(month, year, amount)
        self.budget_changed.emit()

    def set_category_budget(self, month, year, category_id, amount):
        self.model.set_category_budget(month, year, category_id, amount)
        self.budget_changed.emit()

    def remove_category_budget(self, month, year, category_id):
        self.model.remove_category_budget(month, year, category_id)
        self.budget_changed.emit()
        
    def get_all_categories(self):
        return self.category_model.get_all_categories()
