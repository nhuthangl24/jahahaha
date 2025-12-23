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

    print("--- BẮT ĐẦU TẠO DỮ LIỆU MẪU ---")

    # 1. Đảm bảo có đủ danh mục đa dạng
    existing_categories = category_model.get_all_categories()
    existing_names = [c['name'] for c in existing_categories]

    sample_categories = [
        # Chi tiêu
        ("Ăn uống", "expense", "🍔", "#FF5733"),
        ("Di chuyển", "expense", "🚕", "#33FF57"),
        ("Mua sắm", "expense", "🛍️", "#FF33A8"),
        ("Giải trí", "expense", "🎬", "#A833FF"),
        ("Hóa đơn", "expense", "🧾", "#33FFF5"),
        # Thu nhập
        ("Lương", "income", "💰", "#3357FF"),
        ("Thưởng", "income", "🎁", "#33FFBD"),
        # Vay nợ
        ("Cho vay", "incurdebt", "💸", "#FF8C33"),
        ("Đi vay", "incurdebt", "🤝", "#8C33FF")
    ]

    for name, type_, icon, color in sample_categories:
        if name not in existing_names:
            print(f"Tạo danh mục mới: {name}")
            category_model.add_category(name, type_, icon, color)
    
    # Tải lại danh sách danh mục mới nhất
    categories = category_model.get_all_categories()
    
    # Phân loại danh mục để random cho hợp lý
    expense_cats = [c for c in categories if c['type'] == 'expense']
    income_cats = [c for c in categories if c['type'] == 'income']
    debt_cats = [c for c in categories if c['type'] == 'incurdebt']

    # 2. Danh sách ghi chú mẫu phong phú
    notes_expense = [
        "Ăn trưa cơm tấm", "Cà phê sáng", "Đổ xăng xe máy", "Mua áo thun mới", 
        "Vé xem phim", "Tiền điện tháng này", "Mua sách", "Đi Grab đi làm", 
        "Ăn tối với bạn", "Mua đồ siêu thị"
    ]
    notes_income = ["Nhận lương tháng 12", "Tiền thưởng dự án", "Bán đồ cũ", "Lì xì sớm"]
    notes_debt = ["Cho bạn mượn tiền", "Mượn tiền đóng trọ", "Trả nợ cũ", "Ứng lương"]

    payment_methods = ["cash", "bank", "ewallet"]
    
    # 3. Tạo 15 giao dịch ngẫu nhiên nhưng có logic
    # Cấu trúc: Khoảng 2 thu nhập, 2 vay nợ, còn lại là chi tiêu
    transactions_plan = []
    
    # Thêm 2 thu nhập
    for _ in range(2):
        transactions_plan.append(('income', random.choice(income_cats) if income_cats else None))
        
    # Thêm 2 vay nợ
    for _ in range(2):
        transactions_plan.append(('incurdebt', random.choice(debt_cats) if debt_cats else None))
        
    # Thêm 11 chi tiêu
    for _ in range(11):
        transactions_plan.append(('expense', random.choice(expense_cats) if expense_cats else None))
        
    random.shuffle(transactions_plan) # Trộn đều thứ tự

    count = 0
    for type_, category in transactions_plan:
        if not category: continue # Bỏ qua nếu không tìm thấy danh mục phù hợp
        
        count += 1
        
        # Random ngày trong tháng hiện tại
        days_ago = random.randint(0, 20)
        date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        # Random số tiền hợp lý theo loại
        if type_ == 'income':
            amount = random.choice([10000000, 15000000, 2000000, 5000000]) # Lương/Thưởng chẵn
            note = random.choice(notes_income)
        elif type_ == 'incurdebt':
            amount = random.choice([500000, 1000000, 2000000, 5000000]) # Vay mượn chẵn
            note = random.choice(notes_debt)
        else: # expense
            if category['name'] == "Ăn uống":
                amount = random.randint(30, 500) * 1000 # 30k - 500k
            elif category['name'] == "Di chuyển":
                amount = random.randint(10, 100) * 1000 # 10k - 100k
            elif category['name'] == "Hóa đơn":
                amount = random.randint(200, 1000) * 1000 # 200k - 1tr
            else:
                amount = random.randint(50, 2000) * 1000 # 50k - 2tr
            note = random.choice(notes_expense)

        transaction_controller.add_transaction(
            date=date,
            amount=amount,
            type_=type_,
            category_id=category['_id'],
            payment_method=random.choice(payment_methods),
            note=note,
            tags=["demo-data"]
        )
        print(f"[{count}/15] {date} | {type_.upper():<10} | {amount:>12,} đ | {note}")

    print("--- HOÀN TẤT ---")

if __name__ == "__main__":
    generate_data()