import customtkinter as ctk
import threading
import time
from tkinter import filedialog 

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ToolApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AQUA-REG-TOOL V.4.0 - Đa Web & Tùy Chỉnh Kích Thước")
        self.geometry("1300x800") 
        
        # Cho phép kéo giãn cửa sổ tùy ý (Ngang, Dọc)
        self.resizable(True, True)
        self.minsize(1100, 600) # Kích thước nhỏ nhất để không bị vỡ khung
        
        self.task_count = 0
        self.tasks_data = [] 

        # ================= KHU VỰC 1: INPUT DỮ LIỆU CÓ LABEL =================
        self.frame_data = ctk.CTkFrame(self)
        self.frame_data.pack(pady=5, padx=10, fill="x")

        # DÒNG 0: LABELS
        ctk.CTkLabel(self.frame_data, text="Username").grid(row=0, column=0, padx=5, sticky="w")
        ctk.CTkLabel(self.frame_data, text="Password").grid(row=0, column=1, padx=5, sticky="w")
        ctk.CTkLabel(self.frame_data, text="Họ và tên").grid(row=0, column=2, padx=5, sticky="w")
        ctk.CTkLabel(self.frame_data, text="Số tài khoản").grid(row=0, column=3, padx=5, sticky="w")

        # DÒNG 1: ENTRIES
        self.entry_user = ctk.CTkEntry(self.frame_data, placeholder_text="Nhập Username...")
        self.entry_user.grid(row=1, column=0, padx=5, pady=(0, 5))
        self.entry_pass = ctk.CTkEntry(self.frame_data, placeholder_text="Nhập Password...")
        self.entry_pass.grid(row=1, column=1, padx=5, pady=(0, 5))
        self.entry_name = ctk.CTkEntry(self.frame_data, placeholder_text="Nhập Họ Tên...")
        self.entry_name.grid(row=1, column=2, padx=5, pady=(0, 5))
        self.entry_stk = ctk.CTkEntry(self.frame_data, placeholder_text="Nhập STK...")
        self.entry_stk.grid(row=1, column=3, padx=5, pady=(0, 5))

        # DÒNG 2: LABELS
        ctk.CTkLabel(self.frame_data, text="Tên ngân hàng").grid(row=2, column=0, padx=5, sticky="w")
        ctk.CTkLabel(self.frame_data, text="Số điện thoại").grid(row=2, column=1, padx=5, sticky="w")
        ctk.CTkLabel(self.frame_data, text="Mật khẩu rút tiền").grid(row=2, column=2, padx=5, sticky="w")

        # DÒNG 3: ENTRIES
        self.entry_bank = ctk.CTkEntry(self.frame_data, placeholder_text="Tên ngân hàng")
        self.entry_bank.grid(row=3, column=0, padx=5, pady=(0, 5))
        self.entry_phone = ctk.CTkEntry(self.frame_data, placeholder_text="Số điện thoại")
        self.entry_phone.grid(row=3, column=1, padx=5, pady=(0, 5))
        self.entry_rut = ctk.CTkEntry(self.frame_data, placeholder_text="Mật khẩu rút tiền")
        self.entry_rut.grid(row=3, column=2, padx=5, pady=(0, 5))

        # ================= KHU VỰC 2: CẤU HÌNH & QUẢN LÝ TỔNG =================
        self.frame_config = ctk.CTkFrame(self)
        self.frame_config.pack(pady=5, padx=10, fill="x")

        # --- CHỌN NHIỀU WEB CÙNG LÚC (CHECKBOX) ---
        ctk.CTkLabel(self.frame_config, text="Chọn Web/Cổng:").pack(side="left", padx=(10, 5))
        
        self.sites_vars = {
            "C168": ctk.BooleanVar(value=True), # Mặc định tick chọn C168
            "HI": ctk.BooleanVar(value=False),
            "NEW": ctk.BooleanVar(value=False),
            "SC88": ctk.BooleanVar(value=False),
            "F168": ctk.BooleanVar(value=False),
            "QQ": ctk.BooleanVar(value=False),
        }
        
        for site, var in self.sites_vars.items():
            cb = ctk.CTkCheckBox(self.frame_config, text=site, variable=var, width=60)
            cb.pack(side="left", padx=5)

        # --- TÙY CHỌN KHÁC ---
        self.check_hide = ctk.CTkSwitch(self.frame_config, text="Chạy Ẩn")
        self.check_hide.pack(side="left", padx=20)

        self.btn_import = ctk.CTkButton(self.frame_config, text="📂 Nhập File", fg_color="#8E44AD", hover_color="#732D91", command=self.import_file)
        self.btn_import.pack(side="left", padx=5)

        self.btn_export = ctk.CTkButton(self.frame_config, text="💾 Xuất File", fg_color="#2980B9", hover_color="#1F618D", command=self.export_file)
        self.btn_export.pack(side="left", padx=5)

        self.btn_start = ctk.CTkButton(self.frame_config, text="▶ THÊM VÀ CHẠY", fg_color="green", hover_color="darkgreen", command=self.add_task)
        self.btn_start.pack(side="right", padx=10)

        # ================= KHU VỰC 3: BẢNG QUẢN LÝ (TABLE) =================
        self.table_frame = ctk.CTkScrollableFrame(self)
        self.table_frame.pack(pady=5, padx=10, fill="both", expand=True)

        self.header_frame = ctk.CTkFrame(self.table_frame, fg_color="gray20")
        self.header_frame.pack(fill="x", pady=2)
        
        headers = [
            ("STT", 40), ("Web", 70), ("Username", 120), ("Password", 100), 
            ("Họ Tên", 130), ("SĐT", 100), ("Bank", 90), ("STK", 110), 
            ("Trạng thái", 180), ("Hành động", 120)
        ]
        
        for text, width in headers:
            lbl = ctk.CTkLabel(self.header_frame, text=text, width=width, font=("Arial", 12, "bold"))
            lbl.pack(side="left", padx=5)

        # ================= KHU VỰC 4: SYSTEM LOG =================
        self.log_frame = ctk.CTkFrame(self, height=120)
        self.log_frame.pack(pady=5, padx=10, fill="x")
        self.log_frame.pack_propagate(False)

        ctk.CTkLabel(self.log_frame, text="System Log (Theo dõi tiến trình):", font=("Arial", 11, "bold")).pack(anchor="w", padx=5)
        self.log_box = ctk.CTkTextbox(self.log_frame, state="disabled", fg_color="black", text_color="#00FF00", font=("Consolas", 12))
        self.log_box.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.write_log("Hệ thống AQUA-REG-TOOL đã sẵn sàng!")

    # ================= CÁC HÀM XỬ LÝ (LOGIC) =================

    def write_log(self, message):
        def update_gui():
            self.log_box.configure(state="normal")
            timestamp = time.strftime("%H:%M:%S")
            self.log_box.insert("end", f"[{timestamp}] {message}\n")
            self.log_box.configure(state="disabled")
            self.log_box.yview("end") 
        self.after(0, update_gui)

    def import_file(self):
        # Mở cửa sổ chọn file
        filepath = filedialog.askopenfilename(title="Chọn File Dữ Liệu", filetypes=[("Text Files", "*.txt")])
        if filepath:
            self.write_log(f"Đang đọc dữ liệu từ file: {filepath}...")
            try:
                # Đọc nội dung file
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                success_count = 0
                # Lấy danh sách các web đang được tick chọn
                selected_sites = [site for site, var in self.sites_vars.items() if var.get()]
                
                if not selected_sites:
                    self.write_log("⚠️ LỖI: Bạn chưa tick chọn Web/Cổng nào để chạy!")
                    return

                # Duyệt qua từng dòng trong file txt
                for line in lines:
                    line = line.strip()
                    if not line: continue # Bỏ qua nếu dòng trống
                    
                    # Tách dữ liệu dựa trên ký tự '|'
                    # Cấu trúc: User|Pass|Tên|SĐT|Bank|STK|MK Rút
                    data = line.split('|')
                    
                    if len(data) >= 7: # Đảm bảo dòng có đủ 7 trường dữ liệu
                        for site in selected_sites:
                            self.task_count += 1
                            task_data = {
                                "stt": str(self.task_count),
                                "web": site,
                                "user": data[0],
                                "pwd": data[1],
                                "name": data[2],
                                "phone": data[3],
                                "bank": data[4],
                                "stk": data[5]
                            }
                            # Gọi hàm vẽ 1 hàng mới trên bảng UI và cho chạy luôn
                            self._create_table_row(task_data)
                        success_count += 1
                    else:
                        self.write_log(f"⚠️ Bỏ qua dòng sai định dạng: {line}")
                
                self.write_log(f"✅ Đã nhập và khởi tạo chạy thành công {success_count} tài khoản từ file.")
            except Exception as e:
                self.write_log(f"❌ Lỗi khi đọc file: {str(e)}")

    def export_file(self):
        filepath = filedialog.asksaveasfilename(title="Lưu File", defaultextension=".txt")
        if filepath:
            self.write_log(f"Đã xuất dữ liệu ra file: {filepath}")

    def add_task(self):
        """Tạo nhiều luồng dựa trên số lượng web được tick chọn"""
        # Lấy danh sách các web đang được tick
        selected_sites = [site for site, var in self.sites_vars.items() if var.get()]
        
        if not selected_sites:
            self.write_log("⚠️ LỖI: Bạn chưa chọn Web/Cổng nào để chạy!")
            return

        user_input = self.entry_user.get() or "Trống"
        
        # Duyệt qua từng web đã chọn và tạo luồng riêng
        for site in selected_sites:
            self.task_count += 1
            stt = str(self.task_count)
            
            task_data = {
                "stt": stt,
                "web": site,
                "user": user_input,
                "pwd": self.entry_pass.get() or "Trống",
                "name": self.entry_name.get() or "Trống",
                "phone": self.entry_phone.get() or "Trống",
                "bank": self.entry_bank.get() or "Trống",
                "stk": self.entry_stk.get() or "Trống"
            }
            
            self._create_table_row(task_data)

    def _create_table_row(self, task_data):
        """Hàm phụ trách vẽ UI cho 1 hàng dữ liệu"""
        row_frame = ctk.CTkFrame(self.table_frame)
        row_frame.pack(fill="x", pady=2)

        lbls = {}
        lbls['stt'] = ctk.CTkLabel(row_frame, text=task_data['stt'], width=40)
        lbls['web'] = ctk.CTkLabel(row_frame, text=task_data['web'], width=70, text_color="#F39C12", font=("Arial", 12, "bold"))
        lbls['user'] = ctk.CTkLabel(row_frame, text=task_data['user'], width=120)
        lbls['pwd'] = ctk.CTkLabel(row_frame, text=task_data['pwd'], width=100)
        lbls['name'] = ctk.CTkLabel(row_frame, text=task_data['name'], width=130)
        lbls['phone'] = ctk.CTkLabel(row_frame, text=task_data['phone'], width=100)
        lbls['bank'] = ctk.CTkLabel(row_frame, text=task_data['bank'], width=90)
        lbls['stk'] = ctk.CTkLabel(row_frame, text=task_data['stk'], width=110)

        for key in ['stt', 'web', 'user', 'pwd', 'name', 'phone', 'bank', 'stk']:
            lbls[key].pack(side="left", padx=5)
        
        lbl_status = ctk.CTkLabel(row_frame, text="Đang khởi tạo...", width=180, text_color="yellow")
        lbl_status.pack(side="left", padx=5)

        action_frame = ctk.CTkFrame(row_frame, fg_color="transparent", width=120)
        action_frame.pack(side="left", padx=5)

        btn_pause = ctk.CTkButton(action_frame, text="⏸", width=40, fg_color="orange", hover_color="darkorange")
        btn_pause.is_running = True 

        def toggle_pause():
            if btn_pause.is_running:
                btn_pause.configure(text="▶", fg_color="blue", hover_color="darkblue")
                lbl_status.configure(text="Đã tạm dừng", text_color="orange")
                btn_pause.is_running = False
                self.write_log(f"Luồng {task_data['stt']} ({task_data['web']} - {task_data['user']}): Đã TẠM DỪNG.")
            else:
                btn_pause.configure(text="⏸", fg_color="orange", hover_color="darkorange")
                lbl_status.configure(text="Đang tiếp tục...", text_color="yellow")
                btn_pause.is_running = True
                self.write_log(f"Luồng {task_data['stt']} ({task_data['web']} - {task_data['user']}): TIẾP TỤC chạy.")

        btn_pause.configure(command=toggle_pause)
        btn_pause.pack(side="left", padx=2)

        btn_edit = ctk.CTkButton(action_frame, text="...", width=30, fg_color="gray", command=lambda: self.open_edit_popup(task_data, lbls))
        btn_edit.pack(side="left", padx=2)

        self.write_log(f"Đã thêm luồng {task_data['stt']} chạy cổng {task_data['web']}")

        # --- LUỒNG GIẢ LẬP ĐỂ TEST ---
        def mock_bot_run():
            time.sleep(2)
            if btn_pause.is_running:
                lbl_status.configure(text=f"Đang vào {task_data['web']}...", text_color="lightblue")
            time.sleep(3)
            if btn_pause.is_running:
                lbl_status.configure(text="✅ Thành công", text_color="green")
                self.write_log(f"Luồng {task_data['stt']} ({task_data['web']}): Đăng ký THÀNH CÔNG!")
                btn_pause.configure(state="disabled") 

        threading.Thread(target=mock_bot_run, daemon=True).start()

    def open_edit_popup(self, task_data, lbls):
        popup = ctk.CTkToplevel(self)
        popup.title(f"Sửa thông tin luồng {task_data['stt']}")
        popup.geometry("350x250")
        popup.grab_set() 
        popup.attributes("-topmost", True)

        ctk.CTkLabel(popup, text="Sửa Password:").pack(pady=(10, 0))
        entry_edit_pwd = ctk.CTkEntry(popup, width=200)
        entry_edit_pwd.insert(0, task_data['pwd'])
        entry_edit_pwd.pack(pady=5)

        ctk.CTkLabel(popup, text="Sửa Số Tài Khoản:").pack(pady=(5, 0))
        entry_edit_stk = ctk.CTkEntry(popup, width=200)
        entry_edit_stk.insert(0, task_data['stk'])
        entry_edit_stk.pack(pady=5)

        def save_edit():
            new_pwd = entry_edit_pwd.get()
            new_stk = entry_edit_stk.get()
            
            task_data['pwd'] = new_pwd
            task_data['stk'] = new_stk
            
            lbls['pwd'].configure(text=new_pwd)
            lbls['stk'].configure(text=new_stk)
            
            self.write_log(f"Luồng {task_data['stt']}: Đã cập nhật thông tin thành công.")
            popup.destroy() 

        btn_save = ctk.CTkButton(popup, text="Lưu thay đổi", fg_color="green", command=save_edit)
        btn_save.pack(pady=15)


if __name__ == "__main__":
    app = ToolApp()
    app.mainloop()