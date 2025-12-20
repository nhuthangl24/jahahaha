from app.services.database import DatabaseService

class BudgetModel:
    def __init__(self):
        self.collection = DatabaseService().get_collection('budgets')

    def get_budget(self, month, year):
        return self.collection.find_one({"month": month, "year": year})

    def set_budget(self, month, year, total_budget):
        self.collection.update_one(
            {"month": month, "year": year},
            {"$set": {"total_budget": float(total_budget)}},
            upsert=True
        )
