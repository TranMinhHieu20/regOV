import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from playwright.async_api import async_playwright
from CLIENT_TOOL import utils
from CLIENT_TOOL import flows
from SERVER_API import db

# TỪ ĐIỂN TÊN MIỀN
DOMAIN_MAP = {
    "hi": "https://hi1444.com/Register",
    "qq": "https://www.qq8894.com/register",
    "new": "https://new8826.xyz/Register",
    "f168": "https://f1686s.com/home/register",
    "c168": "https://c168a.vip/home/register",
    "sc88": "https://m.sc8888.com/home/register"
}

# DỮ LIỆU ĐẦU VÀO
MY_DATA = {
    "username": "hiesCute029",
    "password": "password123",
    "pin_bank": "112233",
    "sdt": "0987654029",
    "ten_that": "Tran Van Vien",
    "stk_bank": "809182311010",
    "ten_bank": "MB BANK"
}

# CÁC TRANG MUỐN CHẠY
cac_web_muon_chay = ["qq"] 

async def start():
    config_cloud = db.lay_cau_hinh_tu_cloud()
    if not config_cloud:
        return print("❌ Không lấy được cấu hình. Hãy chạy python upload_db.py trước!")
    
    port = utils.find_hidemium_debug_port()
    if not port: 
        return print("❌ Không tìm thấy Hidemium. Vui lòng mở 1 Profile Hidemium lên trước!")
    
    ws_url = utils.get_websocket_url(port)
    
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]

        tasks = []
        for ten_tat in cac_web_muon_chay:
            full_url = DOMAIN_MAP.get(ten_tat.lower())
           
            if not full_url: continue
                
            domain_name = full_url.split("//")[-1].split("/")[0]
            cfg = config_cloud.get(domain_name, config_cloud.get("default"))
            
            page = await context.new_page()
            tasks.append(flows.run_full_flow(page, full_url, MY_DATA, cfg))
        
        await asyncio.gather(*tasks)
        print("\n🏆 ĐÃ CHẠY XONG TẤT CẢ LUỒNG!")



async def start_mobile_flow():
    async with async_playwright() as p:
        # Lấy thông số giả lập của iPhone 13
        device_config = p.devices['iPhone 13']
        
        # Mở trình duyệt
        browser = await p.chromium.launch(headless=False)
        
        # Tạo ngữ cảnh mới với cấu hình điện thoại (vừa có UA, vừa có kích thước màn hình dọc)
        context = await browser.new_context(**device_config)
        
        page = await context.new_page()
        
        # Đi tới trang web - lúc này web sẽ hiện giao diện mobile như hình trên
        await page.goto("https://c168a.vip/home/register")

     
        await page.pause()
        # Bắt đầu thực hiện các actions tiếp theo...

if __name__ == "__main__":
    input("👉 Hãy mở 1 Profile Hidemium lên, sau đó nhấn Enter ở đây để Tool chạy...")
    asyncio.run(start_mobile_flow())
    # asyncio.run(start())