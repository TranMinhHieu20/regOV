import sys
import os
import subprocess
import threading
import customtkinter as ctk

# Thêm đường dẫn gốc vào sys.path để import chéo
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from SERVER_API import db
from CLIENT_TOOL.gui import ToolApp

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AuthApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AQUA-REG-TOOL - Đăng Nhập Hệ Thống")
        self.geometry("450x550")
        self.resizable(False, False)
        
        # Tabs
        self.tabview = ctk.CTkTabview(self, width=400, height=450)
        self.tabview.pack(pady=20, padx=20)
        
        self.tab_login = self.tabview.add("Đăng Nhập")
        # self.tab_register = self.tabview.add("Đăng Ký")
        
        self.setup_login_tab()
        # self.setup_register_tab()

    def setup_login_tab(self):
        ctk.CTkLabel(self.tab_login, text="ĐĂNG NHẬP HỆ THỐNG", font=("Arial", 20, "bold")).pack(pady=(20, 30))
        
        self.entry_login_user = ctk.CTkEntry(self.tab_login, placeholder_text="Username hoặc Email", width=250, height=40)
        self.entry_login_user.pack(pady=10)
        
        self.entry_login_pass = ctk.CTkEntry(self.tab_login, placeholder_text="Password", show="*", width=250, height=40)
        self.entry_login_pass.pack(pady=10)
        
        # Nút Quên mật khẩu
        self.lbl_forgot = ctk.CTkLabel(self.tab_login, text="Quên mật khẩu?", text_color="#3498DB", cursor="hand2")
        self.lbl_forgot.pack(pady=0)
        self.lbl_forgot.bind("<Button-1>", self.open_forgot_password_popup)
        
        self.lbl_login_msg = ctk.CTkLabel(self.tab_login, text="", text_color="red")
        self.lbl_login_msg.pack(pady=5)
        
        self.btn_login = ctk.CTkButton(self.tab_login, text="Đăng Nhập", font=("Arial", 15, "bold"), width=250, height=45, fg_color="#2980B9", hover_color="#1F618D", command=self.handle_login)
        self.btn_login.pack(pady=10)

    def setup_register_tab(self):
        ctk.CTkLabel(self.tab_register, text="ĐĂNG KÝ TÀI KHOẢN", font=("Arial", 20, "bold")).pack(pady=(20, 20))
        
        self.entry_reg_user = ctk.CTkEntry(self.tab_register, placeholder_text="Username", width=250, height=40)
        self.entry_reg_user.pack(pady=10)
        
        self.entry_reg_email = ctk.CTkEntry(self.tab_register, placeholder_text="Email", width=250, height=40)
        self.entry_reg_email.pack(pady=10)
        
        self.entry_reg_pass = ctk.CTkEntry(self.tab_register, placeholder_text="Password", show="*", width=250, height=40)
        self.entry_reg_pass.pack(pady=10)
        
        self.lbl_reg_msg = ctk.CTkLabel(self.tab_register, text="", text_color="red")
        self.lbl_reg_msg.pack(pady=5)
        
        self.btn_register = ctk.CTkButton(self.tab_register, text="Đăng Ký", font=("Arial", 15, "bold"), width=250, height=45, fg_color="#27AE60", hover_color="#1E8449", command=self.handle_register)
        self.btn_register.pack(pady=10)

    def handle_login(self):
        username = self.entry_login_user.get().strip()
        password = self.entry_login_pass.get().strip()
        
        if not username or not password:
            self.lbl_login_msg.configure(text="Vui lòng nhập đầy đủ thông tin!", text_color="red")
            return
            
        self.btn_login.configure(state="disabled", text="Đang xử lý...")
        self.lbl_login_msg.configure(text="")
        
        def process_login():
            success, msg, session_token = db.login_user(username, password)
            if success:
                self.lbl_login_msg.configure(text=msg, text_color="green")
                self.after(1000, lambda: self.launch_main_app(username, session_token))
            else:
                self.lbl_login_msg.configure(text=msg, text_color="red")
                self.btn_login.configure(state="normal", text="Đăng Nhập")
                
        threading.Thread(target=process_login, daemon=True).start()

    def handle_register(self):
        username = self.entry_reg_user.get().strip()
        email = self.entry_reg_email.get().strip()
        password = self.entry_reg_pass.get().strip()
        
        if not username or not email or not password:
            self.lbl_reg_msg.configure(text="Vui lòng nhập đầy đủ thông tin!", text_color="red")
            return
            
        self.btn_register.configure(state="disabled", text="Đang xử lý...")
        self.lbl_reg_msg.configure(text="")
        
        def process_register():
            success, msg = db.register_user(username, email, password)
            if success:
                self.lbl_reg_msg.configure(text=msg, text_color="green")
                self.btn_register.configure(state="normal", text="Đăng Ký")
                # Chuyển sang tab đăng nhập sau 2 giây
                self.after(2000, lambda: self.tabview.set("Đăng Nhập"))
            else:
                self.lbl_reg_msg.configure(text=msg, text_color="red")
                self.btn_register.configure(state="normal", text="Đăng Ký")
                
        threading.Thread(target=process_register, daemon=True).start()

    def launch_main_app(self, username, session_token):
        self.destroy() # Đóng cửa sổ đăng nhập
        app = ToolApp(username, session_token)
        app.mainloop()

    def open_forgot_password_popup(self, event=None):
        popup = ctk.CTkToplevel(self)
        popup.title("Khôi Phục Mật Khẩu")
        popup.geometry("350x400")
        popup.grab_set()
        popup.attributes("-topmost", True)
        
        ctk.CTkLabel(popup, text="Email đã đăng ký:").pack(pady=(20, 5))
        entry_email = ctk.CTkEntry(popup, width=250)
        entry_email.pack(pady=5)
        
        lbl_msg = ctk.CTkLabel(popup, text="", text_color="red")
        lbl_msg.pack(pady=5)
        
        # Frame OTP (ẩn lúc đầu)
        frame_otp = ctk.CTkFrame(popup, fg_color="transparent")
        
        ctk.CTkLabel(frame_otp, text="Mã OTP (gửi về email):").pack(pady=5)
        entry_otp = ctk.CTkEntry(frame_otp, width=250)
        entry_otp.pack(pady=5)
        
        ctk.CTkLabel(frame_otp, text="Mật khẩu mới:").pack(pady=5)
        entry_new_pass = ctk.CTkEntry(frame_otp, show="*", width=250)
        entry_new_pass.pack(pady=5)
        
        def send_otp():
            email = entry_email.get().strip()
            if not email:
                lbl_msg.configure(text="Vui lòng nhập email!", text_color="red")
                return
            
            btn_send_otp.configure(state="disabled", text="Đang gửi...")
            
            def process():
                success, msg = db.generate_and_send_otp(email)
                if success:
                    lbl_msg.configure(text=msg, text_color="green")
                    btn_send_otp.pack_forget()
                    frame_otp.pack(pady=10)
                    btn_reset.pack(pady=10)
                else:
                    lbl_msg.configure(text=msg, text_color="red")
                    btn_send_otp.configure(state="normal", text="Nhận mã OTP")
            
            threading.Thread(target=process, daemon=True).start()
            
        def reset_password():
            email = entry_email.get().strip()
            otp = entry_otp.get().strip()
            new_pass = entry_new_pass.get().strip()
            
            if not otp or not new_pass:
                lbl_msg.configure(text="Nhập đầy đủ OTP và MK mới!", text_color="red")
                return
                
            btn_reset.configure(state="disabled", text="Đang xử lý...")
            
            def process():
                success, msg = db.verify_otp_and_reset_password(email, otp, new_pass)
                if success:
                    lbl_msg.configure(text=msg, text_color="green")
                    popup.after(2000, popup.destroy)
                else:
                    lbl_msg.configure(text=msg, text_color="red")
                    btn_reset.configure(state="normal", text="Khôi Phục")
                    
            threading.Thread(target=process, daemon=True).start()
            
        btn_send_otp = ctk.CTkButton(popup, text="Nhận mã OTP", command=send_otp)
        btn_send_otp.pack(pady=10)
        
        btn_reset = ctk.CTkButton(popup, text="Khôi Phục Mật Khẩu", fg_color="green", hover_color="darkgreen", command=reset_password)
        # Nút reset sẽ được pack sau khi OTP gửi thành công

if __name__ == "__main__":
    app = AuthApp()
    app.mainloop()
