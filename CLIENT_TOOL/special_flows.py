import asyncio
from CLIENT_TOOL.actions import smart_click

async def flow_rut_tien_3_o_dac_biet(page, cfg, user_data):
    """
    Luồng xử lý đặc biệt cho trang web có 3 ô nhập mật khẩu.
    Trình tự: Bấm Rút tiền 1 -> Bấm Rút tiền 2 -> Điền 3 ô -> Cập nhật.
    """
    try:
        print("\n🚀 [Special Flow] Bắt đầu luồng cài đặt 3 ô đặc biệt...")

        # # 1. Bấm nút Rút tiền 1
        # nut_1 = cfg.get("nut_rut_tien_1")
        # if nut_1:
        #     print(f" -> Đang bấm Rút tiền 1: {nut_1}")
        #     await smart_click(page.locator(nut_1).first)
        #     await asyncio.sleep(2) # Chờ hiệu ứng chuyển cảnh

        # 2. Bấm nút Rút tiền 2
        nut_2 = cfg.get("nut_rut_tien_2")
        if nut_2:
            print(f" -> Đang bấm Rút tiền 2: {nut_2}")
            await smart_click(page.locator(nut_2).first)
            await asyncio.sleep(2)

        # 3. Điền 3 ô mật khẩu
        o_pin = cfg.get("o_nhap_pass_rut")          # #pin
        o_confirm = cfg.get("o_nhap_xac_nhan_pass_rut") # #confirmpin
        o_pass_reg = cfg.get("o_nhap_lai_pass")     # #password
        
        # Lấy dữ liệu
        pin_moi = str(user_data.get('pin_bank', '123456'))
        pass_web = str(user_data.get('password'))

        print(f" 📝 Đang điền form bảo mật (PIN: {pin_moi})...")
        
        if o_pin:
            await page.locator(o_pin).first.wait_for(state="visible", timeout=10000)
            await page.locator(o_pin).first.fill(pin_moi)
        
        if o_confirm:
            await page.locator(o_confirm).first.fill(pin_moi)
            
        if o_pass_reg:
            print(" 🔐 Nhập mật khẩu đăng ký vào ô thứ 3...")
            await page.locator(o_pass_reg).first.fill(pass_web)

        await asyncio.sleep(1)

        # 4. Bấm nút Cập nhật
        nut_cap_nhat = cfg.get("nut_xacnhan_pass_rut")
        if nut_cap_nhat:
            print(" 🚀 Bấm nút Cập nhật...")
            await smart_click(page.locator(nut_cap_nhat).first)
            await asyncio.sleep(3) # Đợi web phản hồi thành công

        print("✅ [Special Flow] Hoàn tất cài đặt mật khẩu rút tiền!")
        return True

    except Exception as e:
        print(f"❌ [Special Flow] Lỗi: {e}")
        return False

# async def flow_nhap_bank_78win(page, cfg, user_data):
#     try:
#         print("\n🏦 [Special Flow] Bắt đầu điền thông tin Ngân hàng 78win...")

#         # 1. Đóng Popup (nếu có nút Đóng riêng)
#         btn_dong = cfg.get("btn_dong")
#         if btn_dong:
#             try:
#                 print(f" -> Đang đóng popup: {btn_dong}")
#                 await page.locator(btn_dong).first.click(timeout=3000)
#                 await asyncio.sleep(1)
#             except:
#                 print(" -> Không thấy popup đóng, bỏ qua...")

#         # 2. Nhập Số tài khoản
#         if cfg.get("input_stk"):
#             print(f" -> Nhập STK: {user_data['stk_bank']}")
#             await page.locator(cfg.get("input_stk")).first.fill(str(user_data['stk_bank']))

#         # 3. Nhập lại mật khẩu Game (Ô password xác nhận)
#         if cfg.get("nhap_lai_pass"):
#             print(f" -> Xác nhận lại mật khẩu Game...")
#             await page.locator(cfg.get("nhap_lai_pass")).first.fill(str(user_data['password']))

#         # 4. Chọn Ngân hàng (Quy trình: Click mở -> Search -> Chọn)
#         if cfg.get("input_tim_ngan_hang"):
#             print(f" -> Đang chọn Ngân hàng: {user_data['ten_bank']}")
#             # Click vào ô chọn ngân hàng để hiện danh sách/ô search
#             await page.locator(cfg.get("input_tim_ngan_hang")).first.click()
#             await asyncio.sleep(1)
            
#             # Nếu có ô nhập tên để tìm kiếm
#             if cfg.get("input_ten_ngan_hang"):
#                 await page.locator(cfg.get("input_ten_ngan_hang")).first.fill(user_data['ten_bank'])
#                 await asyncio.sleep(1)
            
#             # Chọn item ngân hàng hiện ra
#             item_selector = cfg.get("item_ngan_hang")
#             # Tìm item có chứa tên ngân hàng của mình
#             target_item = page.locator(item_selector).filter(has_text=user_data['ten_bank']).first
#             await target_item.click()
#             await asyncio.sleep(1)

#         # 5. Bấm OK/Lưu
#         nut_luu = cfg.get("nut_luu_ngan_hang")
#         if nut_luu:
#             print(" 🚀 Bấm nút OK để hoàn tất...")
#             await page.locator(nut_luu).first.click()
#             await asyncio.sleep(3)

#         print("✅ [Special Flow] Đã hoàn thành thêm Ngân hàng cho 78win!")
#         return True
#     except Exception as e:
#         print(f"❌ [Special Flow Bank] Lỗi: {e}")
#         return False

async def flow_nhap_bank_78win(page, cfg, user_data):
    try:
        print("\n🏦 [Special Flow] Bắt đầu điền thông tin Ngân hàng 78win...")

        # --- BƯỚC QUAN TRỌNG: ĐỢI FORM HIỆN VÀ DỌN RÁC ---
        # Đợi tối đa 10s cho đến khi ô nhập STK xuất hiện (dấu hiệu form bank đã load)
        stk_selector = cfg.get("input_stk")
        try:
            await page.locator(stk_selector).first.wait_for(state="visible", timeout=10000)
        except:
            print(" ⚠️ Form Bank chưa hiện, đang thử dọn dẹp Popup che khuất...")
            # Xóa các lớp phủ mờ (overlay) của thông báo "Cài đặt thành công" nếu nó còn kẹt
            await page.evaluate("() => { document.querySelectorAll('.van-overlay, .van-popup').forEach(el => el.remove()); }")
            await asyncio.sleep(1)

        # 1. Đóng Popup (nếu có nút Đóng cụ thể)
        btn_dong = cfg.get("btn_dong")
        if btn_dong:
            try:
                await page.locator(btn_dong).first.click(timeout=2000)
                await asyncio.sleep(0.5)
            except: pass

        # 2. Nhập Số tài khoản
        if stk_selector:
            print(f" -> Nhập STK: {user_data['stk_bank']}")
            await page.locator(stk_selector).first.fill(str(user_data['stk_bank']))

        # 3. Nhập lại mật khẩu Game (Xác nhận)
        if cfg.get("nhap_lai_pass"):
            print(f" -> Xác nhận mật khẩu Game...")
            await page.locator(cfg.get("nhap_lai_pass")).first.fill(str(user_data['password']))

        # 4. Chọn Ngân hàng (Dùng JS để kích hoạt vì #bankid thường bị readonly)
        if cfg.get("input_tim_ngan_hang"):
            print(f" -> Đang mở danh sách ngân hàng...")
            selector_mo = cfg.get("input_tim_ngan_hang")
            
            # Ép click bằng JavaScript (Xuyên qua mọi rào cản readonly)
            await page.locator(selector_mo).first.evaluate("node => node.click()")
            await asyncio.sleep(1.5) # Đợi danh sách hiện
            
            # Nhập tên tìm kiếm
            if cfg.get("input_ten_ngan_hang"):
                search_box = page.locator(cfg.get("input_ten_ngan_hang")).first
                await search_box.wait_for(state="visible", timeout=5000)
                await search_box.fill(user_data['ten_bank'])
                await asyncio.sleep(1)
            
            # Chọn Item
            item_selector = cfg.get("item_ngan_hang")
            await page.locator(item_selector).filter(has_text=user_data['ten_bank']).last.click()
            await asyncio.sleep(0.5)

        # 5. Bấm OK/Lưu
        nut_luu = cfg.get("nut_luu_ngan_hang")
        if nut_luu:
            print(" 🚀 Bấm nút OK...")
            await page.locator(nut_luu).first.click()
            await asyncio.sleep(3)

        return True
    except Exception as e:
        print(f"❌ [Special Flow Bank] Lỗi: {e}")
        return False