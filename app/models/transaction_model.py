from bson.objectid import ObjectId
from app.services.database import DatabaseService
from datetime import datetime

class TransactionModel:
    def __init__(self):
        self.collection = DatabaseService().get_collection('transactions')

    def get_all_transactions(self):
        return list(self.collection.find().sort("date", -1))

    def get_transactions_by_month(self, month, year):
        start_date = f"{year}-{month:02d}-01"
        regex = f"^{year}-{month:02d}"
        return list(self.collection.find({"date": {"$regex": regex}}).sort("date", -1))

    def add_transaction(self, date, amount, type_, category_id, payment_method, note, tags=None):
        transaction = {
            "date": date,
            "amount": float(amount),
            "type": type_,
            "category_id": ObjectId(category_id) if category_id else None,
            "payment_method": payment_method,
            "note": note,
            "tags": tags or []
        }
        return self.collection.insert_one(transaction).inserted_id

    def update_transaction(self, transaction_id, data):
        if 'category_id' in data and data['category_id']:
            data['category_id'] = ObjectId(data['category_id'])
        if 'amount' in data:
            data['amount'] = float(data['amount'])
            
        self.collection.update_one({"_id": ObjectId(transaction_id)}, {"$set": data})

    def delete_transaction(self, transaction_id):
        self.collection.delete_one({"_id": ObjectId(transaction_id)})
