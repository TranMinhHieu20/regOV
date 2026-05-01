# --- TRONG FILE: actions.py ---
import asyncio
import ddddocr
import random
import os

async def smart_click(locator, timeout=3000):
    """
    Hàm click linh hoạt cho Hidemium (Desktop + Mobile profile):
    Ưu tiên: click() → tap() → JS TouchEvent + click.
    """
    # Chiến lược 1: Click thường (tốt nhất cho Desktop profile)
    try:
        await locator.click(timeout=timeout)
        return
    except:
        pass
    # Chiến lược 2: Tap (tốt nhất cho Mobile profile)
    try:
        await locator.tap(timeout=timeout)
        return
    except:
        pass
    # Chiến lược 3: Ép bằng JS — fire đầy đủ chuỗi touch + click
    try:
        await locator.evaluate("""node => {
            node.dispatchEvent(new TouchEvent('touchstart', {bubbles: true}));
            node.dispatchEvent(new TouchEvent('touchend', {bubbles: true}));
            node.click();
        }""")
    except Exception as e:
        print(f"⚠️ Lỗi smart_click (hết chiến lược): {e}")


async def smart_tap(locator, timeout=3000):
    """
    Hàm tap linh hoạt cho Hidemium (ưu tiên Touch cho bàn phím ảo, ô nhập...):
    Ưu tiên: tap() → click() → JS TouchEvent + click.
    """
    # Chiến lược 1: Tap (ưu tiên cho mobile / bàn phím ảo)
    try:
        await locator.tap(timeout=timeout)
        return
    except:
        pass
    # Chiến lược 2: Click thường
    try:
        await locator.click(timeout=timeout)
        return
    except:
        pass
    # Chiến lược 3: Ép bằng JS
    try:
        await locator.evaluate("""node => {
            node.dispatchEvent(new TouchEvent('touchstart', {bubbles: true}));
            node.dispatchEvent(new TouchEvent('touchend', {bubbles: true}));
            node.click();
        }""")
    except Exception as e:
        print(f"⚠️ Lỗi smart_tap (hết chiến lược): {e}")

async def bam_nut_dang_ky(page, selector_dang_ky):
    """Hàm chuyên dụng để xử lý việc bấm nút đăng ký an toàn"""
    print(f"🖱️ Đang click Đăng Ký (Tìm bộ chọn đang hiển thị)...")
    await asyncio.sleep(1) # Nghỉ 1 nhịp để JS web nhận diện form
    
    try:
        selector_hien_thi = f"{selector_dang_ky}:visible"
        nut_dang_ky = page.locator(selector_hien_thi).last
        
        await nut_dang_ky.wait_for(state="visible", timeout=60000)
        await smart_click(nut_dang_ky)
        print("✔️ Đã bấm nút ĐĂNG KÝ thành công!")
        
        # CHỜ CHUYỂN CẢNH: Sau khi bấm đăng ký, web cần thời gian phản hồi
        await asyncio.sleep(2) 
        return True
    except Exception as e:
        print(f"❌ Kẹt nút Đăng ký. Chi tiết: {e}")
        return False


async def kiem_tra_va_cho_captcha(page):
    """
    Hàm phát hiện Captcha trượt: Kiên nhẫn đợi tối đa 8s để xem Captcha có mọc lên không.
    """
    print("🔍 Đang quan sát xem Captcha có mọc lên không (Kiên nhẫn đợi 60 giây)...")
    
    da_thay_captcha = False
    # Bắt một phần chữ để tránh lỗi font hoặc khoảng trắng ẩn của web
    dauhieu_captcha = page.get_by_text("Trượt để hoàn thành")
    
    try:
        # Ép Tool đứng im chờ cái chữ trên hiện ra (tối đa 60s)
        await dauhieu_captcha.wait_for(state="visible", timeout=60000)
        da_thay_captcha = True
    except:
        # Nếu sau 60s mà vẫn im lìm -> Chắc chắn không có Captcha
        da_thay_captcha = False

    if da_thay_captcha:
        print("\n" + "!"*50)
        print("🚨 THÔNG BÁO: PHÁT HIỆN CAPTCHA TRÊN TRANG NÀY!")
        print("👉 Vui lòng dùng tay kéo mảnh ghép để hoàn tất.")
        print("⏳ Tool đang đóng băng để đợi bạn giải xong...")
        print("!"*50 + "\n")

        try:
            # Tool đứng đợi cho đến khi dòng chữ biến mất (bạn đã giải xong)
            await dauhieu_captcha.wait_for(state="hidden", timeout=120000)
            print("✅ Đã giải xong Captcha! Đang tiếp tục quy trình...")
            
            # CHỜ CHUYỂN CẢNH: Nghỉ 3s để web load vào trang chủ sau khi qua cửa
            await asyncio.sleep(3) 
            return True
        except:
            print("❌ Đợi quá lâu (2 phút) mà chưa thấy giải Captcha. Bỏ qua luồng này.")
            return False
    else:
        print("✔️ May mắn! Trang này không yêu cầu giải Captcha.")
        return True


async def don_dep_popup(page, danh_sach_popup):
    """Hàm chuyên dụng để lôi danh sách cấu hình ra và chém mọi popup"""
    print("\n--- BẮT ĐẦU DỌN DẸP POPUP ---")
    
    if not danh_sach_popup:
        print("⚠️ Bỏ qua quét Popup vì chưa có cấu hình 'nut_dong_popup' trên Cloud.")
        return

    # Nếu trên Cloud lỡ cấu hình 1 chuỗi thay vì list, ta tự bọc nó vào list
    if isinstance(danh_sach_popup, str):
        danh_sach_popup = [danh_sach_popup]

    for selector in danh_sach_popup:
        for _ in range(6): # Quét 7 lần cho mỗi loại (phòng ngừa popup kép)
            try:
                nut_dong = page.locator(f"{selector}:visible").last
                await nut_dong.wait_for(state="visible", timeout=2000)
                await smart_click(nut_dong)
                print(f"✔️ BÙM! Đã đóng 1 Popup bằng vũ khí: {selector}")
                
                # CHỜ HIỆU ỨNG: Đợi 1.5s để hiệu ứng mờ của popup biến mất hẳn
                await asyncio.sleep(1) 
            except:
                break # Không thấy popup này nữa -> Chuyển sang loại vũ khí tiếp theo
                
    print("✅ Đã dọn dẹp xong màn hình!")
    await asyncio.sleep(1) # Nghỉ ngơi 1 chút trước khi sang tab Tôi


async def bam_vao_tab_toi(page, selector_toi):
    """Hàm tự động bấm vào mục Tôi dựa trên cấu hình DB"""
    if not selector_toi:
        print("⚠️ Chưa cấu hình 'nut_toi' trên Cloud, bỏ qua bước này.")
        return False

    print(f"👉 Đang tìm và click vào mục 'Tôi' (Selector: {selector_toi})...")
    try:
        nut_toi = page.locator(f"{selector_toi}:visible").last
        
        # Đợi nút hiện ra tối đa 60s
        await nut_toi.wait_for(state="visible", timeout=60000)
        await smart_click(nut_toi)
        print("✔️ Đã click tab 'Tôi'!")
        
        # CHỜ CHUYỂN CẢNH: Sang trang cá nhân thường phải load dữ liệu
        await asyncio.sleep(3) 
        return True
    except Exception as e:
        print(f"❌ Không click được nút 'Tôi'. Lỗi: {e}")
        return False


async def bam_vao_rut_tien(page, selector_rut_tien):
    """Hàm tự động bấm vào mục Rút Tiền dựa trên cấu hình DB"""
    if not selector_rut_tien:
        print("⚠️ Chưa cấu hình 'nut_rut_tien' trên Cloud, bỏ qua bước này.")
        return False

    print(f"💸 Đang tìm và click vào 'Rút Tiền' (Selector: {selector_rut_tien})...")
    try:
        nut = page.locator(f"{selector_rut_tien}:visible").last
        
        # Đợi nút hiện ra tối đa 10s
        await nut.wait_for(state="visible", timeout=10000)
        await smart_click(nut)
        
        print("✔️ Đã truy cập thành công vào trang Rút Tiền!")
        
        # CHỜ CHUYỂN CẢNH: Để form rút tiền load lên cho bạn nhìn thấy
        await asyncio.sleep(3)
        return True
    except Exception as e:
        print(f"❌ Không click được nút 'Rút Tiền'. Lỗi: {e}")
        return False
    
# --- TRONG FILE: actions.py ---

async def cai_dat_mat_khau_rut_tien(page, mat_khau, selector_o_nhap, selector_xac_nhan):
    # Sử dụng class chuẩn từ ảnh F12
    if not selector_o_nhap: 
        selector_o_nhap = 'ul.ui-password-input__security.hairline--surround'
    if not selector_xac_nhan: 
        selector_xac_nhan = "button:has-text('Xác Nhận')" #

    print(f"🔐 Đang thiết lập mật khẩu rút tiền: {mat_khau}")
    
    try:
        pass_boxes = page.locator(selector_o_nhap)
        await pass_boxes.first.wait_for(state="visible", timeout=10000)
        count_boxes = await pass_boxes.count()
        
        for i in range(count_boxes):
            print(f"   -> Đang nhập hàng mật khẩu thứ {i+1}...")
            
            # Dùng smart_tap (ưu tiên tap cho bàn phím ảo)
            target_box = pass_boxes.nth(i)
            await smart_tap(target_box)
            await asyncio.sleep(0.8) # Đợi bàn phím ảo trồi lên
            
            # Kiểm tra bàn phím ảo
            ban_phim_ao = page.locator('.van-keypad, [class*="keyboard"], [class*="keypad"], .number-board').filter(visible=True).first
            
            if await ban_phim_ao.is_visible(timeout=2000):
                print("   ⌨️ Phát hiện bàn phím ảo, đang bấm số...")
                for so in mat_khau:
                    # Tìm nút số chính xác trong bàn phím ảo
                    nut_so = ban_phim_ao.get_by_text(so, exact=True).first
                    await smart_tap(nut_so) # smart_tap cho phím ảo
                    await asyncio.sleep(0.2)
            else:
                print("   ⌨️ Không thấy bàn phím ảo, dùng phím thật...")
                await page.keyboard.type(mat_khau, delay=150)
            
            await asyncio.sleep(0.5)

        # --- BẤM XÁC NHẬN ---
        print("   -> Bấm nút Xác Nhận...")
        nut_xn = page.locator(selector_xac_nhan).first
        await smart_click(nut_xn)
        
        # Đợi phản hồi từ server (thường có loading hoặc popup)
        await asyncio.sleep(2.0)
        return True

    except Exception as e:
        print(f"❌ Lỗi cài mật khẩu rút tiền: {e}")
        return False
# --- TRONG FILE: actions.py ---

async def bam_vao_them_tai_khoan(page, selector_them_tk):
    """Hàm tự động bấm vào mục Thêm Ngân Hàng"""
    
    # Nếu quên chưa cấu hình DB, tự động lấy backup selector này
    if not selector_them_tk: selector_them_tk = "span:text-is('Thêm Tài Khoản')"
    
    print(f"🏦 Đang tìm và click vào 'Thêm Tài Khoản'...")
    try:
        # Lấy nút đang hiển thị
        nut = page.locator(f"{selector_them_tk}:visible").last
        
        # Đợi nút hiện ra tối đa 7 giây
        await nut.wait_for(state="visible", timeout=7000)
        await smart_click(nut)
        
        print("✔️ Đã bấm 'Thêm Tài Khoản' thành công!")
        
        # Nghỉ 2s để form nhập ngân hàng (Tên thẻ, Số tài khoản...) tải ra màn hình
        await asyncio.sleep(2) 
        return True
    except Exception as e:
        print(f"❌ Không tìm thấy nút 'Thêm Tài Khoản'. Lỗi: {e}")
        return False

    
async def tai_khoan_ngan_hang(page, selector_them_tk):
    """Hàm tự động bấm vào mục Thêm Tài Khoản Ngân Hàng"""
    
    # Nếu quên chưa cấu hình DB, tự động lấy backup selector này
    if not selector_them_tk: selector_them_tk = "p:text-is('Tài khoản ngân hàng)"
    
    print(f"🏦 Đang tìm và click vào 'Thêm Tài hhoản ngân hàng '...")
    try:
        # Lấy nút đang hiển thị
        nut = page.locator(f"{selector_them_tk}:visible").last
        
        # Đợi nút hiện ra tối đa 7 giây
        await nut.wait_for(state="visible", timeout=7000)
        await smart_click(nut)
        
        print("✔️ Đã bấm 'Thêm Tài khoản ngân hàng' thành công!")
        
        # Nghỉ 2s để form nhập ngân hàng (Tên thẻ, Số tài khoản...) tải ra màn hình
        await asyncio.sleep(2) 
        return True
    except Exception as e:
        print(f"❌ Không tìm thấy nút 'Thêm tài Khoản ngân hàng'. Lỗi: {e}")
        return False
    
# --- TRONG FILE: actions.py ---

async def xac_minh_mat_khau_truoc_khi_them(page, mat_khau, selector_o_nhap, selector_xac_nhan):
    """Hàm nhập mật khẩu rút tiền để mở khóa form thêm ngân hàng"""
    
    # Gán giá trị mặc định nếu truyền vào None (giống hàm cài đặt)
    if not selector_o_nhap: 
        selector_o_nhap = 'ul.ui-password-input__security.hairline--surround'
    if not selector_xac_nhan: 
        selector_xac_nhan = "button:has-text('Tiếp Theo')"

    print(f"🔑 Đang xác minh mật khẩu: {mat_khau}")
    
    try:
        # 1. Tìm và chờ ô nhập xuất hiện
        pass_boxes = page.locator(selector_o_nhap).first
        await pass_boxes.wait_for(state="visible", timeout=10000)
        
        # 2. Kích hoạt bàn phím ảo (smart_tap ưu tiên tap → click → JS)
        print("   -> Đang chạm vào ô nhập để hiện bàn phím...")
        await smart_tap(pass_boxes)
        await asyncio.sleep(1.0) # Đợi bàn phím trồi hẳn lên

        # 3. Kiểm tra bàn phím ảo (Sử dụng selector linh hoạt)
        ban_phim_ao = page.locator('.van-keypad, [class*="keyboard"], [class*="keypad"], .number-board').filter(visible=True).first
        
        if await ban_phim_ao.is_visible(timeout=3000):
            print("   ⌨️ Phát hiện bàn phím ảo, đang bấm từng số...")
            for so in mat_khau:
                # Tìm nút số trong bàn phím ảo
                nut_so = ban_phim_ao.get_by_text(so, exact=True).first
                await smart_tap(nut_so)
                await asyncio.sleep(0.3) # Nghỉ ngắn giữa các lần bấm
        else:
            print("   ⌨️ Không thấy bàn phím ảo, sử dụng keyboard.type...")
            # Focus lại vào ô nhập trước khi gõ
            await pass_boxes.focus()
            await page.keyboard.type(mat_khau, delay=150)

        await asyncio.sleep(1.0) # Chờ hệ thống nhận đủ 6 số

        # 4. Bấm nút XÁC NHẬN (Dùng evaluate để ép click nếu bị che)
        print("   -> Bấm nút Xác Nhận mở form...")
        nut_ok = page.locator(selector_xac_nhan).first
        
        if await nut_ok.is_visible():
            # Dùng smart_click tự xử lý fallback
            await smart_click(nut_ok)
            
            print("✔️ Đã bấm Xác nhận thành công.")
            await asyncio.sleep(2.5) # Đợi form ngân hàng load
            return True
        else:
            print("❌ Không tìm thấy nút Xác nhận sau khi nhập mật khẩu.")
            return False

    except Exception as e:
        print(f"❌ Lỗi xác minh mật khẩu: {e}")
        return False
# --- TRONG FILE: actions.py ---

async def dien_thong_tin_ngan_hang(page, so_tai_khoan, ten_ngan_hang, cfg):
    """Hàm điền form ngân hàng — hỗ trợ cả Desktop & Mobile Hidemium"""
    
    selector_stk = cfg.get("input_stk", "input[placeholder*='số tài khoản']")
    selector_tim_nh = cfg.get("input_tim_ngan_hang", "input[placeholder*='Chọn ngân hàng']")
    selector_luu = cfg.get("nut_luu_ngan_hang", "button:has-text('Xác Nhận')")
    # Selector item ngân hàng trong dropdown — có thể cấu hình từ Cloud
    selector_item_nh = cfg.get("item_ngan_hang", ".ui-options__option._bankOption_r0ahx_213")

    print(f"🏦 Bắt đầu nhập liệu: STK[{so_tai_khoan}] - NH[{ten_ngan_hang}]")
    
    try:
        # 1. NHẬP SỐ TÀI KHOẢN
        o_stk = page.locator(selector_stk).last
        await smart_tap(o_stk)
        await asyncio.sleep(0.5)
        await page.keyboard.type(str(so_tai_khoan), delay=100)

        # 2. TÌM NGÂN HÀNG
        print(f"   -> Đang chạm vào ô tìm kiếm ngân hàng...")
        o_tim = page.locator(selector_tim_nh).last
        await smart_tap(o_tim)
        await asyncio.sleep(1.0)

        # Gõ tên ngân hàng để lọc
        await page.keyboard.type(ten_ngan_hang, delay=100)
        await asyncio.sleep(3.0) # Đợi web load kết quả (mobile cần lâu hơn)

        # 3. BẤM CHỌN NGÂN HÀNG — THỬ NHIỀU CHIẾN LƯỢC
        item_ngan_hang = None
        da_chon = False

        # Chiến lược 1: Tìm chính xác bằng selector cấu hình + exact text
        print(f"   🔍 Tìm '{ten_ngan_hang}' bằng selector: {selector_item_nh}")
        try:
            loc1 = page.locator(selector_item_nh).get_by_text(ten_ngan_hang, exact=True).last
            if await loc1.is_visible(timeout=3000):
                item_ngan_hang = loc1
                print(f"   ✅ Tìm thấy (exact match)")
        except:
            pass

        # Chiến lược 2: Tìm chứa text (không exact) — phòng trường hợp web thêm khoảng trắng
        if not item_ngan_hang:
            print(f"   🔍 Thử tìm (contains match)...")
            try:
                loc2 = page.locator(selector_item_nh).get_by_text(ten_ngan_hang, exact=False).last
                if await loc2.is_visible(timeout=3000):
                    item_ngan_hang = loc2
                    print(f"   ✅ Tìm thấy (contains match)")
            except:
                pass

        # Chiến lược 3: Tìm rộng hơn — bỏ qua selector class, tìm bất kỳ element chứa text
        if not item_ngan_hang:
            print(f"   🔍 Thử tìm rộng (any visible element)...")
            try:
                loc3 = page.get_by_text(ten_ngan_hang, exact=False).last
                if await loc3.is_visible(timeout=3000):
                    item_ngan_hang = loc3
                    print(f"   ✅ Tìm thấy (broad match)")
            except:
                pass

        # Nếu tìm được → scroll vào view rồi click
        if item_ngan_hang:
            print(f"   🎯 Đã thấy '{ten_ngan_hang}'. Đang cuộn vào view và chọn...")
            # Scroll element vào viewport trước (mobile hay bị che)
            await item_ngan_hang.scroll_into_view_if_needed()
            await asyncio.sleep(0.5)
            await smart_click(item_ngan_hang)
            
            # Kiểm tra xem dropdown đã đóng chưa (dấu hiệu chọn thành công)
            await asyncio.sleep(1.5)
            try:
                still_visible = await page.locator(selector_item_nh).first.is_visible(timeout=2000)
                if still_visible:
                    # Dropdown vẫn mở → thử tap lại bằng JS
                    print(f"   ⚠️ Dropdown vẫn mở, thử tap lại bằng JS...")
                    await item_ngan_hang.evaluate("""node => {
                        node.dispatchEvent(new PointerEvent('pointerdown', {bubbles: true}));
                        node.dispatchEvent(new PointerEvent('pointerup', {bubbles: true}));
                        node.dispatchEvent(new TouchEvent('touchstart', {bubbles: true}));
                        node.dispatchEvent(new TouchEvent('touchend', {bubbles: true}));
                        node.click();
                    }""")
                    await asyncio.sleep(1.5)
            except:
                pass  # Dropdown đã đóng → OK
            
            da_chon = True
            print(f"   => Đã chọn xong: {ten_ngan_hang}")
        else:
            print(f"   ❌ Không tìm thấy '{ten_ngan_hang}' trong danh sách!")
            # Debug: In ra tất cả các option đang hiện
            try:
                all_items = page.locator(selector_item_nh)
                count = await all_items.count()
                print(f"   📋 Số lượng item hiện tại: {count}")
                for i in range(min(count, 5)):
                    txt = await all_items.nth(i).inner_text()
                    print(f"      [{i}] {txt}")
            except:
                pass
            return False

        if not da_chon:
            return False

        # 4. BẤM XÁC NHẬN
        print("   -> Bấm Xác Nhận lưu form...")
        btn_xn = page.locator(selector_luu).last
        await smart_click(btn_xn)
        
        await asyncio.sleep(3) 
        return True

    except Exception as e:
        print(f"❌ Lỗi điền form Ngân hàng: {e}")
        return False
     

ocr = ddddocr.DdddOcr(show_ad=False)
async def xu_ly_captcha(page, cfg):

    anh_selector = cfg.get("anh_captcha")
    input_selector = cfg.get("input_captcha")
    print("Bắt đầu xử lý Captcha...")
    if anh_selector and input_selector:
        print("🔍 Phát hiện cấu hình Captcha, đang tiến hành giải...")
        try:
            # 1. Tìm ô nhập và ÉP CỨNG FOCUS vào đó
            o_nhap = page.locator(cfg["input_captcha"])
            await o_nhap.focus()
            
            # Dừng lại 1.5 giây để đợi web load và hiển thị cái ảnh captcha ra
            await page.wait_for_timeout(1500)
            
            # 2. Chụp lén cái ảnh (trong khi con trỏ chuột vẫn đang nhấp nháy ở ô nhập)
            anh_element = page.locator(cfg["anh_captcha"])
            image_bytes = await anh_element.screenshot()
            
            # 3. Đưa ảnh cho mắt thần ddddocr đọc
            text_captcha = ocr.classification(image_bytes)
            print(f"🤖 Đã giải mã được mã Captcha: {text_captcha}")
            
            # 4. Gõ kết quả vào ô (Dùng .type để gõ từng phím, không làm mất focus)
            # Chú ý: Tuyệt đối không dùng .fill() ở đây
            await o_nhap.type(text_captcha, delay=100)
            print("Đã nhập xong Captcha!")
            
        except Exception as e:
            print(f"Lỗi khi xử lý captcha: {e}")


import cv2
import numpy as np
import random
import asyncio
def calculate_distance_opencv(bg_path, slice_path):
    try:
        img_gray = cv2.imread(bg_path, 0)
        template = cv2.imread(slice_path, 0)

        # Lọc nhiễu ảnh để chỉ lấy đường viền lỗ trống
        bg_edge = cv2.Canny(img_gray, 100, 200)
        tp_edge = cv2.Canny(template, 100, 200)

        res = cv2.matchTemplate(bg_edge, tp_edge, cv2.TM_CCOEFF_NORMED)
        
        # C168: Lỗ trống thường nằm sau khoảng 1/3 chiều ngang ảnh
        # Gọt bỏ 60px đầu tiên để OpenCV không bao giờ bắt trúng điểm xuất phát (X=0)
        res[:, :60] = 0 
        
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        
        # Nếu độ khớp quá thấp ( < 0.2), có thể ảnh chụp bị lỗi
        if max_val < 0.15:
            print("⚠️ Độ khớp quá thấp, có thể tính toán sai.")

        return max_loc[0]
    except Exception as e:
        print(f"❌ Lỗi OpenCV: {e}")
        return 0
    
async def get_final_distance(page, cfg, gap_x_opencv):
    # 1. Lấy chiều rộng thực tế của khung Captcha trên màn hình web
    bg_box = await page.locator(cfg["captcha_bg_img"]).bounding_box()
    web_width = bg_box['width'] # Thường khoảng 260-300px

    # 2. Lấy chiều rộng của file ảnh mà OpenCV vừa xử lý
    import cv2
    img = cv2.imread("temp_bg.png")
    real_width = img.shape[1] # Có thể là 600px hoặc hơn

    # 3. Tính tỉ lệ và quy đổi
    ratio = web_width / real_width
    final_distance = gap_x_opencv * ratio
    
    print(f"📏 Web Width: {web_width} | Real Width: {real_width} | Ratio: {ratio}")
    return final_distance

async def giai_captcha_keo_opencv(page, cfg):
    try:
        # 0. XÓA ẢNH CŨ
        for f in ["temp_bg.png", "temp_slice.png"]:
            if os.path.exists(f):
                os.remove(f)
                
        # 1. Chờ khung captcha xuất hiện
        bg_selector = cfg["captcha_bg_img"]
        slice_selector = cfg["captcha_slice_img"]
        bg_locator = page.locator(bg_selector)
        
        await bg_locator.wait_for(state="visible", timeout=10000)

        # 2. CHỜ CHIẾN THUẬT: Đợi ảnh load hoàn toàn
        await asyncio.sleep(2.5) 

        # 3. Chụp ảnh mới nhất
        print("📸 Đang chụp ảnh Captcha...")
        await bg_locator.screenshot(path="temp_bg.png")
        await page.locator(slice_selector).screenshot(path="temp_slice.png")

        # 4. Tính toán khoảng cách bằng OpenCV
        gap_x_raw = calculate_distance_opencv("temp_bg.png", "temp_slice.png")
        if gap_x_raw <= 0:
            print("⚠️ OpenCV không tìm thấy lỗ trống.")
            return False

        distance = await get_final_distance(page, cfg, gap_x_raw)
        print(f"📏 Web Width: {distance/0.33:.1f} | Gap: {gap_x_raw} | Distance: {distance:.2f}px")

        # 5. Lấy tọa độ nút kéo
        slider_locator = page.locator(cfg["captcha_slider_btn"])
        box = await slider_locator.bounding_box()
        if not box:
            return False
            
        start_x = box['x'] + box['width'] / 2
        start_y = box['y'] + box['height'] / 2

        # 6. THỰC HIỆN KÉO
        await page.mouse.move(start_x, start_y)
        await page.mouse.down()
        await asyncio.sleep(0.3)

        steps = 100
        for i in range(1, steps + 1):
            t = i / steps
            move_ratio = 1 - (1 - t) ** 3 # Ease Out
            current_x = start_x + (distance * move_ratio)
            current_y = start_y + random.uniform(-1, 1)
            
            await page.mouse.move(current_x, current_y, steps=1)
            if i % 10 == 0:
                await asyncio.sleep(0.01)

        await asyncio.sleep(0.5) 
        await page.mouse.up() 
        
        print("🖱️ Đã kéo xong, đang đợi kiểm tra kết quả...")
        await asyncio.sleep(4.0) # Đợi web check kết quả

        # 7. KIỂM TRA THỰC TẾ
        is_still_visible = await page.locator(bg_selector).is_visible()
        
        if is_still_visible:
            print("❌ Captcha vẫn còn, đang bấm làm mới...")
            refresh_btn = page.locator("div[class*='botion_refresh']")
            if await refresh_btn.is_visible():
                await refresh_btn.click()
            return False 
        
        print("✅ Thành công!")
        return True

    except Exception as e:
        print(f"❌ Lỗi khi giải captcha: {e}")
        return False
    
