from pymongo import MongoClient

class DatabaseService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseService, cls).__new__(cls)
            cls._instance.client = MongoClient('mongodb+srv://luunhuthang2402:nhutahngl24@learnnoaz.nwz1byp.mongodb.net/?appName=learnnoaz')
            cls._instance.db = cls._instance.client['finance_app']
        return cls._instance

    def get_db(self):
        return self.db

    def get_collection(self, collection_name):
        return self.db[collection_name]
