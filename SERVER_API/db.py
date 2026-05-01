import os
import hashlib
import binascii
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pymongo import MongoClient

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from path_helper import get_data_path

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
vault = {}
env_path = get_data_path("SERVER_API", ".env")

if os.path.exists(env_path):
    # CHẾ ĐỘ DEVELOPER: Ưu tiên dùng file .env nếu có
    from dotenv import load_dotenv
    load_dotenv(env_path)
    vault = {
        "MONGO_URI": os.getenv("MONGO_URI"),
        "SMTP_HOST": os.getenv("SMTP_HOST", "smtp.gmail.com"),
        "SMTP_PORT": int(os.getenv("SMTP_PORT", 587)),
        "SMTP_USER": os.getenv("SMTP_USER"),
        "SMTP_PASS": os.getenv("SMTP_PASS")
    }
else:
    # CHẾ ĐỘ PRODUCTION: Dùng vault mã hóa trong code
    from secret_gate import get_vault
    vault = get_vault()

URI = vault.get("MONGO_URI")
SMTP_HOST = vault.get("SMTP_HOST")
SMTP_PORT = vault.get("SMTP_PORT")
SMTP_USER = vault.get("SMTP_USER")
SMTP_PASS = vault.get("SMTP_PASS")


def lay_cau_hinh_tu_cloud():
    if not URI:
        print("❌ Lỗi: Không tìm thấy cấu hình kết nối")
        return {}

    try:
        client = MongoClient(URI, serverSelectionTimeoutMS=5000)
        db = client["ToolAutoDB"]
        collection = db["Configs"]
        
        result = collection.find_one({"name": "main_web_config"})
        if result and "data" in result:
            return result["data"]
        return {}
    except Exception as e:
        print(f"❌ Lỗi kết nối DB: {e}")
        return {}

def hash_password(password: str, salt: bytes = None) -> tuple:
    if salt is None:
        salt = os.urandom(16)
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt, pwdhash

def register_user(username, email, password):
    if not URI:
        return False, "Không tìm thấy MONGO_URI"
    try:
        client = MongoClient(URI, serverSelectionTimeoutMS=5000)
        db = client["ToolAutoDB"]
        users_col = db["Users"]
        
        if users_col.find_one({"username": username}):
            return False, "Username đã tồn tại!"
            
        salt, pwdhash = hash_password(password)
        
        user_data = {
            "username": username,
            "email": email,
            "password_salt": binascii.hexlify(salt).decode('ascii'),
            "password_hash": binascii.hexlify(pwdhash).decode('ascii'),
            "session_token": "",
            "status": "active" # Có thể đổi thành 'pending' nếu cần duyệt
        }
        
        users_col.insert_one(user_data)
        return True, "Đăng ký thành công!"
    except Exception as e:
        return False, f"Lỗi DB: {str(e)}"

def login_user(username, password):
    if not URI:
        return False, "Không tìm thấy MONGO_URI", None
    try:
        client = MongoClient(URI, serverSelectionTimeoutMS=5000)
        db = client["ToolAutoDB"]
        users_col = db["Users"]
        
        user = users_col.find_one({"$or": [{"username": username}, {"email": username}]})
        if not user:
            return False, "Sai tài khoản hoặc mật khẩu!", None
            
        if user.get("status") != "active":
            return False, "Tài khoản đang bị khóa hoặc chưa kích hoạt!", None
            
        # Kiểm tra mật khẩu
        salt = binascii.unhexlify(user["password_salt"].encode('ascii'))
        stored_hash = user["password_hash"]
        _, pwdhash = hash_password(password, salt)
        computed_hash = binascii.hexlify(pwdhash).decode('ascii')
        
        if computed_hash == stored_hash:
            # Tạo session token mới (đá văng phiên đăng nhập cũ ở máy khác)
            new_session_token = str(uuid.uuid4())
            users_col.update_one({"_id": user["_id"]}, {"$set": {"session_token": new_session_token}})
            
            return True, "Đăng nhập thành công!", new_session_token
        else:
            return False, "Sai tài khoản hoặc mật khẩu!", None
            
    except Exception as e:
        return False, f"Lỗi DB: {str(e)}", None

def check_session(username, session_token):
    if not URI:
        return False
    try:
        client = MongoClient(URI, serverSelectionTimeoutMS=3000)
        db = client["ToolAutoDB"]
        user = db["Users"].find_one({"username": username})
        if user and user.get("session_token") == session_token and user.get("status") == "active":
            return True
        return False
    except:
        return True # Tránh bị đá văng nếu rớt mạng tạm thời

def generate_and_send_otp(email):
    if not URI or not SMTP_USER:
        return False, "Thiếu cấu hình MongoDB hoặc SMTP"
    try:
        client = MongoClient(URI, serverSelectionTimeoutMS=5000)
        db = client["ToolAutoDB"]
        users_col = db["Users"]
        
        user = users_col.find_one({"email": email})
        if not user:
            return False, "Email không tồn tại trong hệ thống!"
            
        otp = str(random.randint(100000, 999999))
        expiry = datetime.utcnow() + timedelta(minutes=5)
        
        users_col.update_one({"_id": user["_id"]}, {"$set": {"reset_otp": otp, "otp_expiry": expiry}})
        
        # Gửi email
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = email
        msg['Subject'] = "Mã OTP Khôi Phục Mật Khẩu - AQUA REG TOOL"
        
        body = f"Mã OTP của bạn là: {otp}\nMã này sẽ hết hạn trong 5 phút.\nVui lòng không chia sẻ mã này cho bất kỳ ai."
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
        
        return True, "Mã OTP đã được gửi đến email của bạn!"
    except Exception as e:
        return False, f"Lỗi gửi OTP: {str(e)}"

def verify_otp_and_reset_password(email, otp, new_password):
    if not URI:
        return False, "Không tìm thấy MONGO_URI"
    try:
        client = MongoClient(URI, serverSelectionTimeoutMS=5000)
        db = client["ToolAutoDB"]
        users_col = db["Users"]
        
        user = users_col.find_one({"email": email, "reset_otp": otp})
        if not user:
            return False, "Mã OTP không hợp lệ!"
            
        if datetime.utcnow() > user.get("otp_expiry", datetime.min):
            return False, "Mã OTP đã hết hạn!"
            
        salt, pwdhash = hash_password(new_password)
        
        users_col.update_one({"_id": user["_id"]}, {
            "$set": {
                "password_salt": binascii.hexlify(salt).decode('ascii'),
                "password_hash": binascii.hexlify(pwdhash).decode('ascii')
            },
            "$unset": {"reset_otp": "", "otp_expiry": ""}
        })
        
        return True, "Khôi phục mật khẩu thành công!"
    except Exception as e:
        return False, f"Lỗi DB: {str(e)}"

def change_password(username, old_password, new_password):
    if not URI:
        return False, "Không tìm thấy MONGO_URI"
    try:
        client = MongoClient(URI, serverSelectionTimeoutMS=5000)
        db = client["ToolAutoDB"]
        users_col = db["Users"]
        
        user = users_col.find_one({"username": username})
        if not user:
            return False, "Người dùng không tồn tại!"
            
        salt = binascii.unhexlify(user["password_salt"].encode('ascii'))
        stored_hash = user["password_hash"]
        _, pwdhash = hash_password(old_password, salt)
        computed_hash = binascii.hexlify(pwdhash).decode('ascii')
        
        if computed_hash != stored_hash:
            return False, "Mật khẩu cũ không chính xác!"
            
        new_salt, new_pwdhash = hash_password(new_password)
        
        users_col.update_one({"_id": user["_id"]}, {
            "$set": {
                "password_salt": binascii.hexlify(new_salt).decode('ascii'),
                "password_hash": binascii.hexlify(new_pwdhash).decode('ascii')
            }
        })
        return True, "Đổi mật khẩu thành công!"
    except Exception as e:
        return False, f"Lỗi DB: {str(e)}"