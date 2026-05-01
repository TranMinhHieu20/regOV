import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from playwright.async_api import async_playwright
# from CLIENT_TOOL import utils
from CLIENT_TOOL import flows
from SERVER_API import db

# TỪ ĐIỂN TÊN MIỀN
DOMAIN_MAP = {
    "hi": "https://hi1444.com/Register",
    "qq": "https://www.qq8894.com/register",
    "new": "https://m.new8826.xyz/Account/Register",
    "f168": "https://f1686s.com/home/register",
    "c168": "https://c168a.vip/home/register",
    "sc88": "https://m.sc8888.com/home/register",
    "f8": "https://m.f8betf.cool/Account/Register",
}

# DỮ LIỆU ĐẦU VÀO
MY_DATA = {
    "username": "hiesCute074",
    "password": "password123",
    "pin_bank": "112233",
    "sdt": "0987654084",
    "ten_that": "Tran Thanh Cong",
    "stk_bank": "8091823110357",
    "ten_bank": "MB BANK"
}

# CÁC TRANG MUỐN CHẠY
cac_web_muon_chay = [ "f8"] 

async def start():
    config_cloud = db.lay_cau_hinh_tu_cloud()
    if not config_cloud:
        return print("❌ Không lấy được cấu hình. Hãy chạy python upload_db.py trước!")
    
    async with async_playwright() as p:
        
        # =================================================================
        # 1. CẤU HÌNH GIẢ LẬP IPHONE 13 ĐỂ TEST LOCAL (ĐANG BẬT)
        # =================================================================
        print("📱 Đang khởi tạo giả lập iPhone 13...")
        device_config = p.devices['iPhone 13']
        device_config['has_touch'] = True  # Thêm vào Dict trước
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            **device_config
            )

        # =================================================================
        # 2. CẤU HÌNH KẾT NỐI HIDEMIUM CHO PRODUCTION (ĐANG TẠM TẮT ĐỂ TEST)
        # (Khi nào test IP13 mượt rồi, hãy xóa '#' ở đoạn dưới và bôi '#' vào đoạn 1)
        # =================================================================
        # port = utils.find_hidemium_debug_port()
        # if not port: 
        #     return print("❌ Không tìm thấy Hidemium. Vui lòng mở 1 Profile Hidemium lên trước!")
        # ws_url = utils.get_websocket_url(port)
        # browser = await p.chromium.connect_over_cdp(ws_url)
        # context = browser.contexts[0]
        # =================================================================

        tasks = []
        for ten_tat in cac_web_muon_chay:
            full_url = DOMAIN_MAP.get(ten_tat.lower())
            
            if not full_url: continue
                
            domain_name = full_url.split("//")[-1].split("/")[0]
            cfg = config_cloud.get(domain_name, config_cloud.get("default"))
            
            page = await context.new_page()
            
            # Gắn luồng chạy tự động vào giao diện điện thoại vừa tạo
            tasks.append(flows.run_full_flow(page, full_url, MY_DATA, cfg))
        
        await asyncio.gather(*tasks)
        print("\n🏆 ĐÃ CHẠY XONG TẤT CẢ LUỒNG!")
        
        # Lệnh pause này giúp trình duyệt không bị tắt bụp đi ngay lập tức
        # Để bạn có thời gian nhấn F12 soi Selector mới
        print("🛑 Bot đang tạm dừng để bạn soi F12. Nhấn Resume trên thanh công cụ Playwright để kết thúc...")
        await page.pause()

if __name__ == "__main__":
    print("🚀 Bắt đầu chạy tool giả lập iPhone 13...")
    asyncio.run(start())