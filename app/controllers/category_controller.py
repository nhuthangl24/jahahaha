from PySide6.QtCore import QObject, Signal
from app.models.category_model import CategoryModel

class CategoryController(QObject):
    categories_changed = Signal()

    def __init__(self):
        super().__init__()
        self.model = CategoryModel()

    def get_all_categories(self):
        return self.model.get_all_categories()

    def get_categories_by_type(self, type_):
        return self.model.get_categories_by_type(type_)

    def add_category(self, name, type_, icon, color):
        self.model.add_category(name, type_, icon, color)
        self.categories_changed.emit()

    def update_category(self, category_id, name, type_, icon, color):
        data = {
            "name": name,
            "type": type_,
            "icon": icon,
            "color": color
        }
        self.model.update_category(category_id, data)
        self.categories_changed.emit()

    def delete_category(self, category_id):
        self.model.delete_category(category_id)
        self.categories_changed.emit()
