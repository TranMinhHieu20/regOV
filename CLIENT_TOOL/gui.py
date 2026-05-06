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
from path_helper import get_data_path

DOMAIN_MAP = {
    "hi144": "https://hi1444.com/Register",
    "qq88": "https://www.qq8894.com/register",
    "new88": "https://m.new8826.xyz/Account/Register",
    "f168": "https://f1686s.com/home/register",
    "c168": "https://c168a.vip/home/register",
    "sc88": "https://m.sc8888.com/home/register",
    "f8": "https://m.f8betf.cool/Account/Register",
    "mb66": "https://m.mb667.pro/Account/Register",
    "shbet": "https://m.shbetv9.top/Account/Register",
    "j88": "https://m.j855.xyz/Account/Register",
    "u888": "https://m.u8889.ink/Account/Register",
    "789bet": "https://m.vip789betj.com/Account/Register",
    "78win": "https://www.78wina1.ltd/signup",
    "junv1":"",
    "junv2":""
}

# --- PREMIUM COLORS ---
BG_COLOR = "#0B0E14"
HEADER_COLOR = "#151921"
ACCENT_COLOR = "#00D2FF"
SUCCESS_COLOR = "#00F260"
DANGER_COLOR = "#FF4B2B"

class ToolApp(ctk.CTk):
    def __init__(self, username, session_token):
        super().__init__()
        self.username = username
        self.session_token = session_token
        self.title(f"AQUA-REG DASHBOARD | {username}")
        self.geometry("1500x800")
        self.configure(fg_color=BG_COLOR)
        
        self.config_cloud = db.lay_cau_hinh_tu_cloud()
        self.task_count = 0
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.setup_ui()
        self.load_local_state()
        self.start_session_monitor()
        
    def setup_ui(self):
        self.header = ctk.CTkFrame(self, fg_color=HEADER_COLOR, corner_radius=0, border_width=1, border_color="#2C3440")
        self.header.grid(row=0, column=0, sticky="new", padx=0, pady=0)
        for i in range(4): self.header.grid_columnconfigure(i, weight=1)

        def create_input_group(label, placeholder, row, col, show=None):
            container = ctk.CTkFrame(self.header, fg_color="transparent")
            container.grid(row=row, column=col, padx=15, pady=10, sticky="ew")
            ctk.CTkLabel(container, text=label, font=("Arial", 11, "bold"), text_color=ACCENT_COLOR).pack(anchor="w")
            e = ctk.CTkEntry(container, placeholder_text=placeholder, show=show, height=35, corner_radius=8, border_color="#34495E", fg_color="#1C222D")
            e.pack(fill="x", pady=2)
            return e

        self.entry_user = create_input_group("USERNAME", "Nhập tài khoản", 0, 0)
        self.entry_pass = create_input_group("PASSWORD", "Nhập mật khẩu", 0, 1)
        self.entry_name = create_input_group("HỌ TÊN THẬT", "Họ và tên", 0, 2)
        self.entry_phone = create_input_group("SỐ ĐIỆN THOẠI", "SĐT đăng ký", 0, 3)
        self.entry_bank = create_input_group("NGÂN HÀNG", "MB, MBBANK, MBB...", 1, 0)
        self.entry_stk = create_input_group("SỐ TÀI KHOẢN", "STK nhận tiền", 1, 1)
        self.entry_rut = create_input_group("MẬT KHẨU RÚT", "PIN 6 số", 1, 2)
        self.entry_chinhanh = create_input_group("CHI NHÁNH", "CHI NHÁNH", 1, 3)
        self.entry_email = create_input_group("EMAIL", "Nhập email (nếu có)", 2, 1)


        action_container = ctk.CTkFrame(self.header, fg_color="transparent")
        action_container.grid(row=2, column=0, padx=15, pady=10, sticky="ew")
        ctk.CTkLabel(action_container, text="PROFILE HIDEMIUM", font=("Arial", 11, "bold"), text_color=ACCENT_COLOR).pack(anchor="w")
        self.combo_hidemium = ctk.CTkComboBox(action_container, values=["Scanning..."], height=35, corner_radius=8, fg_color="#1C222D", border_color="#34495E")
        self.combo_hidemium.pack(side="left", fill="x", expand=True, pady=2)
        ctk.CTkButton(action_container, text="🔄", width=35, height=35, fg_color="#2C3E50", command=self.refresh_profiles).pack(side="right", padx=(5, 0))

        self.ctrl_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.ctrl_bar.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        
        # --- SITES SELECTION AREA (RE-DESIGNED FOR PREMIUM LOOK) ---
        self.sites_frame = ctk.CTkFrame(self.ctrl_bar, fg_color="#1A1F26", corner_radius=12, border_width=1, border_color="#34495E")
        self.sites_frame.pack(side="left", padx=10, fill="both", expand=True)
        
        # Configure Grid Columns for perfect alignment
        for i in range(4): self.sites_frame.grid_columnconfigure(i, weight=1, uniform="sites_cols")

        # Header with Indicator
        header_container = ctk.CTkFrame(self.sites_frame, fg_color="transparent")
        header_container.grid(row=0, column=0, columnspan=4, sticky="ew", padx=15, pady=(10, 5))
        
        ctk.CTkLabel(header_container, text="● MỤC TIÊU VẬN HÀNH", font=("Arial", 12, "bold"), text_color=ACCENT_COLOR).pack(side="left")
        
        # SELECT ALL (Switch Style)
        self.var_all = ctk.BooleanVar()
        self.check_all = ctk.CTkCheckBox(header_container, text="CHỌN TẤT CẢ", variable=self.var_all, 
                                         command=self.toggle_select_all, font=("Arial", 10, "bold"), 
                                         text_color=SUCCESS_COLOR, checkbox_width=16, checkbox_height=16,
                                         hover_color="#1C222D")
        self.check_all.pack(side="right")

        self.sites_vars = {}
        
        # Define Grid Matrix - 4 columns layout
        matrix_sites = [
            ["c168", "f168", "sc88", "f8", "junv1"],
            ["hi144", "qq88", "new88", "mb66", "junv2"],
            ["shbet", "j88", "u888", "789bet", "78win"],
            
        ]
        
        # Build the grid
        for r_idx, row_sites in enumerate(matrix_sites):
            for c_idx, site in enumerate(row_sites):
                if site in DOMAIN_MAP:
                    var = ctk.BooleanVar()
                    cb = ctk.CTkCheckBox(self.sites_frame, text=site.upper(), variable=var, 
                                         font=("Arial", 11, "bold"), text_color="#BDC3C7",
                                         checkbox_width=18, checkbox_height=18, 
                                         border_color=ACCENT_COLOR, hover_color="#2C3E50")
                    cb.grid(row=r_idx + 1, column=c_idx, padx=15, pady=5, sticky="w")
                    self.sites_vars[site] = var

        self.btn_run = ctk.CTkButton(self.ctrl_bar, text="🚀 BẮT ĐẦU CHẠY", fg_color=ACCENT_COLOR, hover_color="#00B4DB", height=40, font=("Arial", 13, "bold"), text_color="black", command=self.add_task)
        self.btn_run.pack(side="left", padx=10)
        ctk.CTkButton(self.ctrl_bar, text="📂 NHẬP FILE", fg_color="#27AE60", command=self.import_file, height=40).pack(side="left", padx=5)
        ctk.CTkButton(self.ctrl_bar, text="🔑 ĐỔI MK", fg_color="#5D6D7E", command=self.open_change_password_popup, height=40).pack(side="right", padx=5)

        self.table_scroll = ctk.CTkScrollableFrame(self, label_text="DASHBOARD - QUẢN LÝ LUỒNG CHẠY ĐA NHIỆM", label_font=("Arial", 13, "bold"), fg_color=HEADER_COLOR, corner_radius=15, border_width=1, border_color="#2C3440")
        self.table_scroll.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.table_frame = self.table_scroll
        for i in range(13): self.table_frame.grid_columnconfigure(i, weight=1)
        headers = ["STT", "Web", "Profile", "User", "Pass", "Họ Tên", "SĐT", "Bank", "STK", "PIN", "Email", "Trạng Thái", "Thao Tác"]
        for idx, h in enumerate(headers):
            ctk.CTkLabel(self.table_frame, text=h, font=("Arial", 11, "bold"), text_color="#ABB2B9", fg_color="#1C222D", height=35).grid(row=0, column=idx, padx=1, pady=5, sticky="ew")

        self.log_box = ctk.CTkTextbox(self, height=120, font=("Consolas", 12), fg_color="#07090C", border_width=1, border_color="#2C3440", text_color=SUCCESS_COLOR)
        self.log_box.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.refresh_profiles()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def toggle_select_all(self):
        val = self.var_all.get()
        for var in self.sites_vars.values():
            var.set(val)

    def write_log(self, msg):
        timestamp = time.strftime("[%H:%M:%S] ")
        self.log_box.insert("end", f"{timestamp} {msg}\n")
        self.log_box.see("end")

    def refresh_profiles(self):
        profiles = utils.get_all_running_hidemium()
        if profiles:
            display_vals = [f"Tên: {p['profile']} (Port: {p['port']})" for p in profiles]
            self.combo_hidemium.configure(values=display_vals); self.combo_hidemium.set(display_vals[0])
            self.write_log(f"Đã cập nhật {len(profiles)} Profile.")
        else:
            self.combo_hidemium.configure(values=["No Active Profiles"]); self.combo_hidemium.set("No Active Profiles")

    def on_closing(self):
        self.save_local_state(); self.destroy(); os._exit(0)
        
    def save_local_state(self):
        state = {
            "user": self.entry_user.get(), "pwd": self.entry_pass.get(),
            "name": self.entry_name.get(), "phone": self.entry_phone.get(),
            "bank": self.entry_bank.get(), "stk": self.entry_stk.get(),
            "rut": self.entry_rut.get(), "branch": self.entry_chinhanh.get(),
            "email": self.entry_email.get(), "sites": {k: v.get() for k, v in self.sites_vars.items()}
        }
        try:
            with open(get_data_path("local_state.json"), "w", encoding="utf-8") as f: json.dump(state, f)
        except: pass

    def load_local_state(self):
        try:
            state_path = get_data_path("local_state.json")
            if os.path.exists(state_path):
                with open(state_path, "r", encoding="utf-8") as f: state = json.load(f)
                self.entry_user.insert(0, state.get("user", ""))
                self.entry_pass.insert(0, state.get("pwd", ""))
                self.entry_name.insert(0, state.get("name", ""))
                self.entry_phone.insert(0, state.get("phone", ""))
                self.entry_bank.insert(0, state.get("bank", ""))
                self.entry_stk.insert(0, state.get("stk", ""))
                self.entry_rut.insert(0, state.get("rut", ""))
                self.entry_chinhanh.insert(0, state.get("branch", ""))
                self.entry_email.insert(0, state.get("email", ""))
                saved_sites = state.get("sites", {})
                for k, v in saved_sites.items():
                    if k in self.sites_vars: self.sites_vars[k].set(v)
        except: pass

    def import_file(self):
        filepath = filedialog.askopenfilename(title="Chọn File", filetypes=[("Text files", "*.txt")])
        if not filepath: return
        try:
            with open(filepath, 'r', encoding='utf-8') as f: lines = f.readlines()
            selected_sites = [site for site, var in self.sites_vars.items() if var.get()]
            if not selected_sites:
                self.write_log("⚠️ LỖI NGƯỜI DÙNG: Bạn chưa chọn Cổng Game nào!")
                return

            for idx, line in enumerate(lines):
                line = line.strip()
                if not line: continue 
                data = line.split('|')
                if len(data) < 7:
                    self.write_log(f"⚠️ LỖI FILE: Dòng {idx+1} không đủ 7 cột (User|Pass|Tên|SĐT|Bank|STK|PIN).")
                    continue
                
                selected_hide = self.combo_hidemium.get()
                if "Port:" not in selected_hide:
                    self.write_log("⚠️ LỖI: Bạn chưa chọn Profile Hidemium hợp lệ!")
                    return
                
                port = selected_hide.split("(Port: ")[1].replace(")", "")
                p_name = selected_hide.split(" (Port:")[0].replace("Tên: ", "")
                for site in selected_sites:
                    self.task_count += 1
                    task_data = {
                        "stt": str(self.task_count), "web": site, "user": data[0], "pwd": data[1],
                        "name": data[2], "phone": data[3], "bank": data[4], "stk": data[5],
                        "rut": data[6], "branch": data[7] if len(data) >= 8 else "Hà Nội",
                        "email": data[8] if len(data) >= 9 else "",
                        "port": port, "profile": p_name
                    }
                    self._create_table_row(task_data)
            self.write_log("✅ Đã nhập danh sách từ file thành công.")
        except Exception as e:
            self.write_log(f"❌ Lỗi xử lý file: {str(e)}")

    def add_task(self):
        selected_sites = [site for site, var in self.sites_vars.items() if var.get()]
        if not selected_sites:
            self.write_log("⚠️ LỖI NGƯỜI DÙNG: Vui lòng tick chọn ít nhất 1 Cổng game!")
            return
        
        selected_hide = self.combo_hidemium.get()
        if "Port:" not in selected_hide:
            self.write_log("⚠️ LỖI NGƯỜI DÙNG: Bạn chưa chọn Profile Hidemium nào!")
            return

        if not self.entry_user.get() or self.entry_user.get() == "Trống":
            self.write_log("⚠️ THIẾU THÔNG TIN: Vui lòng nhập 'Username'!")
            return

        port = selected_hide.split("(Port: ")[1].replace(")", "")
        p_name = selected_hide.split(" (Port:")[0].replace("Tên: ", "")
        for site in selected_sites:
            self.task_count += 1
            task_data = {
                "stt": str(self.task_count), "web": site, "user": self.entry_user.get(), "pwd": self.entry_pass.get() or "123456",
                "name": self.entry_name.get() or "Vô Danh", "phone": self.entry_phone.get() or "0900000000", 
                "bank": self.entry_bank.get() or "MB", "stk": self.entry_stk.get() or "111222333", 
                "rut": self.entry_rut.get() or "112233", "branch": self.entry_chinhanh.get() or "Hà Nội",
                "email": self.entry_email.get() or "",
                "port": port, "profile": p_name
            }
            self._create_table_row(task_data)

    def _create_table_row(self, task_data):
        row_idx = int(task_data['stt'])
        def create_cell(text, color="#E0E0E0", weight="normal"):
            entry = ctk.CTkEntry(self.table_frame, fg_color="transparent", border_width=0, text_color=color, font=("Arial", 12, weight), justify="center")
            entry.insert(0, str(text)); entry.configure(state="readonly")
            return entry

        lbls = { 'stt': create_cell(task_data['stt']), 'web': create_cell(task_data['web'], color="#F39C12", weight="bold"), 'profile': create_cell(task_data.get('profile', 'N/A'), color="cyan"), 'user': create_cell(task_data['user']), 'pwd': create_cell(task_data['pwd']), 'name': create_cell(task_data['name']), 'phone': create_cell(task_data['phone']), 'bank': create_cell(task_data['bank']), 'stk': create_cell(task_data['stk']), 'rut': create_cell(task_data['rut'], color="#E74C3C"), 'email': create_cell(task_data.get('email', 'N/A')) }
        cols = ['stt', 'web', 'profile', 'user', 'pwd', 'name', 'phone', 'bank', 'stk', 'rut', 'email']
        for col_idx, key in enumerate(cols): lbls[key].grid(row=row_idx, column=col_idx, padx=1, pady=3, sticky="ew")
        
        lbl_status = ctk.CTkLabel(self.table_frame, text="INITIALIZING...", text_color="yellow", font=("Arial", 11, "bold"))
        lbl_status.grid(row=row_idx, column=11, padx=1, pady=3, sticky="ew")
        action_frame = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        action_frame.grid(row=row_idx, column=12, padx=1, pady=3)

        btn_pause = ctk.CTkButton(action_frame, text="⏸", width=30, height=25, fg_color="#F39C12")
        btn_pause.is_running = True 
        def toggle_pause():
            if btn_pause.is_running:
                btn_pause.configure(text="▶", fg_color="#2980B9"); lbl_status.configure(text="PAUSED", text_color="#F39C12"); btn_pause.is_running = False
            else:
                btn_pause.configure(text="⏸", fg_color="#F39C12"); lbl_status.configure(text="RESUMING...", text_color="yellow"); btn_pause.is_running = True
        btn_pause.configure(command=toggle_pause); btn_pause.pack(side="left", padx=1)
        ctk.CTkButton(action_frame, text="⚙", width=30, height=25, fg_color="#5D6D7E", command=lambda: self.open_edit_popup(task_data, lbls)).pack(side="left", padx=1)
        btn_delete = ctk.CTkButton(action_frame, text="🗑", width=30, height=25, fg_color=DANGER_COLOR)
        def delete_row():
            task_data['is_deleted'] = True
            for key in cols: lbls[key].destroy()
            lbl_status.destroy(); action_frame.destroy()
        btn_delete.configure(command=delete_row); btn_delete.pack(side="left", padx=1)

        def run_bot_thread():
            async def run_pw():
                try:
                    full_url = DOMAIN_MAP.get(task_data['web'].lower())
                    domain_name = full_url.split("//")[-1].split("/")[0]
                    cfg = self.config_cloud.get(domain_name, self.config_cloud.get("default"))
                    ws_url = utils.get_websocket_url(task_data['port'])
                    if not ws_url:
                        self.after(0, lambda: lbl_status.configure(text="❌ LỖI KẾT NỐI", text_color=DANGER_COLOR))
                        self.write_log(f"❌ LUỒNG {task_data['stt']}: Không tìm thấy Profile trên Port {task_data['port']}. Hãy mở Hidemium!")
                        return
                    async with async_playwright() as p:
                        browser = await p.chromium.connect_over_cdp(ws_url)
                        
                        # Sử dụng context mặc định đang có sẵn để chạy chung 1 cửa sổ (nhiều Tab)
                        if browser.contexts:
                            context = browser.contexts[0]
                            await context.add_init_script("""
                                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                                window.Element.prototype._addEventListener = window.Element.prototype.addEventListener;
                                window.Element.prototype.addEventListener = function(a,b,c) {
                                    if(a==='beforeunload') return;
                                    this._addEventListener(a,b,c);
                                };
                            """)
                        else:
                            context = await browser.new_context()
                            
                        page = await context.new_page()
                        my_data = { "username": task_data['user'], "password": task_data['pwd'], "ten_that": task_data['name'], "sdt": task_data['phone'], "ten_bank": task_data['bank'], "stk_bank": task_data['stk'], "pin_bank": task_data['rut'], "branch": task_data.get('branch', 'Hà Nội'), "email": task_data.get('email', '') }
                        def report_status(msg):
                            if not task_data.get('is_deleted', False): self.after(0, lambda: lbl_status.configure(text=msg.upper()))
                        def is_aborted(): return task_data.get('is_deleted', False)
                        await flows.run_full_flow(page, full_url, my_data, cfg, report_status, is_aborted)
                        if not is_aborted(): self.after(0, lambda: lbl_status.configure(text="SUCCESS ✅", text_color=SUCCESS_COLOR))
                except Exception as e: self.after(0, lambda: lbl_status.configure(text="ERROR ❌", text_color=DANGER_COLOR))
                finally: self.after(0, lambda: btn_pause.configure(state="disabled"))
            loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop); loop.run_until_complete(run_pw()); loop.close()
        threading.Thread(target=run_bot_thread, daemon=True).start()

    def open_edit_popup(self, task_data, lbls):
        popup = ctk.CTkToplevel(self); popup.title(f"Edit {task_data['stt']}"); popup.geometry("380x520"); popup.configure(fg_color=HEADER_COLOR); popup.grab_set(); popup.attributes("-topmost", True)
        scroll = ctk.CTkScrollableFrame(popup, fg_color="transparent"); scroll.pack(fill="both", expand=True, padx=20, pady=20)
        entries = {}
        fields = [("Username", "user"), ("Password", "pwd"), ("Họ Tên", "name"), ("SĐT", "phone"), ("Ngân hàng", "bank"), ("Số tài khoản", "stk"), ("Mật khẩu rút", "rut"), ("Chi nhánh", "branch"), ("Email", "email")]
        for label_text, key in fields:
            ctk.CTkLabel(scroll, text=f"{label_text}:", font=("Arial", 11, "bold"), text_color=ACCENT_COLOR).pack(anchor="w", pady=(10, 0))
            e = ctk.CTkEntry(scroll, width=300, fg_color="#1C222D", border_color="#34495E"); e.insert(0, str(task_data.get(key, ""))); e.pack(pady=2, anchor="w"); entries[key] = e
        def save_edit():
            for _, key in fields:
                new_val = entries[key].get(); task_data[key] = new_val
                if key in lbls: lbls[key].configure(state="normal"); lbls[key].delete(0, 'end'); lbls[key].insert(0, new_val); lbls[key].configure(state="readonly")
            popup.destroy() 
        ctk.CTkButton(popup, text="SAVE CHANGES", fg_color=ACCENT_COLOR, text_color="black", command=save_edit).pack(pady=20)

    def open_change_password_popup(self):
        popup = ctk.CTkToplevel(self); popup.title("Password"); popup.geometry("350x320"); popup.configure(fg_color=HEADER_COLOR); popup.grab_set(); popup.attributes("-topmost", True)
        ctk.CTkLabel(popup, text="Old:").pack(pady=10); entry_old = ctk.CTkEntry(popup, show="*", width=250); entry_old.pack()
        ctk.CTkLabel(popup, text="New:").pack(pady=10); entry_new = ctk.CTkEntry(popup, show="*", width=250); entry_new.pack()
        def change_pwd():
            success, msg = db.change_password(self.username, entry_old.get(), entry_new.get()); messagebox.showinfo("Info", msg); popup.destroy()
        ctk.CTkButton(popup, text="SAVE", fg_color=SUCCESS_COLOR, text_color="black", command=change_pwd).pack(pady=20)

    def start_session_monitor(self):
        def monitor():
            while True:
                time.sleep(20)
                if not db.check_session(self.username, self.session_token):
                    self.after(0, lambda: (messagebox.showwarning("Alert", "Logged out!"), self.destroy(), os._exit(0))); break
        threading.Thread(target=monitor, daemon=True).start()