import sys
import os
import customtkinter as ctk
from datetime import datetime, timedelta
from pymongo import MongoClient

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from SERVER_API import db

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AdminPanel(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("👑 BOSS PANEL - QUẢN LÝ KHÁCH HÀNG")
        self.geometry("1000x650")
        
        self.database = self.connect_db()
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        
        self.setup_ui()
        self.refresh_users()

    def connect_db(self):
        if not db.URI:
            return None
        try:
            client = MongoClient(db.URI, serverSelectionTimeoutMS=5000)
            return client["ToolAutoDB"]
        except:
            return None

    def setup_ui(self):
        # --- HEADER (THÊM USER MỚI) ---
        header = ctk.CTkFrame(self, corner_radius=10)
        header.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        ctk.CTkLabel(header, text="THÊM KHÁCH HÀNG MỚI", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=6, pady=(10, 5))
        
        self.entry_user = ctk.CTkEntry(header, placeholder_text="Username", width=150)
        self.entry_user.grid(row=1, column=0, padx=10, pady=10)
        
        self.entry_pass = ctk.CTkEntry(header, placeholder_text="Password", width=120)
        self.entry_pass.grid(row=1, column=1, padx=10, pady=10)
        
        self.entry_email = ctk.CTkEntry(header, placeholder_text="Email", width=150)
        self.entry_email.grid(row=1, column=2, padx=10, pady=10)
        
        options = ["Dùng thử 1 Ngày", "Dùng thử 2 Ngày", "Dùng thử 3 Ngày", "1 Tháng", "2 Tháng", "3 Tháng", "6 Tháng", "1 Năm"]
        self.combo_time = ctk.CTkComboBox(header, values=options, width=120)
        self.combo_time.grid(row=1, column=3, padx=10, pady=10)
        
        btn_add = ctk.CTkButton(header, text="➕ TẠO", command=self.add_user, fg_color="#27AE60", hover_color="#2ECC71", width=80)
        btn_add.grid(row=1, column=4, padx=10, pady=10)
        
        ctk.CTkButton(header, text="🔄 LÀM MỚI", command=self.refresh_users, fg_color="#2980B9", hover_color="#3498DB", width=100).grid(row=1, column=5, padx=10, pady=10)

        # --- THANH TÌM KIẾM ---
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        ctk.CTkLabel(search_frame, text="🔍 Tìm kiếm Email:").pack(side="left", padx=5)
        self.entry_search = ctk.CTkEntry(search_frame, placeholder_text="Nhập email cần tìm...", width=250)
        self.entry_search.pack(side="left", padx=5)
        
        ctk.CTkButton(search_frame, text="TÌM", width=60, command=self.refresh_users).pack(side="left", padx=5)
        ctk.CTkButton(search_frame, text="HỦY TÌM KIẾM", width=100, fg_color="#7F8C8D", hover_color="#95A5A6", 
                      command=self.clear_search).pack(side="left", padx=5)

        # --- BẢNG DANH SÁCH ---
        self.scroll_frame = ctk.CTkScrollableFrame(self, corner_radius=10)
        self.scroll_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Tiêu đề bảng
        headers = ["Username", "Ngày Hết Hạn", "Trạng Thái", "Online", "Hành Động"]
        for i, h in enumerate(headers):
            ctk.CTkLabel(self.scroll_frame, text=h, font=("Arial", 13, "bold"), text_color="#F39C12").grid(row=0, column=i, padx=20, pady=10)

    def add_user(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()
        email = self.entry_email.get().strip()
        time_str = self.combo_time.get()
        
        if not username or not password or not email:
            self.show_msg("Vui lòng nhập Username, Password và Email!")
            return
            
        days = 30
        if "1 Ngày" in time_str: days = 1
        elif "2 Ngày" in time_str: days = 2
        elif "3 Ngày" in time_str: days = 3
        elif "2 Tháng" in time_str: days = 60
        elif "3 Tháng" in time_str: days = 90
        elif "6 Tháng" in time_str: days = 180
        elif "1 Năm" in time_str: days = 365
        
        success, msg = db.register_user(username, email, password, days=days)
        if success:
            self.entry_user.delete(0, 'end')
            self.entry_pass.delete(0, 'end')
            self.entry_email.delete(0, 'end')
            self.refresh_users()
            self.show_msg(f"✅ Đã tạo thành công tài khoản {username} (Hạn {days} ngày)")
        else:
            self.show_msg(f"❌ Lỗi: {msg}")

    def refresh_users(self):
        if self.database is None:
            self.show_msg("❌ Lỗi kết nối Database!")
            return
            
        # Xóa các dòng cũ
        for widget in self.scroll_frame.winfo_children():
            if int(widget.grid_info()["row"]) > 0:
                widget.destroy()
                
        search_email = ""
        if hasattr(self, 'entry_search'):
            search_email = self.entry_search.get().strip()
            
        if search_email:
            # Tìm gần đúng email không phân biệt chữ hoa chữ thường
            users = list(self.database["Users"].find({"email": {"$regex": search_email, "$options": "i"}}))
        else:
            users = list(self.database["Users"].find())
        
        for idx, user in enumerate(users):
            row = idx + 1
            username = user.get("username", "")
            
            # Xử lý Hạn sử dụng
            expiry = user.get("expiry_date")
            if expiry:
                expiry_str = expiry.strftime("%d/%m/%Y")
                is_expired = datetime.utcnow() > expiry
            else:
                expiry_str = "Vĩnh viễn"
                is_expired = False
                
            status = user.get("status", "active")
            if is_expired and status == "active":
                status = "locked (hết hạn)"
                
            session = user.get("session_token", "")
            is_online = "🟢" if len(session) > 5 else "🔴"
            
            color_status = "#2ECC71" if status == "active" else "#E74C3C"
            color_expiry = "#E74C3C" if is_expired else "#FFFFFF"
            
            ctk.CTkLabel(self.scroll_frame, text=username, font=("Arial", 12, "bold")).grid(row=row, column=0, padx=20, pady=10)
            ctk.CTkLabel(self.scroll_frame, text=expiry_str, text_color=color_expiry).grid(row=row, column=1, padx=20, pady=10)
            ctk.CTkLabel(self.scroll_frame, text=status.upper(), text_color=color_status).grid(row=row, column=2, padx=20, pady=10)
            ctk.CTkLabel(self.scroll_frame, text=is_online).grid(row=row, column=3, padx=20, pady=10)
            
            # Khung chứa các nút hành động
            action_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
            action_frame.grid(row=row, column=4, padx=20, pady=5)
            
            # Nút Gia hạn
            btn_gia_han = ctk.CTkButton(action_frame, text="Gia hạn +1 Tháng", width=100, height=25, 
                                      command=lambda u=username: self.extend_user(u, 30))
            btn_gia_han.pack(side="left", padx=5)
            
            # Nút Khóa/Mở Khóa
            text_lock = "Khóa" if status == "active" else "Mở Khóa"
            color_lock = "#E74C3C" if status == "active" else "#2ECC71"
            btn_lock = ctk.CTkButton(action_frame, text=text_lock, width=80, height=25, fg_color=color_lock,
                                   command=lambda u=username, s=status: self.toggle_lock(u, s))
            btn_lock.pack(side="left", padx=5)

    def extend_user(self, username, days_to_add):
        user = self.database["Users"].find_one({"username": username})
        if user:
            current_expiry = user.get("expiry_date")
            if not current_expiry or current_expiry < datetime.utcnow():
                new_expiry = datetime.utcnow() + timedelta(days=days_to_add)
            else:
                new_expiry = current_expiry + timedelta(days=days_to_add)
                
            self.database["Users"].update_one(
                {"username": username}, 
                {"$set": {"expiry_date": new_expiry, "status": "active"}}
            )
            self.refresh_users()
            self.show_msg(f"✅ Đã gia hạn tài khoản {username} thêm {days_to_add} ngày!")

    def toggle_lock(self, username, current_status):
        new_status = "locked" if current_status == "active" else "active"
        update_data = {"$set": {"status": new_status}}
        if new_status == "locked":
             update_data["$set"]["session_token"] = "" # Ép văng khỏi tool
             
        self.database["Users"].update_one({"username": username}, update_data)
        self.refresh_users()

    def clear_search(self):
        self.entry_search.delete(0, 'end')
        self.refresh_users()

    def show_msg(self, text):
        popup = ctk.CTkToplevel(self)
        popup.title("Thông báo")
        popup.geometry("350x150")
        popup.attributes("-topmost", True)
        ctk.CTkLabel(popup, text=text, wraplength=300).pack(pady=30)
        ctk.CTkButton(popup, text="OK", command=popup.destroy, width=100).pack()

if __name__ == "__main__":
    app = AdminPanel()
    app.mainloop()
