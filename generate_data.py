import sys
import os
import random
from datetime import datetime, timedelta

# Add current directory to path so we can import app
sys.path.append(os.getcwd())

from app.controllers.transaction_controller import TransactionController
from app.models.category_model import CategoryModel

def generate_data():
    transaction_controller = TransactionController()
    category_model = CategoryModel()

    # Ensure we have some categories
    categories = category_model.get_all_categories()
    if not categories:
        print("Creating dummy categories...")
        # Create some basic categories if none exist
        basic_categories = [
            ("Ăn uống", "expense", "🍔", "#FF5733"),
            ("Di chuyển", "expense", "🚕", "#33FF57"),
            ("Lương", "income", "💰", "#3357FF"),
            ("Giải trí", "expense", "🎬", "#F333FF"),
            ("Hóa đơn", "expense", "🧾", "#33FFF5")
        ]
        for name, type_, icon, color in basic_categories:
            category_model.add_category(name, type_, icon, color)
        categories = category_model.get_all_categories()

    notes = [
        "Ăn trưa với đồng nghiệp", "Đi siêu thị mua đồ", "Tiền taxi đi làm", "Nhận lương tháng này", 
        "Thưởng dự án", "Cà phê sáng", "Thanh toán tiền điện", "Thanh toán tiền nước", 
        "Tiền nhà trọ", "Xem phim cuối tuần", "Đăng ký tập Gym", "Mua sách lập trình", 
        "Mua quà sinh nhật", "Quyên góp từ thiện", "Đầu tư chứng khoán", "Gửi tiết kiệm", 
        "Mua sắm quần áo", "Du lịch Đà Lạt", "Đặt phòng khách sạn", "Vé máy bay", 
        "Vé xe buýt", "Vé tàu hỏa", "Ăn vặt chiều", "Sửa xe máy", "Cắt tóc"
    ]

    payment_methods = ["cash", "bank", "credit", "ewallet"]

    print(f"Generating {len(notes)} transactions...")

    for i in range(25):
        note = notes[i] if i < len(notes) else f"Giao dịch {i+1}"
        
        # Random date within last 30 days
        days_ago = random.randint(0, 30)
        date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        # Random category
        category = random.choice(categories)
        category_id = category['_id']
        type_ = category['type']
        
        # Random amount based on type
        if type_ == 'income':
            amount = random.randint(5000000, 20000000)
        else:
            amount = random.randint(20000, 500000)
            
        payment_method = random.choice(payment_methods)
        
        transaction_controller.add_transaction(
            date=date,
            amount=amount,
            type_=type_,
            category_id=category_id,
            payment_method=payment_method,
            note=note,
            tags=["auto-generated"]
        )
        print(f"Added: {note} - {amount}")

    print("Done!")

if __name__ == "__main__":
    generate_data()
