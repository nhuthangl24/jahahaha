import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QFile, QTextStream

# Add project root to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.views.main_window import MainWindow
from app.views.dashboard_view import DashboardView
from app.views.transactions_view import TransactionsView
from app.views.categories_view import CategoriesView
from app.views.budgets_view import BudgetsView
from app.views.import_export_view import ImportExportView

from app.controllers.dashboard_controller import DashboardController
from app.controllers.transaction_controller import TransactionController
from app.controllers.category_controller import CategoryController
from app.controllers.budget_controller import BudgetController

def main():
    app = QApplication(sys.argv)
    
    # Load Styles
    style_file = QFile(os.path.join(os.path.dirname(__file__), "app/ui/styles.qss"))
    if style_file.open(QFile.ReadOnly | QFile.Text):
        stream = QTextStream(style_file)
        app.setStyleSheet(stream.readAll())
    
    # Initialize Controllers
    dashboard_controller = DashboardController()
    transaction_controller = TransactionController()
    category_controller = CategoryController()
    budget_controller = BudgetController()
    
    # Initialize Views
    dashboard_view = DashboardView(dashboard_controller)
    transactions_view = TransactionsView(transaction_controller)
    categories_view = CategoriesView(category_controller)
    budgets_view = BudgetsView(budget_controller)
    import_export_view = ImportExportView()
    
    # Setup Main Window
    window = MainWindow()
    window.set_view(0, dashboard_view)
    window.set_view(1, transactions_view)
    window.set_view(2, categories_view)
    window.set_view(3, budgets_view)
    window.set_view(4, import_export_view)
    
    # Connect signals for cross-view updates
    # When transactions change, update dashboard and budget
    transaction_controller.transactions_changed.connect(dashboard_view.refresh_dashboard)
    transaction_controller.transactions_changed.connect(budgets_view.refresh_budget)
    
    # When categories change, update transactions view (dropdowns) and dashboard
    category_controller.categories_changed.connect(dashboard_view.refresh_dashboard)
    # Note: TransactionsView updates its dropdowns when the dialog is opened, so no direct signal needed there
    
    # When budget changes, update dashboard
    budget_controller.budget_changed.connect(dashboard_view.refresh_dashboard)
    
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
