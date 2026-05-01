import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import customtkinter as ctk
import threading
import time
import asyncio
import json
from tkinter import filedialog, messagebox
from playwright.async_api import async_playwright

from SERVER_API import db
from CLIENT_TOOL import utils
from CLIENT_TOOL import flows

DOMAIN_MAP = {
    "hi": "https://hi1444.com/Register",
    "qq": "https://www.qq8894.com/register",
    "new": "https://new8826.xyz/Register",
    "f168": "https://f1686s.com/home/register",
    "c168": "https://c168a.vip/home/register",
    "sc88": "https://m.sc8888.com/home/register"
}

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ToolApp(ctk.CTk):
    def __init__(self, username='admin', session_token=None):
        super().__init__()
        self.username = username
        self.session_token = session_token
        self.title(f"AQUA-REG-TOOL V.4.0")
        self.geometry("1300x850") 
        
        self.config_cloud = db.lay_cau_hinh_tu_cloud()
        if not self.config_cloud:
            messagebox.showerror("Lỗi Cấu Hình", "Không thể lấy cấu hình Web từ Database.") 
        
        # Bắt đầu luồng kiểm tra session liên tục
        if self.session_token:
            self.start_session_monitor()
        
        # Bắt sự kiện khi tắt cửa sổ để tự động lưu cấu hình
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Cho phép kéo giãn cửa sổ tùy ý
        self.resizable(True, True)
        self.minsize(1100, 700) 
        
        self.task_count = 0
        self.tasks_data = [] 

        # Cấu hình grid cho cửa sổ chính
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1) # Bảng quản lý

        # ================= TOP HEADER (USER INFO & PWD) =================
        self.header_bar = ctk.CTkFrame(self, fg_color="#341F97", height=50, corner_radius=0)
        self.header_bar.grid(row=0, column=0, sticky="ew")
        self.header_bar.pack_propagate(False)

        self.lbl_welcome = ctk.CTkLabel(self.header_bar, text=f"👤 Xin chào: {self.username}", 
                                       font=("Arial", 14, "bold"), text_color="white")
        self.lbl_welcome.pack(side="left", padx=20)

        self.btn_change_pwd = ctk.CTkButton(self.header_bar, text="🔑 ĐỔI MẬT KHẨU", fg_color="#E67E22", 
                                            hover_color="#CA6F1E", width=120, height=30, font=("Arial", 11, "bold"),
                                            command=self.open_change_password_popup)
        self.btn_change_pwd.pack(side="right", padx=20)

        # ================= KHU VỰC 1: NHẬP LIỆU (CARD STYLE) =================
        self.frame_data = ctk.CTkFrame(self, fg_color="#1E272E", corner_radius=20, border_width=1, border_color="#34495E")
        self.frame_data.grid(row=1, column=0, padx=20, pady=(15, 10), sticky="nsew")
        
        for i in range(3): self.frame_data.grid_columnconfigure(i, weight=1)

        # Hàng 1
        self.create_input_field(self.frame_data, "Username", "entry_user", "Tên đăng nhập...", 0, 0)
        self.create_input_field(self.frame_data, "Password", "entry_pass", "Mật khẩu web...", 0, 1)
        self.create_input_field(self.frame_data, "Họ và tên", "entry_name", "Họ tên thật...", 0, 2)

        # Hàng 2
        self.create_input_field(self.frame_data, "Số điện thoại", "entry_phone", "09xxxxxxxx", 1, 0)
        self.create_input_field(self.frame_data, "Tên ngân hàng", "entry_bank", "Ví dụ: MB Bank", 1, 1)
        self.create_input_field(self.frame_data, "Số tài khoản", "entry_stk", "Số TK ngân hàng", 1, 2)

        # Hàng 3 (Mật khẩu rút tiền & Button Start)
        self.create_input_field(self.frame_data, "Mật khẩu rút tiền", "entry_rut", "Mã PIN 6 số", 2, 0)

        # ================= KHU VỰC 2: CẤU HÌNH (STK) =================
        self.frame_config = ctk.CTkFrame(self, fg_color="#2C3E50", corner_radius=15)
        self.frame_config.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")

        # Checkbox Web
        self.site_frame = ctk.CTkFrame(self.frame_config, fg_color="transparent")
        self.site_frame.pack(side="left", padx=10, pady=10)
        
        self.sites_vars = {
            "C168": ctk.BooleanVar(value=True), "HI": ctk.BooleanVar(value=False),
            "NEW": ctk.BooleanVar(value=False), "SC88": ctk.BooleanVar(value=False),
            "F168": ctk.BooleanVar(value=False), "QQ": ctk.BooleanVar(value=False),
        }
        for site, var in self.sites_vars.items():
            ctk.CTkCheckBox(self.site_frame, text=site, variable=var, width=65, font=("Arial", 11, "bold")).pack(side="left", padx=5)

        # Buttons Right
        self.btn_frame = ctk.CTkFrame(self.frame_config, fg_color="transparent")
        self.btn_frame.pack(side="right", padx=10)

        self.btn_start = ctk.CTkButton(self.btn_frame, text="▶ THÊM & CHẠY LUỒNG", fg_color="#00B894", hover_color="#009473", 
                                      font=("Arial", 13, "bold"), height=40, command=self.add_task)
        self.btn_start.pack(side="right", padx=5)

        self.btn_scan_hide = ctk.CTkButton(self.btn_frame, text="🔄 Quét Hidemium", fg_color="#0984E3", hover_color="#0870C1", command=self.scan_hidemium)
        self.btn_scan_hide.pack(side="right", padx=5)
        
        self.combo_hidemium = ctk.CTkComboBox(self.btn_frame, values=["Chưa quét Hidemium..."], width=180)
        self.combo_hidemium.pack(side="right", padx=5)

        # ================= KHU VỰC 3: BẢNG QUẢN LÝ =================
        self.table_frame = ctk.CTkScrollableFrame(self, fg_color="#1E272E", corner_radius=15, border_width=1, border_color="#34495E")
        self.table_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        
        # Configure Table Columns
        self.headers = [
            ("STT", 40), ("Web", 60), ("Profile", 70), ("Username", 120), ("Password", 100), 
            ("Họ Tên", 120), ("SĐT", 100), ("Bank", 90), ("STK", 110), 
            ("Trạng thái", 200), ("Hành động", 110)
        ]
        for i in range(len(self.headers)): self.table_frame.grid_columnconfigure(i, weight=1)

        for col_idx, (text, width) in enumerate(self.headers):
            lbl = ctk.CTkLabel(self.table_frame, text=text, font=("Arial", 12, "bold"), fg_color="#341F97", 
                               text_color="white", height=35, corner_radius=5)
            lbl.grid(row=0, column=col_idx, padx=2, pady=5, sticky="ew")

        # ================= KHU VỰC 4: LOG =================
        self.log_box = ctk.CTkTextbox(self, height=100, fg_color="#000000", text_color="#55E6C1", font=("Consolas", 12), corner_radius=10)
        self.log_box.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        self.write_log("Hệ thống AQUA-REG-TOOL đã sẵn sàng!")
        
        # Tải cấu hình cũ (nếu có)
        self.load_local_state()

    def create_input_field(self, parent, label_text, attr_name, placeholder, row, col):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=col, padx=15, pady=10, sticky="nsew")
        
        ctk.CTkLabel(frame, text=label_text, font=("Arial", 11, "bold"), text_color="#BDC3C7").pack(anchor="w", padx=2)
        entry = ctk.CTkEntry(frame, placeholder_text=placeholder, height=35, border_color="#34495E", fg_color="#2C3E50")
        entry.pack(fill="x", pady=(2, 0))
        setattr(self, attr_name, entry)

    # ================= CÁC HÀM XỬ LÝ (LOGIC) =================
    
    def on_closing(self):
        self.save_local_state()
        self.destroy()
        os._exit(0)
        
    def save_local_state(self):
        state = {
            "user": self.entry_user.get(),
            "pwd": self.entry_pass.get(),
            "name": self.entry_name.get(),
            "phone": self.entry_phone.get(),
            "bank": self.entry_bank.get(),
            "stk": self.entry_stk.get(),
            "rut": self.entry_rut.get(),
            "sites": {k: v.get() for k, v in self.sites_vars.items()}
        }
        try:
            with open("local_state.json", "w", encoding="utf-8") as f:
                json.dump(state, f)
        except: pass

    def load_local_state(self):
        try:
            if os.path.exists("local_state.json"):
                with open("local_state.json", "r", encoding="utf-8") as f:
                    state = json.load(f)
                
                self.entry_user.insert(0, state.get("user", ""))
                self.entry_pass.insert(0, state.get("pwd", ""))
                self.entry_name.insert(0, state.get("name", ""))
                self.entry_phone.insert(0, state.get("phone", ""))
                self.entry_bank.insert(0, state.get("bank", ""))
                self.entry_stk.insert(0, state.get("stk", ""))
                self.entry_rut.insert(0, state.get("rut", ""))
                
                saved_sites = state.get("sites", {})
                for k, v in saved_sites.items():
                    if k in self.sites_vars:
                        self.sites_vars[k].set(v)
        except: pass

    def scan_hidemium(self):
        self.write_log("Đang quét các Profile Hidemium đang mở...")
        profiles = utils.get_all_running_hidemium()
        current_selection = self.combo_hidemium.get()
        
        if not profiles:
            self.combo_hidemium.configure(values=["Không tìm thấy Hidemium"])
            self.combo_hidemium.set("Không tìm thấy Hidemium")
            self.hidemium_list = []
            self.write_log("❌ Không có cửa sổ Hidemium nào đang mở!")
        else:
            self.hidemium_list = profiles
            display_values = []
            for p in profiles:
                # Dùng tên Profile thực tế trích xuất từ Hidemium thay vì đếm số
                display_values.append(f"Tên: {p['profile']} (Port: {p['port']})")
                
            self.combo_hidemium.configure(values=display_values)
            
            # Giữ nguyên lựa chọn cũ nếu nó vẫn còn đang mở
            if current_selection in display_values:
                self.combo_hidemium.set(current_selection)
            else:
                self.combo_hidemium.set(display_values[0])
                
            self.write_log(f"✅ Đã tìm thấy {len(profiles)} cửa sổ Hidemium.")

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
                        selected_hide_text = self.combo_hidemium.get()
                        port = "unknown"
                        profile_name = "N/A"
                        if "Port:" in selected_hide_text:
                            parts = selected_hide_text.split(" (Port: ")
                            if len(parts) == 2:
                                profile_name = parts[0].replace("Tên: ", "").strip()
                                port = parts[1].replace(")", "").strip()
                            
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
                                "stk": data[5],
                                "rut": data[6] if len(data) > 6 else "112233",
                                "port": port,
                                "profile": profile_name
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

        selected_hide_text = self.combo_hidemium.get()
        if "Port:" not in selected_hide_text:
            self.write_log("⚠️ LỖI: Bạn chưa chọn Profile Hidemium hợp lệ!")
            return
            
        port = "unknown"
        profile_name = "N/A"
        parts = selected_hide_text.split(" (Port: ")
        if len(parts) == 2:
            profile_name = parts[0].replace("Tên: ", "").strip()
            port = parts[1].replace(")", "").strip()
            
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
                "stk": self.entry_stk.get() or "Trống",
                "rut": self.entry_rut.get() or "112233",
                "port": port,
                "profile": profile_name
            }
            
            self._create_table_row(task_data)

    def _create_table_row(self, task_data):
        """Hàm phụ trách vẽ UI cho 1 hàng dữ liệu bằng Grid"""
        row_idx = int(task_data['stt']) # Dùng STT làm số hàng
        
        def create_selectable_cell(text, width, text_color="white", font=("Arial", 12)):
            # Dùng justify="center" để căn giữa giống Header
            entry = ctk.CTkEntry(self.table_frame, width=width, fg_color="transparent", border_width=0, text_color=text_color, font=font, justify="center")
            entry.insert(0, str(text))
            entry.configure(state="readonly")
            return entry

        lbls = {}
        lbls['stt'] = create_selectable_cell(task_data['stt'], 35)
        lbls['web'] = create_selectable_cell(task_data['web'], 55, text_color="#F39C12", font=("Arial", 12, "bold"))
        lbls['profile'] = create_selectable_cell(task_data.get('profile', 'N/A'), 60, text_color="cyan")
        lbls['user'] = create_selectable_cell(task_data['user'], 110)
        lbls['pwd'] = create_selectable_cell(task_data['pwd'], 90)
        lbls['name'] = create_selectable_cell(task_data['name'], 110)
        lbls['phone'] = create_selectable_cell(task_data['phone'], 90)
        lbls['bank'] = create_selectable_cell(task_data['bank'], 80)
        lbls['stk'] = create_selectable_cell(task_data['stk'], 110)

        cols = ['stt', 'web', 'profile', 'user', 'pwd', 'name', 'phone', 'bank', 'stk']
        for col_idx, key in enumerate(cols):
            lbls[key].grid(row=row_idx, column=col_idx, padx=3, pady=2, sticky="ew")
        
        lbl_status = ctk.CTkLabel(self.table_frame, text="Đang khởi tạo...", width=180, text_color="yellow")
        lbl_status.grid(row=row_idx, column=9, padx=3, pady=2, sticky="ew")

        action_frame = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        action_frame.grid(row=row_idx, column=10, padx=3, pady=2)

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
        
        btn_delete = ctk.CTkButton(action_frame, text="🗑", width=30, fg_color="#C0392B", hover_color="#922B21")
        
        def delete_row():
            task_data['is_deleted'] = True
            for key in cols:
                lbls[key].destroy()
            lbl_status.destroy()
            action_frame.destroy()
            self.write_log(f"Đã XÓA luồng {task_data['stt']} ({task_data['web']}) khỏi hệ thống!")

        btn_delete.configure(command=delete_row)
        btn_delete.pack(side="left", padx=2)

        self.write_log(f"Đã thêm luồng {task_data['stt']} chạy cổng {task_data['web']} trên Port {task_data.get('port', 'N/A')}")

        def run_bot_thread():
            async def run_pw():
                try:
                    full_url = DOMAIN_MAP.get(task_data['web'].lower())
                    if not full_url:
                        lbl_status.configure(text="❌ Lỗi tên miền", text_color="red")
                        return

                    domain_name = full_url.split("//")[-1].split("/")[0]
                    cfg = self.config_cloud.get(domain_name, self.config_cloud.get("default"))

                    ws_url = utils.get_websocket_url(task_data['port'])
                    if not ws_url:
                        lbl_status.configure(text="❌ Lỗi kết nối Port", text_color="red")
                        return
                    
                    lbl_status.configure(text=f"Đang kết nối Profile...", text_color="yellow")
                    
                    async with async_playwright() as p:
                        browser = await p.chromium.connect_over_cdp(ws_url)
                        context = browser.contexts[0]
                        page = await context.new_page()
                        
                        lbl_status.configure(text=f"Đang chạy {task_data['web']}...", text_color="lightblue")
                        
                        my_data = {
                            "username": task_data['user'],
                            "password": task_data['pwd'],
                            "ten_that": task_data['name'],
                            "sdt": task_data['phone'],
                            "ten_bank": task_data['bank'],
                            "stk_bank": task_data['stk'],
                            "pin_bank": task_data.get('rut', '112233')
                        }
                        
                        def report_status(msg):
                            # Không cập nhật UI nếu đã xóa
                            if not task_data.get('is_deleted', False):
                                self.after(0, lambda: lbl_status.configure(text=msg))
                                
                        def is_aborted():
                            return task_data.get('is_deleted', False)
                        
                        await flows.run_full_flow(page, full_url, my_data, cfg, report_status, is_aborted)
                        
                        if is_aborted():
                            return
                            
                        if not task_data.get('is_deleted', False):
                            lbl_status.configure(text="✅ Thành công", text_color="green")
                            self.write_log(f"Luồng {task_data['stt']} ({task_data['web']}): Đăng ký THÀNH CÔNG!")
                        
                except Exception as e:
                    lbl_status.configure(text="❌ Lỗi kịch bản", text_color="red")
                    self.write_log(f"Lỗi luồng {task_data['stt']}: {str(e)}")
                finally:
                    btn_pause.configure(state="disabled") 

            # Tạo event loop riêng cho thread này
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(run_pw())
            loop.close()

        threading.Thread(target=run_bot_thread, daemon=True).start()

    def open_edit_popup(self, task_data, lbls):
        popup = ctk.CTkToplevel(self)
        popup.title(f"Sửa thông tin luồng {task_data['stt']}")
        popup.geometry("380x500")
        popup.grab_set() 
        popup.attributes("-topmost", True)

        scroll = ctk.CTkScrollableFrame(popup, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        entries = {}
        fields = [
            ("Username", "user"),
            ("Password", "pwd"),
            ("Họ Tên", "name"),
            ("SĐT", "phone"),
            ("Ngân hàng", "bank"),
            ("Số tài khoản", "stk"),
            ("Mật khẩu rút", "rut")
        ]

        for label_text, key in fields:
            ctk.CTkLabel(scroll, text=f"Sửa {label_text}:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(5, 0))
            e = ctk.CTkEntry(scroll, width=300)
            e.insert(0, str(task_data.get(key, "")))
            e.pack(pady=2, anchor="w")
            entries[key] = e

        def save_edit():
            for _, key in fields:
                new_val = entries[key].get()
                task_data[key] = new_val
                # Cập nhật UI Entry (cần đổi sang normal mới sửa được text)
                if key in lbls:
                    lbls[key].configure(state="normal")
                    lbls[key].delete(0, 'end')
                    lbls[key].insert(0, new_val)
                    lbls[key].configure(state="readonly")
            
            self.write_log(f"Luồng {task_data['stt']}: Đã cập nhật thông tin thành công.")
            popup.destroy() 

        btn_save = ctk.CTkButton(popup, text="Lưu thay đổi", fg_color="green", command=save_edit)
        btn_save.pack(pady=10)

    def open_change_password_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Đổi Mật Khẩu")
        popup.geometry("350x300")
        popup.grab_set()
        popup.attributes("-topmost", True)

        ctk.CTkLabel(popup, text="Mật khẩu cũ:").pack(pady=(20, 5))
        entry_old_pwd = ctk.CTkEntry(popup, show="*", width=250)
        entry_old_pwd.pack(pady=5)

        ctk.CTkLabel(popup, text="Mật khẩu mới:").pack(pady=5)
        entry_new_pwd = ctk.CTkEntry(popup, show="*", width=250)
        entry_new_pwd.pack(pady=5)
        
        lbl_msg = ctk.CTkLabel(popup, text="", text_color="red")
        lbl_msg.pack(pady=5)

        def change_pwd_action():
            old_pwd = entry_old_pwd.get()
            new_pwd = entry_new_pwd.get()
            
            if not old_pwd or not new_pwd:
                lbl_msg.configure(text="Vui lòng nhập đủ thông tin!", text_color="red")
                return
                
            btn_save_pwd.configure(state="disabled", text="Đang xử lý...")
            
            def process():
                success, msg = db.change_password(self.username, old_pwd, new_pwd)
                if success:
                    lbl_msg.configure(text=msg, text_color="green")
                    popup.after(2000, popup.destroy)
                else:
                    lbl_msg.configure(text=msg, text_color="red")
                    btn_save_pwd.configure(state="normal", text="Đổi Mật Khẩu")
                    
            threading.Thread(target=process, daemon=True).start()

        btn_save_pwd = ctk.CTkButton(popup, text="Lưu Mật Khẩu", fg_color="green", command=change_pwd_action)
        btn_save_pwd.pack(pady=15)

    def start_session_monitor(self):
        def monitor():
            while True:
                time.sleep(10) # Kiểm tra mỗi 10 giây
                is_valid = db.check_session(self.username, self.session_token)
                if not is_valid:
                    self.write_log("🚨 PHÁT HIỆN ĐĂNG NHẬP Ở NƠI KHÁC! Đang đóng ứng dụng...")
                    # Dùng messagebox để hiện thông báo rồi tắt app
                    def force_close():
                        messagebox.showwarning("Cảnh báo bảo mật", "Tài khoản của bạn vừa được đăng nhập ở nơi khác!\nPhiên làm việc này sẽ bị đóng lại.")
                        self.destroy()
                        os._exit(0)
                    self.after(0, force_close)
                    break
        threading.Thread(target=monitor, daemon=True).start()

if __name__ == "__main__":
    app = ToolApp()
    app.mainloop()