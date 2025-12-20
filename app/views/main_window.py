from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ứng Dụng Quản Lý Tài Chính")
        self.resize(1280, 800)
        
        # Main Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = QWidget()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(0, 20, 0, 20)
        self.sidebar_layout.setSpacing(10)
        self.sidebar_layout.setAlignment(Qt.AlignTop)

        # App Title in Sidebar
        self.app_title = QLabel("QUẢN LÝ TÀI CHÍNH")
        self.app_title.setStyleSheet("color: white; font-weight: bold; font-size: 16px; padding-left: 20px; margin-bottom: 20px;")
        self.sidebar_layout.addWidget(self.app_title)

        # Navigation Buttons
        self.nav_buttons = {}
        self.create_nav_button("Bảng Điều Khiển", 0)
        self.create_nav_button("Giao Dịch", 1)
        self.create_nav_button("Danh Mục", 2)
        self.create_nav_button("Ngân Sách", 3)
        self.create_nav_button("Nhập / Xuất", 4)

        self.sidebar_layout.addStretch()
        self.main_layout.addWidget(self.sidebar)

        # Content Area
        self.content_area = QStackedWidget()
        self.main_layout.addWidget(self.content_area)

        # Placeholder Views (will be replaced by actual views)
        self.dashboard_view = QWidget()
        self.transactions_view = QWidget()
        self.categories_view = QWidget()
        self.budgets_view = QWidget()
        self.import_export_view = QWidget()

        self.content_area.addWidget(self.dashboard_view)
        self.content_area.addWidget(self.transactions_view)
        self.content_area.addWidget(self.categories_view)
        self.content_area.addWidget(self.budgets_view)
        self.content_area.addWidget(self.import_export_view)

        # Set default view
        self.nav_buttons["Bảng Điều Khiển"].setChecked(True)
        self.content_area.setCurrentIndex(0)

    def create_nav_button(self, text, index):
        btn = QPushButton(text)
        btn.setObjectName("SidebarButton")
        btn.setCheckable(True)
        btn.setAutoExclusive(True)
        btn.clicked.connect(lambda: self.switch_view(index))
        self.sidebar_layout.addWidget(btn)
        self.nav_buttons[text] = btn

    def switch_view(self, index):
        self.content_area.setCurrentIndex(index)

    def set_view(self, index, widget):
        # Helper to replace placeholder widgets with actual views
        old_widget = self.content_area.widget(index)
        self.content_area.removeWidget(old_widget)
        self.content_area.insertWidget(index, widget)
