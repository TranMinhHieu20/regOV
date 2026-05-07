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
            ten_ngan_hang = str(user_data['ten_bank'])
            print(f" -> Đang mở danh sách ngân hàng để tìm: {ten_ngan_hang}...")
            selector_mo = cfg.get("input_tim_ngan_hang")
            
            # Ép click bằng JavaScript (Xuyên qua mọi rào cản readonly)
            await page.locator(selector_mo).first.evaluate("node => node.click()")
            await asyncio.sleep(1.5) # Đợi danh sách hiện
            
            # 1. Tách danh sách ngân hàng và tạo biến thể
            danh_sach_aliases = [nh.strip() for nh in ten_ngan_hang.split(',') if nh.strip()]
            cac_bien_the_go = []
            ten_chuan_de_so = []
            for nh in danh_sach_aliases:
                cac_bien_the_go.append(nh)
                cac_bien_the_go.append(nh.replace(" ", ""))
                if "MB" in nh.upper():
                    cac_bien_the_go.extend(["MB BANK", "MB"])
                ten_chuan_de_so.append(nh.upper().replace(" ", ""))
            
            cac_bien_the_go = list(dict.fromkeys(cac_bien_the_go))
            ten_chuan_de_so = list(dict.fromkeys(ten_chuan_de_so))

            item_ngan_hang = None
            item_selector = cfg.get("item_ngan_hang")

            # 2. Thử gõ từng từ khóa vào ô tìm kiếm
            if cfg.get("input_ten_ngan_hang"):
                search_box = page.locator(cfg.get("input_ten_ngan_hang")).first
                await search_box.wait_for(state="visible", timeout=5000)
                
                for tu_khoa in cac_bien_the_go:
                    print(f"    - Thử tìm: '{tu_khoa}'")
                    await search_box.fill("") # Xóa cũ
                    await search_box.type(tu_khoa, delay=50)
                    await asyncio.sleep(1.2)
                    
                    # Lấy danh sách kết quả hiển thị
                    options = page.locator(item_selector).filter(visible=True)
                    count = await options.count()
                    for i in range(count):
                        opt = options.nth(i)
                        text_raw = (await opt.inner_text()).upper()
                        text_chuan = text_raw.replace(" ", "")
                        
                        import re
                        words_web = re.findall(r'\w+', text_raw)
                        
                        found = False
                        for t in ten_chuan_de_so:
                            # So khớp chính xác hoặc khớp ở đầu mỗi từ
                            if t == text_chuan or any(t == w or w.startswith(t) for w in words_web):
                                found = True; break
                        
                        if found:
                            item_ngan_hang = opt
                            break
                    if item_ngan_hang: break
            else:
                # Nếu không có ô search, tìm trực tiếp trong danh sách
                options = page.locator(item_selector)
                count = await options.count()
                for i in range(count):
                    opt = options.nth(i)
                    text_raw = (await opt.inner_text()).upper()
                    text_chuan = text_raw.replace(" ", "")
                    
                    import re
                    words_web = re.findall(r'\w+', text_raw)
                    
                    found = False
                    for t in ten_chuan_de_so:
                        if t == text_chuan or any(t == w or w.startswith(t) for w in words_web):
                            found = True; break
                    
                    if found:
                        item_ngan_hang = opt
                        break

            # 3. Chốt hạ việc chọn Item
            if item_ngan_hang:
                # Dùng smart_click để đảm bảo bấm chính xác vào ngân hàng đã chọn
                print(f"    🎯 Đã thấy ngân hàng, đang bấm chọn: {await item_ngan_hang.inner_text()}")
                await smart_click(item_ngan_hang)
                await asyncio.sleep(1.0)
            else:
                print(f"    ❌ Không tìm thấy ngân hàng nào khớp với '{ten_ngan_hang}'")

        # 5. Bấm OK/Lưu
        nut_luu = cfg.get("nut_luu_ngan_hang")
        if nut_luu:
            print(" 🚀 Bấm nút OK để hoàn tất...")
            # Sử dụng smart_click và đảm bảo nút đã hiện trong vùng nhìn thấy
            target_ok = page.locator(nut_luu).first
            await target_ok.scroll_into_view_if_needed()
            await smart_click(target_ok)
            await asyncio.sleep(3)

        return True
    except Exception as e:
        print(f"❌ [Special Flow Bank] Lỗi: {e}")
        return False

async def flow_full_qq88(page, cfg, user_data):
    try:
        print("\n🎯 [QQ88 Flow] Bắt đầu luồng thiết lập ngân hàng QQ88...")

        # 0. BƯỚC DỌN ĐƯỜNG: Tắt nút X che màn hình
        nut_x_selector = cfg.get("nut_X")
        if nut_x_selector:
            print(" -> Thực hiện dọn dẹp phần tử che khuất...")
            # Truyền nut_x_selector vào hàm evaluate như một đối số để tránh lỗi cú pháp
            await page.evaluate("""(selector) => {
                const el = document.querySelector(selector);
                if (el) {
                    const wrapper = el.closest('.entry-count-wrapper') || el;
                    wrapper.remove();
                    return "Deleted";
                }
                return "Not found";
            }""", nut_x_selector)
            await asyncio.sleep(1)

        # 1. Bấm nút cài đặt (Rút tiền/Thêm thẻ)
        nut_cai_dat_selector = cfg.get("nut_cai_dat_1")
        if nut_cai_dat_selector:
            print(f" -> Đang bấm nút cài đặt: {nut_cai_dat_selector}")
            # Dùng evaluate để chắc chắn bấm xuyên qua mọi lớp mờ còn sót lại
            await smart_click(page.locator(nut_cai_dat_selector).first)
            await asyncio.sleep(2)

        # 2. Bấm vào ô chọn ngân hàng (.inputSelect)
        input_select_selector = cfg.get("input_tim_ngan_hang")
        if input_select_selector:
            print(" -> Mở danh sách chọn ngân hàng...")
            # Tiếp tục dùng JS Click cho chắc chắn
            await smart_click(page.locator(input_select_selector).first)
            await asyncio.sleep(1.5)

        # 3. Tìm kiếm và chọn ngân hàng (Logic linh hoạt 3 kiểu: MBB, MB BANK...)
        # ... (Giữ nguyên đoạn tìm kiếm linh hoạt mình đã viết ở trên) ...
        ten_tu_gui = user_data.get('ten_bank', '')
        danh_sach_ten = [t.strip() for t in ten_tu_gui.split(',')] if ',' in ten_tu_gui else [ten_tu_gui, "MBB", "MB BANK"]
        
        search_input = page.locator(cfg.get("input_ten_ngan_hang")).first
        item_selector = cfg.get("item_ngan_hang")
        
        da_chon_bank = False
        for ten in danh_sach_ten:
            if da_chon_bank: break
            print(f" 🔍 Thử tìm kiếm: {ten}")
            await search_input.fill("")
            await search_input.type(ten, delay=50)
            await asyncio.sleep(1.2)
            
            # Tìm item khớp
            items = page.locator(item_selector).filter(has_text=ten)
            if await items.count() > 0:
                print(f" ✅ Khớp {ten}, chọn luôn!")
                await items.first.evaluate("node => node.click()")
                da_chon_bank = True
                await asyncio.sleep(1)
        
        # 4. Sau khi chọn Bank xong, nhập STK và Chi nhánh
        # Lưu ý: Nên dùng fill() cho các ô input text bình thường
        if cfg.get("input_stk"):
            await page.locator(cfg.get("input_stk")).first.fill(str(user_data['stk_bank']))
            
        if cfg.get("chi_nhanh"):
            await page.locator(cfg.get("chi_nhanh")).first.fill(user_data.get('branch', 'Hà Nội'))

        # 5. Nhập Mã PIN rút tiền (2 ô)
        if cfg.get("pass_1") and cfg.get("pass_2"):
            # Ưu tiên lấy 'pin_rut_tien', nếu không có thì lấy 'pin' từ file dữ liệu của bạn
            # Bạn hãy đảm bảo trong file Excel/JSON đầu vào có cột 'pin' hoặc 'pin_rut_tien'
            ma_pin = user_data.get('pin_rut_tien') or user_data.get('pin') or "123456"
            
            print(f" -> Đang nhập mã PIN rút tiền: {ma_pin}")
            
            # Ô nhập 1
            input_1 = page.locator(cfg.get("pass_1")).first
            await input_1.fill("") # Xóa trống trước khi nhập
            await input_1.type(str(ma_pin), delay=100) # Gõ từng số để web nhận diện
            await asyncio.sleep(0.5)
            
            # Ô nhập 2
            input_2 = page.locator(cfg.get("pass_2")).first
            await input_2.fill("")
            await input_2.type(str(ma_pin), delay=100)
            await asyncio.sleep(0.5)

        # --- BƯỚC 6: XÁC NHẬN LẦN 1 (Tại Form) ---
        nut_1 = cfg.get("nut_luu_ngan_hang")
        if nut_1:
            print(" 🚀 Bấm Xác nhận lần 1...")
            # Cuộn xuống để thấy nút
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            btn1 = page.locator(nut_1).first
            # Ép click bằng JS để đảm bảo nó kích hoạt popup tiếp theo
            await btn1.evaluate("node => node.click()")
            await asyncio.sleep(1.5) # Đợi Popup/Thẻ <a> hiện lên

        # --- BƯỚC 7: XÁC NHẬN LẦN 2 (Thẻ <a> mới hiện lên) ---
        nut_2 = cfg.get("nut_xac_nhan_cuoi")
        if nut_2:
            print(f" 🔍 Đang tìm thẻ xác nhận cuối cùng: {nut_2}")
            btn2 = page.locator(nut_2).first
            
            try:
                # Đợi thẻ <a> này xuất hiện (vì nó hiện sau khi bấm nút 1)
                await btn2.wait_for(state="visible", timeout=5000)
                
                # Nếu là thẻ <a> dạng Popup, thường nó nằm giữa màn hình
                # Không cần cuộn, bấm thẳng bằng JS
                await btn2.evaluate("node => node.click()")
                print(" ✅ Đã bấm xác nhận thẻ <a> thành công!")
            except Exception as e:
                print(f" ⚠️ Không thấy thẻ <a> hiện lên hoặc lỗi: {e}")
                # Dự phòng: Thử nhấn phím Enter nếu nó là một Dialog của trình duyệt
                await page.keyboard.press("Enter")

        await asyncio.sleep(3) # Chờ kết quả cuối cùng
        return True
    except Exception as e:
        print(f"❌ [QQ88 Flow] Lỗi: {e}")
        return False

# 3. Tìm kiếm và chọn ngân hàng (Logic linh hoạt: MBB, MB BANK...)
async def flow_nhap_bank_jun1(page, cfg, user_data):
    try:
        print("\n🏦 [Special Flow] Bắt đầu quy trình liên kết Ngân hàng junv1...")

        # --- BƯỚC 1: DI CHUYỂN TỪ MENU VÀO FORM ---
        
        # 1.1 Cuộn xuống cuối trang để thấy menu Tài khoản
        print(" 📜 Cuộn xuống cuối trang...")
        await page.evaluate("window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })")
        await asyncio.sleep(1.5)

       # 1.2 Bấm nút "Tài khoản ngân hàng"
        btn_tai_khoan = cfg.get("nut_tai_khoan_nh")
        if btn_tai_khoan:
            print(f" -> Đang tìm và bấm vào: {btn_tai_khoan}")
            try:
                # Thử đợi tối đa 5 giây thay vì 3 giây mặc định của smart_click
                target = page.locator(btn_tai_khoan).first
                await target.wait_for(state="visible", timeout=5000) 
                
                # Cuộn thẳng đến phần tử đó để đảm bảo nó nằm trong tầm nhìn
                await target.scroll_into_view_if_needed()
                await asyncio.sleep(0.5)
                
                # Dùng evaluate click nếu click thông thường bị chặn
                await target.evaluate("node => node.click()")
                print(" ✅ Đã bấm nút Tài khoản ngân hàng")
                await asyncio.sleep(1.5)
            except Exception as e:
                print(f" ❌ Không thấy nút {btn_tai_khoan}, thử tìm theo text...")
                # Phương án dự phòng: Tìm theo nội dung chữ trên nút
                try:
                    await page.get_by_text("Tài khoản ngân hàng").first.click(timeout=3000)
                except:
                    print(f" 🚨 Lỗi nặng: {e}")
                    return False
        # 1.3 Bấm "Thẻ ngân hàng"
        btn_the_nh = cfg.get("them_the_nh")
        if btn_the_nh:
            print(f" -> Chọn: {btn_the_nh}")
            await smart_click(page.locator(btn_the_nh).first)
            await asyncio.sleep(1)

        # 1.4 Bấm nút "Thêm ngân hàng" (+)
        btn_them = cfg.get("them_nh")
        if btn_them:
            print(" ➕ Bấm nút Thêm thẻ ngân hàng...")
            await smart_click(page.locator(btn_them).first)
            await asyncio.sleep(2)

        # --- BƯỚC 2: ĐIỀN FORM THÔNG TIN ---

        # # Đợi form xuất hiện (Dọn rác nếu bị kẹt)
        # stk_selector = cfg.get("input_stk")
        # try:
        #     await page.locator(stk_selector).first.wait_for(state="visible", timeout=10000)
        # except:
        #     print(" ⚠️ Form chưa hiện, đang dọn dẹp Overlay...")
        #     await page.evaluate("() => { document.querySelectorAll('.van-overlay, .van-popup, .am-modal-mask').forEach(el => el.remove()); }")
        #     await asyncio.sleep(1)

        # # 2.1 Nhập Số tài khoản
        # if stk_selector:
        #     stk = str(user_data['stk_bank'])
        #     print(f" -> Nhập STK: {stk}")
        #     await page.locator(stk_selector).first.fill(stk)

        # # 2.2 Chọn Ngân hàng (Mở danh sách và Tìm kiếm)
        # if cfg.get("input_tim_ngan_hang"):
        #     ten_ngan_hang = str(user_data['ten_bank'])
        #     print(f" -> Đang tìm ngân hàng: {ten_ngan_hang}...")
            
        #     # Mở danh sách chọn
        #     await smart_click(page.locator(cfg.get("input_tim_ngan_hang")).first)
        #     await asyncio.sleep(1.5)
            
        #     # Xử lý biến thể tên ngân hàng
        #     danh_sach_aliases = [nh.strip() for nh in ten_ngan_hang.split(',') if nh.strip()]
        #     cac_bien_the_go = []
        #     ten_chuan_de_so = []
        #     for nh in danh_sach_aliases:
        #         cac_bien_the_go.append(nh)
        #         cac_bien_the_go.append(nh.replace(" ", ""))
        #         if "MB" in nh.upper(): cac_bien_the_go.extend(["MB BANK", "MB"])
        #         ten_chuan_de_so.append(nh.upper().replace(" ", ""))
            
        #     cac_bien_the_go = list(dict.fromkeys(cac_bien_the_go))
        #     ten_chuan_de_so = list(dict.fromkeys(ten_chuan_de_so))

        #     item_ngan_hang = None
        #     item_selector = cfg.get("item_ngan_hang")

        #     # Thử gõ tìm kiếm
        #     search_box_selector = cfg.get("input_ten_ngan_hang")
        #     if search_box_selector:
        #         search_box = page.locator(search_box_selector).first
        #         for tu_khoa in cac_bien_the_go:
        #             print(f"    - Thử gõ: '{tu_khoa}'")
        #             await search_box.fill("")
        #             await search_box.type(tu_khoa, delay=50)
        #             await asyncio.sleep(1.2)
                    
        #             options = page.locator(item_selector).filter(visible=True)
        #             count = await options.count()
        #             for i in range(count):
        #                 opt = options.nth(i)
        #                 text_raw = (await opt.inner_text()).upper()
        #                 text_chuan = text_raw.replace(" ", "")
        #                 if any(t == text_chuan or t in text_chuan for t in ten_chuan_de_so):
        #                     item_ngan_hang = opt; break
        #             if item_ngan_hang: break
            
        #     # Bấm chọn ngân hàng đã tìm thấy
        #     if item_ngan_hang:
        #         print(f"    🎯 Đã chọn: {await item_ngan_hang.inner_text()}")
        #         await item_ngan_hang.click()
        #         await asyncio.sleep(1)
        #     else:
        #         print(f"    ❌ Không tìm thấy ngân hàng khớp với {ten_ngan_hang}")

        # # 2.3 Nhập mật khẩu xác nhận (Nếu có)
        # if cfg.get("nhap_lai_pass"):
        #     print(f" -> Xác nhận mật khẩu...")
        #     await page.locator(cfg.get("nhap_lai_pass")).first.fill(str(user_data['password']))

        # # --- BƯỚC 3: LƯU THÔNG TIN ---
        # nut_luu = cfg.get("nut_luu_ngan_hang")
        # if nut_luu:
        #     print(" 🚀 Bấm OK để hoàn tất...")
        #     btn_ok = page.locator(nut_luu).first
        #     await btn_ok.scroll_into_view_if_needed()
        #     # Dùng evaluate click để tránh bị các thông báo Popup che khuất
        #     await smart_click(btn_ok)
        #     print(" ✅ Đã gửi lệnh lưu!")
        #     await asyncio.sleep(5)

        # return True
        
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
            ten_ngan_hang = str(user_data['ten_bank'])
            print(f" -> Đang mở danh sách ngân hàng để tìm: {ten_ngan_hang}...")
            selector_mo = cfg.get("input_tim_ngan_hang")
            
            # Ép click bằng JavaScript (Xuyên qua mọi rào cản readonly)
            await page.locator(selector_mo).first.evaluate("node => node.click()")
            await asyncio.sleep(1.5) # Đợi danh sách hiện
            
            # 1. Tách danh sách ngân hàng và tạo biến thể
            danh_sach_aliases = [nh.strip() for nh in ten_ngan_hang.split(',') if nh.strip()]
            cac_bien_the_go = []
            ten_chuan_de_so = []
            for nh in danh_sach_aliases:
                cac_bien_the_go.append(nh)
                cac_bien_the_go.append(nh.replace(" ", ""))
                if "MB" in nh.upper():
                    cac_bien_the_go.extend(["MB BANK", "MB"])
                ten_chuan_de_so.append(nh.upper().replace(" ", ""))
            
            cac_bien_the_go = list(dict.fromkeys(cac_bien_the_go))
            ten_chuan_de_so = list(dict.fromkeys(ten_chuan_de_so))

            item_ngan_hang = None
            item_selector = cfg.get("item_ngan_hang")

            # 2. Thử gõ từng từ khóa vào ô tìm kiếm
            if cfg.get("input_ten_ngan_hang"):
                search_box = page.locator(cfg.get("input_ten_ngan_hang")).first
                await search_box.wait_for(state="visible", timeout=5000)
                
                for tu_khoa in cac_bien_the_go:
                    print(f"    - Thử tìm: '{tu_khoa}'")
                    await search_box.fill("") # Xóa cũ
                    await search_box.type(tu_khoa, delay=50)
                    await asyncio.sleep(1.2)
                    
                    # Lấy danh sách kết quả hiển thị
                    options = page.locator(item_selector).filter(visible=True)
                    count = await options.count()
                    for i in range(count):
                        opt = options.nth(i)
                        text_raw = (await opt.inner_text()).upper()
                        text_chuan = text_raw.replace(" ", "")
                        
                        import re
                        words_web = re.findall(r'\w+', text_raw)
                        
                        found = False
                        for t in ten_chuan_de_so:
                            # So khớp chính xác hoặc khớp ở đầu mỗi từ
                            if t == text_chuan or any(t == w or w.startswith(t) for w in words_web):
                                found = True; break
                        
                        if found:
                            item_ngan_hang = opt
                            break
                    if item_ngan_hang: break
            else:
                # Nếu không có ô search, tìm trực tiếp trong danh sách
                options = page.locator(item_selector)
                count = await options.count()
                for i in range(count):
                    opt = options.nth(i)
                    text_raw = (await opt.inner_text()).upper()
                    text_chuan = text_raw.replace(" ", "")
                    
                    import re
                    words_web = re.findall(r'\w+', text_raw)
                    
                    found = False
                    for t in ten_chuan_de_so:
                        if t == text_chuan or any(t == w or w.startswith(t) for w in words_web):
                            found = True; break
                    
                    if found:
                        item_ngan_hang = opt
                        break

            # 3. Chốt hạ việc chọn Item
            if item_ngan_hang:
                # Dùng smart_click để đảm bảo bấm chính xác vào ngân hàng đã chọn
                print(f"    🎯 Đã thấy ngân hàng, đang bấm chọn: {await item_ngan_hang.inner_text()}")
                await smart_click(item_ngan_hang)
                await asyncio.sleep(1.0)
            else:
                print(f"    ❌ Không tìm thấy ngân hàng nào khớp với '{ten_ngan_hang}'")

        # 5. Bấm OK/Lưu
        nut_luu = cfg.get("nut_luu_ngan_hang")
        if nut_luu:
            print(" 🚀 Bấm nút OK để hoàn tất...")
            # Sử dụng smart_click và đảm bảo nút đã hiện trong vùng nhìn thấy
            target_ok = page.locator(nut_luu).first
            await target_ok.scroll_into_view_if_needed()
            await smart_click(target_ok)
            await asyncio.sleep(3)

        return True
   
    except Exception as e:
        print(f"❌ [Special Flow 78win] Lỗi: {e}")
        return False

async def flow_nhap_bank_moi(page, cfg, user_data):
    try:
        print("\n🏦 [Special Flow] Bắt đầu quy trình thêm ngân hàng từ dữ liệu...")

        # 1. Bấm "Thêm vào Ứng dụng"
        if cfg.get("them_vao_ung_dung"):
            await smart_click(page.locator(cfg.get("them_vao_ung_dung")).first)
            await asyncio.sleep(1)

        # 2. Bấm "Rút tiền"
        if cfg.get("rut_tien"):
            await smart_click(page.locator(cfg.get("rut_tien")).first)
            await asyncio.sleep(1.5)

        # 3. Bấm "Nút Dropdown/Chọn ngân hàng"
        if cfg.get("input_tim_ngan_hang"):
            await smart_click(page.locator(cfg.get("input_tim_ngan_hang")).first)
            await asyncio.sleep(1)

        # 4. Bấm "Thêm thẻ ngân hàng"
        if cfg.get("them_the_ngan_hang"):
            await smart_click(page.locator(cfg.get("them_the_ngan_hang")).first)
            await asyncio.sleep(1)

        # 5. Bấm "Nút Thêm TK ngân hàng"
        if cfg.get("them_tk_ngan_hang"):
            await smart_click(page.locator(cfg.get("them_tk_ngan_hang")).first)
            await asyncio.sleep(1.5)

        # --- ĐIỀN FORM ---

        # 6. Click vào ô chọn Ngân hàng
        if cfg.get("click_input"):
            await smart_click(page.locator(cfg.get("click_input")).first)
            await asyncio.sleep(1)

        # 7. Tìm kiếm ngân hàng
        if cfg.get("input_ten_ngan_hang"):
            ten_nh = str(user_data['ten_bank'])
            search_box = page.locator(cfg.get("input_ten_ngan_hang")).first
            await search_box.fill(ten_nh)
            await asyncio.sleep(1.5)

            item_selector = cfg.get("item_ngan_hang")
            try:
                # Tìm đúng thẻ li hoặc div chứa tên ngân hàng
                target = page.locator(item_selector).locator("li, div").filter(has_text=ten_nh).first
                await smart_click(target)
            except:
                await smart_click(page.locator(item_selector).first)

        # 8. Nhập Số tài khoản (Lấy từ data)
        if cfg.get("input_stk"):
            stk = str(user_data['stk_bank'])
            print(f" ✍️ Nhập STK: {stk}")
            await page.locator(cfg.get("input_stk")).first.fill(stk)

        # 9. NHẬP CHI NHÁNH (Lấy từ data người dùng nhập)
        if cfg.get("chi_nhanh"):
            # Lấy giá trị chi nhánh từ cột 'chi_nhanh' trong file Excel/Database của bạn
            # Nếu data không có chi nhánh, mặc định điền tên ngân hàng hoặc để trống
            chi_nhanh_data = str(user_data.get('chi_nhanh', 'Viet Nam'))
            print(f" ✍️ Nhập Chi nhánh: {chi_nhanh_data}")
            await page.locator(cfg.get("chi_nhanh")).first.fill(chi_nhanh_data)

        # 10. Bấm Xác nhận
        nut_luu = cfg.get("nut_luu_ngan_hang")
        if nut_luu:
            print(" 🚀 Bấm Xác nhận...")
            target_ok = page.locator(nut_luu).first
            await target_ok.scroll_into_view_if_needed()
            await smart_click(target_ok)
            await asyncio.sleep(3)

        return True

    except Exception as e:
        print(f"❌ [Special Flow] Lỗi: {e}")
        return False