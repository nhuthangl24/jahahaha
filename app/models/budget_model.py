from app.services.database import DatabaseService

class BudgetModel:
    def __init__(self):
        self.collection = DatabaseService().get_collection('budgets')

    def get_budget(self, month, year):
        return self.collection.find_one({"month": month, "year": year})

    def set_total_budget(self, month, year, total_budget):
        self.collection.update_one(
            {"month": month, "year": year},
            {"$set": {"total_budget": float(total_budget)}},
            upsert=True
        )

    def set_category_budget(self, month, year, category_id, amount):
        key = f"category_budgets.{category_id}"
        self.collection.update_one(
            {"month": month, "year": year},
            {"$set": {key: float(amount)}},
            upsert=True
        )

    def remove_category_budget(self, month, year, category_id):
        key = f"category_budgets.{category_id}"
        self.collection.update_one(
            {"month": month, "year": year},
            {"$unset": {key: ""}}
        )
