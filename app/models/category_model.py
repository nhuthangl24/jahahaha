from bson.objectid import ObjectId
from app.services.database import DatabaseService

class CategoryModel:
    def __init__(self):
        self.collection = DatabaseService().get_collection('categories')

    def get_all_categories(self):
        return list(self.collection.find())

    def get_categories_by_type(self, type_):
        return list(self.collection.find({"type": type_}))
        
    def add_category(self, name, type_, icon, color):
        category = {
            "name": name,
            "type": type_,
            "icon": icon,
            "color": color
        }
        return self.collection.insert_one(category).inserted_id

    def update_category(self, category_id, data):
        self.collection.update_one({"_id": ObjectId(category_id)}, {"$set": data})

    def delete_category(self, category_id):
        self.collection.delete_one({"_id": ObjectId(category_id)})
    
    def get_category_by_id(self, category_id):
        if isinstance(category_id, str):
            category_id = ObjectId(category_id)
        return self.collection.find_one({"_id": category_id})

    def search_categories(self, name):
        return list(self.collection.find({"name": {"$regex": name, "$options": "i"}}))
