import os
from dotenv import load_dotenv
from pymongo import MongoClient

env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)
URI = os.getenv("MONGO_URI")

def lay_cau_hinh_tu_cloud():
    if not URI:
        print("❌ Lỗi: Không tìm thấy MONGO_URI trong file .env")
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