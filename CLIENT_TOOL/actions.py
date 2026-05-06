# --- TRONG FILE: actions.py ---
import asyncio
import ddddocr
import random
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from path_helper import get_data_path

async def smart_click(locator, timeout=5000):
    """
    Hệ thống Click thích ứng: Cực kỳ mạnh mẽ, bắn đa sự kiện để đảm bảo web nhận lệnh.
    """
    try:
        # 1. Chờ phần tử xuất hiện (giảm timeout xuống 3s để ko bị treo lâu)
        await locator.wait_for(state="visible", timeout=3000)
        
        # 2. Thử cách bấm chuẩn của Playwright (Tap/Click)
        try:
            is_touch = await locator.page.evaluate("() => 'ontouchstart' in window")
            if is_touch:
                # Dùng tap với timeout ngắn
                await locator.tap(timeout=2000)
            else:
                # Dùng click với timeout ngắn
                await locator.click(timeout=2000, delay=random.randint(50, 100))
            return True
        except:
            pass # Nếu lỗi thì chuyển sang ép bằng JS ngay

        # 3. CHIẾN LƯỢC ÉP LỆNH: Bắn toàn bộ chuỗi sự kiện (Touch + Mouse + Click)
        await locator.evaluate("""node => {
            const opts = {bubbles: true, cancelable: true, view: window};
            
            // Bắn chuỗi Touch (cho Mobile)
            node.dispatchEvent(new TouchEvent('touchstart', opts));
            node.dispatchEvent(new TouchEvent('touchend', opts));
            
            // Bắn chuỗi Mouse (cho Desktop)
            node.dispatchEvent(new MouseEvent('mousedown', opts));
            node.dispatchEvent(new MouseEvent('mouseup', opts));
            
            // Bấm thật sự
            node.click();
            if (node.parentElement && node.parentElement.click) node.parentElement.click();
        }""")
        return True
        
    except Exception as e:
        print(f"⚠️ Lỗi bấm: {e}")
        return False


async def smart_tap(locator, timeout=5000):
    """Alias cho smart_click để đảm bảo tính nhất quán toàn hệ thống"""
    return await smart_click(locator, timeout)


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

# async def cai_dat_mat_khau_rut_tien(page, mat_khau, cfg):
#     # Lấy selector từ DB, nếu không có thì dùng mặc định của c168
#     selector_1 = cfg.get("o_nhap_pass_rut", 'ul.ui-password-input__security.hairline--surround')
#     selector_2 = cfg.get("o_nhap_xac_nhan_pass_rut") # hi144 sẽ có cái này, c168 là None
#     selector_xac_nhan = cfg.get("nut_xacnhan_pass_rut", "button:has-text('Xác Nhận')")

#     print(f"🔐 Đang thiết lập mật khẩu rút tiền: {mat_khau}")
    
#     # --- HÀM CON: Dùng để nhập pass vào 1 ô bất kỳ (Bản Nâng Cấp Chống Trượt) ---
#     # --- HÀM CON: Dùng để nhập pass vào 1 ô bất kỳ (Full Smart Click) ---
#     async def thuc_hien_nhap_mat_khau(target_box):
#         await target_box.wait_for(state="visible", timeout=5000)
        
#         # 1. Gọi bàn phím ảo lên bằng smart_click
#         print("   -> Gọi bàn phím ảo...")
#         await smart_click(target_box) 
        
#         # Đợi 1.5s để bàn phím trồi lên xong hẳn
#         await asyncio.sleep(1.5) 
        
#         ban_phim_ao = page.locator('.van-keypad, [class*="keyboard"], [class*="keypad"], .number-board').filter(visible=True).first
        
#         if await ban_phim_ao.is_visible(timeout=1000):
#             print("   ⌨️ Bàn phím ảo đã lên, đang gõ số...")
#             for so in mat_khau:
#                 nut_so = ban_phim_ao.get_by_text(so, exact=True).first
                
#                 # 2. Dùng smart_click gõ từng số
#                 await smart_click(nut_so) 
                
#                 # Giữ delay 0.3s để web kịp nhận diện từng nhịp nhấn
#                 await asyncio.sleep(0.3) 
#         else:
#             print("   ⌨️ Không thấy bàn phím ảo, dùng phím thật...")
#             # Dùng phím tắt để xóa an toàn
#             # await page.keyboard.press("Control+A")
#             # await page.keyboard.press("Backspace")
#             # await asyncio.sleep(0.2)
            
#             for char in mat_khau:
#                 await page.keyboard.press(char)
#                 await asyncio.sleep(0.15)
                
#         await asyncio.sleep(1.0) 
#     # --------------------------------------------------------------------------------------

#     try:
#         # TRƯỜNG HỢP 1: TRANG CÓ 2 Ô RIÊNG BIỆT (như hi144)
#         if selector_2:
#             print(" 🔄 Chế độ 2 ô selector riêng biệt (hi144)...")
#             # Nhập ô 1
#             print("   -> Đang nhập ô Mật Khẩu...")
#             await thuc_hien_nhap_mat_khau(page.locator(selector_1).first)
            
#             # Nhập ô 2
#             print("   -> Đang nhập ô Xác Nhận...")
#             await thuc_hien_nhap_mat_khau(page.locator(selector_2).first)

#         # TRƯỜNG HỢP 2: TRANG DÙNG 1 SELECTOR CHUNG CHO NHIỀU Ô (như c168)
#         else:
#             print(" 🔄 Chế độ 1 selector chung (c168/f168)...")
#             pass_boxes = page.locator(selector_1)
#             await pass_boxes.first.wait_for(state="visible", timeout=10000)
#             count_boxes = await pass_boxes.count()
            
#             for i in range(count_boxes):
#                 print(f"   -> Đang nhập hàng mật khẩu thứ {i+1}...")
#                 await thuc_hien_nhap_mat_khau(pass_boxes.nth(i))

#         # --- BẤM XÁC NHẬN ---
#         if selector_xac_nhan:
#             print(" -> Bấm nút Xác Nhận / Lưu...")
#             nut_xn = page.locator(selector_xac_nhan).first
            
#             # Dùng duy nhất 1 dòng smart_click này thôi:
#             await smart_click(nut_xn)
            
#             # Tăng thời gian chờ lên 4-5s để web kịp tắt popup "Thành công" 
#             # tránh chặn bước điền ngân hàng tiếp theo.
#             await asyncio.sleep(2.0)
            
#         return True

#     except Exception as e:
#         print(f"❌ Lỗi cài mật khẩu rút tiền: {e}")
#         return False

async def cai_dat_mat_khau_rut_tien(page, mat_khau, cfg):
    selector_1 = cfg.get("o_nhap_pass_rut", 'ul.ui-password-input__security.hairline--surround')
    selector_2 = cfg.get("o_nhap_xac_nhan_pass_rut") 
    selector_nhap_lai = cfg.get("o_nhap_lai_pass")
    selector_xac_nhan = cfg.get("nut_xacnhan_pass_rut", "button:has-text('Xác Nhận'), span:has-text('Gửi đi')")

    print(f"🔐 Đang thiết lập mật khẩu rút tiền: {mat_khau}")
    
    async def thuc_hien_nhap_mat_khau(target_box, label=""):
        try:
            await target_box.wait_for(state="visible", timeout=60000)
            await target_box.scroll_into_view_if_needed()
            
            # 🔥 BƯỚC QUAN TRỌNG CHO HI144: Ép focus bằng JS để web biết mình đang ở ô nào
            await target_box.evaluate("node => node.focus()")
            await asyncio.sleep(0.5)
            
            print(f"   -> Click gọi bàn phím cho {label}...")
            await smart_click(target_box) 
            await asyncio.sleep(1.5) # Đợi bàn phím trồi lên hẳn
            
            # Tìm bàn phím ảo (ưu tiên cái đang hiện - visible)
            ban_phim_ao = page.locator('.van-keypad, [class*="keyboard"], [class*="keypad"], .number-board').filter(visible=True).first
            
            if await ban_phim_ao.is_visible(timeout=1500):
                print(f"   ⌨️ Gõ bàn phím ảo cho {label}...")
                for so in mat_khau:
                    nut_so = ban_phim_ao.get_by_text(so, exact=True).first
                    await smart_click(nut_so) 
                    await asyncio.sleep(0.3) 
            else:
                print(f"   ⌨️ Không thấy bàn phím ảo, gõ phím thật vào {label}...")
                await target_box.focus() # Chắc chắn là đang focus
                for char in mat_khau:
                    await page.keyboard.press(char)
                    await asyncio.sleep(0.15)
                    
            await asyncio.sleep(1.0) # Nghỉ một nhịp giữa 2 ô
        except Exception as e:
            print(f"      ❌ Lỗi khi nhập {label}: {e}")
            raise e
    try:
        # --- XỬ LÝ RIÊNG CHO HI144 ---
        if selector_2:
            print(" 🔄 Chế độ 2 ô selector riêng biệt (hi144)...")
            
            # 1. Nhập ô Mật Khẩu
            o_1 = page.locator(selector_1).first
            await thuc_hien_nhap_mat_khau(o_1, "Ô Mật Khẩu")
            
            # 2. Đóng bàn phím cũ (nếu có) hoặc click ra ngoài/click ô 2 để reset trạng thái
            # hi144 đôi khi bị kẹt bàn phím cũ không nhận số cho ô mới
            # await page.mouse.click(0, 0) # Click nhẹ ra vùng trống
            await asyncio.sleep(0.5)

            # 3. Nhập ô Xác Nhận
            o_2 = page.locator(selector_2).first
            await thuc_hien_nhap_mat_khau(o_2, "Ô Xác Nhận")

        # --- TRƯỜNG HỢP CÒN LẠI (C168...) ---
        else:
            print(" 🔄 Chế độ 1 selector chung (c168/f168)...")
            pass_boxes = page.locator(selector_1)
            await pass_boxes.first.wait_for(state="visible", timeout=10000)
            count_boxes = await pass_boxes.count()
            for i in range(count_boxes):
                await thuc_hien_nhap_mat_khau(pass_boxes.nth(i), f"Hàng thứ {i+1}")

        # --- BẤM XÁC NHẬN ---
        if selector_xac_nhan:
            print(" -> Bấm nút Xác Nhận / Lưu...")
            nut_xn = page.locator(selector_xac_nhan).first
            await smart_click(nut_xn)
            await asyncio.sleep(2.5) # Chờ kết quả trả về
            
        return True

    except Exception as e:
        print(f"❌ Lỗi cài mật khẩu rút tiền: {e}")
        return False

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
    if not selector_them_tk: selector_them_tk = "p:text-is('Tài khoản ngân hàng')"
    
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


async def dien_thong_tin_ngan_hang(page, so_tai_khoan, ten_ngan_hang, chi_nhanh, cfg):
    """Hàm điền form ngân hàng — tự động tương thích c168, hi144 và các trang khác"""
    
    # 1. LẤY CẤU HÌNH TỪ DATABASE
    selector_stk = cfg.get("input_stk", "input[placeholder*='số tài khoản']")
    selector_tim_nh = cfg.get("input_tim_ngan_hang", "input[placeholder*='Chọn ngân hàng']")
    selector_nhap_ten_nh = cfg.get("input_ten_ngan_hang") # Ô gõ chữ ẩn bên trong Dropdown (dành cho hi144)
    selector_item_nh = cfg.get("item_ngan_hang", ".ui-options__option")
    selector_chi_nhanh = cfg.get("chi_nhanh")
    selector_luu = cfg.get("nut_luu_ngan_hang", "button:has-text('Xác Nhận'), button:has-text('Gửi đi')")

    print(f"🏦 Bắt đầu điền thẻ: NH[{ten_ngan_hang}] - STK[{so_tai_khoan}]")
    
    try:

        # --- MỚI: Đợi trang tải xong xuôi trước khi làm ---
        print("   -> Đang đợi trang form ngân hàng tải xong...")
        await page.wait_for_load_state("networkidle", timeout=15000) # Đợi mạng lặng im
        await page.wait_for_load_state("domcontentloaded")
        # ====================================================
        # BƯỚC 1: XỬ LÝ NGÂN HÀNG (Mở menu -> Gõ -> Chọn)
        # ====================================================
        # ====================================================
        # BƯỚC 1: MỞ DANH SÁCH NGÂN HÀNG (Bản cưỡng chế)
        # ====================================================
        print(f"   -> 1. Đang tìm và mở danh sách ngân hàng...")

        # 1. Đợi trang ổn định sau khi mạng lag
        await page.wait_for_load_state("domcontentloaded")
        
        # 2. Selector linh hoạt: Tìm cái nào THỰC SỰ đang hiện trên màn hình
        # Thay vì chỉ dùng .last, ta filter(visible=True) để loại bỏ nút ẩn
        o_tim = page.locator(selector_tim_nh).filter(visible=True).first 

        try:
            # Đợi dính vào code (attached) thay vì visible để tránh Timeout oan do lag
            await o_tim.wait_for(state="attached", timeout=15000)
            await o_tim.scroll_into_view_if_needed()
            
            # 3. THỬ CLICK: Nếu smart_click không ăn sau 3s, dùng JS Click ép buộc
            try:
                # Thử click bình thường trước
                await o_tim.wait_for(state="visible", timeout=3000)
                await smart_click(o_tim)
            except:
                print("   ⚠️ Click thường thất bại/Timeout, dùng JS Click cưỡng chế...")
                # Chiêu cuối: JS Click đâm xuyên qua mọi lớp phủ, mọi trạng thái ẩn
                await o_tim.evaluate("node => node.click()")

            # Đợi 1.5s để menu thực sự xòe ra
            await asyncio.sleep(1.5) 

        except Exception as e:
            print(f"   ❌ Lỗi nghiêm trọng không thể tác động vào ô ngân hàng: {e}")
            return False
       # Gõ tên ngân hàng
        if selector_nhap_ten_nh:
            # Chế độ Dropdown 2 lớp (hi144)
            print("      -> Bắt được ô nhập bên trong Dropdown, đang gõ tên...")
            o_nhap = page.locator(selector_nhap_ten_nh).filter(visible=True).first
            
            # --- ĐOẠN NÀY ĐÃ ĐƯỢC SỬA ĐỂ VƯỢT RÀO DISABLED ---
            await o_nhap.evaluate("node => node.focus()") # Dùng JS ép Focus để vượt mặt Playwright
            await o_nhap.fill("", force=True)             # Thêm force=True để cưỡng chế xóa trắng
            await page.keyboard.type(ten_ngan_hang, delay=100)
            # --------------------------------------------------
            
        else:
            # Chế độ Input bình thường (c168)
            print("      -> Chế độ Input thường, đang gõ tên...")
            await o_tim.focus()
            await o_tim.fill("")
            await page.keyboard.type(ten_ngan_hang, delay=100)
            
        await asyncio.sleep(2.0) # Đợi web lọc danh sách kết quả

       # Bấm chọn Ngân hàng
        print(f"   -> 2. Tìm và click linh hoạt: {ten_ngan_hang}")
        item_ngan_hang = None
        
        # Tạo "băng đạn" các biến thể để gõ thử (giữ nguyên, xóa cách, thêm cách)
        cac_bien_the_go = [ten_ngan_hang]
        
        # Thêm bản không có dấu cách (VD: MB BANK -> MBBANK)
        ten_khong_dau_cach = ten_ngan_hang.replace(" ", "")
        cac_bien_the_go.append(ten_khong_dau_cach)
        
        # Thêm bản có dấu cách đặc trị cho MB (VD: MBBANK -> MB BANK)
        if "MBBANK" in ten_ngan_hang.upper() or "MB" == ten_ngan_hang.upper():
            cac_bien_the_go.append("MB BANK")
            
        # Xóa các biến thể trùng lặp nhưng giữ nguyên thứ tự (Mẹo nhỏ của Python)
        cac_bien_the_go = list(dict.fromkeys(cac_bien_the_go))
        
        # Chuẩn hóa tên ngân hàng đích (Viết hoa, xóa cách để lát nữa so sánh)
        ten_can_tim_chuan = ten_ngan_hang.upper().replace(" ", "")

        # Bắt đầu thử gõ từng biến thể vào ô tìm kiếm
        for tu_khoa in cac_bien_the_go:
            print(f"      -> Đang thử gõ từ khóa: '{tu_khoa}'")
            
            # Bôi đen và xóa sạch ô tìm kiếm (chuẩn bị cho lần gõ)
            await page.keyboard.press("Control+A")
            await page.keyboard.press("Backspace")
            
            # Gõ từ khóa vào
            await page.keyboard.type(tu_khoa, delay=100)
            await asyncio.sleep(1.5) # Đợi 1.5s cho web load xong danh sách
            
            # Lấy các kết quả ĐANG HIỂN THỊ
            danh_sach_option = page.locator(selector_item_nh).filter(visible=True)
            so_luong = await danh_sach_option.count()
            
            # Nếu web có nhả kết quả ra -> Tiến hành đối chiếu chính xác
            if so_luong > 0:
                for i in range(so_luong):
                    opt = danh_sach_option.nth(i)
                    text_thuc_te = await opt.inner_text()
                    
                    # Chuẩn hóa text trên web để so
                    text_web_chuan = text_thuc_te.upper().replace(" ", "")
                    
                    if ten_can_tim_chuan == text_web_chuan or ten_can_tim_chuan in text_web_chuan:
                        item_ngan_hang = opt
                        print(f"      -> 🎯 Bắt đúng mục tiêu: '{text_thuc_te}'")
                        break # Tìm thấy là dừng vòng lặp đối chiếu
            
            # Nếu đã chốt được ngân hàng rồi thì dừng luôn vòng lặp gõ phím
            if item_ngan_hang:
                break
                
        # Cuối cùng: Chốt hạ
        if item_ngan_hang:
            await item_ngan_hang.scroll_into_view_if_needed()
            await smart_click(item_ngan_hang)
            print("      ✅ Chọn ngân hàng thành công!")
            await asyncio.sleep(1.0)
        else:
            print(f"      ❌ Đã thử các kiểu gõ nhưng web không có ngân hàng '{ten_ngan_hang}'!")
            return False

        # ====================================================
        # BƯỚC 2: NHẬP SỐ TÀI KHOẢN
        # ====================================================
        print(f"   -> 3. Nhập STK: {so_tai_khoan}")
        o_stk = page.locator(selector_stk).last
        await smart_click(o_stk)
        await o_stk.focus()
        await o_stk.fill(str(so_tai_khoan))
        
        # Kiểm tra nếu fill chưa ăn thì gõ phím cứng
        val = await o_stk.input_value()
        if not val: await page.keyboard.type(str(so_tai_khoan), delay=100)
        await asyncio.sleep(0.5)

        # ====================================================
        # BƯỚC 3: NHẬP CHI NHÁNH (Dành riêng hi144)
        # ====================================================
        if selector_chi_nhanh:
            print("   -> 4. Đang nhập Chi nhánh...")
            try:
                o_chi_nhanh = page.locator(selector_chi_nhanh).last
                await smart_click(o_chi_nhanh)
                await o_chi_nhanh.fill(chi_nhanh) # Có thể thay bằng dữ liệu lấy từ DB
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"      ⚠️ Lỗi nhập chi nhánh: {e}")

        # ====================================================
        # BƯỚC 4: BẤM XÁC NHẬN LƯU THẺ
        print("   -> Bấm Xác Nhận lưu form...")
        btn_xn = page.locator(selector_luu).last
        await smart_click(btn_xn)
        
        await asyncio.sleep(3) 
        return True

    except Exception as e:
        print(f"❌ Lỗi điền form Ngân hàng: {e}")
        return False


import threading
import ddddocr

# Tạo một "khóa" chung để các luồng xếp hàng giải Captcha, tránh xung đột
ocr_lock = threading.Lock()
ocr = ddddocr.DdddOcr(show_ad=False)

async def xu_ly_captcha(page, cfg):
    anh_selector = cfg.get("anh_captcha") # Lưu ý: Key này phải đồng nhất với file config (anh_captcha)
    input_selector = cfg.get("input_captcha")
    
    if not (anh_selector and input_selector):
        return True # Nếu không có cấu hình thì coi như không cần giải -> Pass

    print("🔍 Bắt đầu xử lý Captcha số...")
    try:
        # 1. Tìm ô nhập và ÉP CỨNG FOCUS vào đó
        o_nhap = page.locator(input_selector).last
        await o_nhap.focus()
        await asyncio.sleep(2) 
        
        # [QUAN TRỌNG] Bôi đen và xóa sạch dữ liệu cũ (đề phòng đây là lần retry thứ 2, thứ 3)
        await page.keyboard.press("Control+A")
        await page.keyboard.press("Backspace")
        
        # Dừng lại 1.5 giây để đợi web load và hiển thị cái ảnh captcha ra
        await page.wait_for_timeout(1500)
        
        # 2. Chụp lén cái ảnh
        anh_element = page.locator(anh_selector).last
        
        # Đảm bảo ảnh đã hiện ra trước khi chụp
        if not await anh_element.is_visible(timeout=3000):
            print("❌ Không thấy ảnh Captcha xuất hiện!")
            return False # Báo lỗi để vòng lặp thử lại
            
        image_bytes = await anh_element.screenshot()
        
        # 3. Đưa ảnh cho mắt thần ddddocr đọc
        with ocr_lock:
            text_captcha = ocr.classification(image_bytes)
            
        # Nếu AI không đọc ra được chữ nào (trả về chuỗi rỗng)
        if not text_captcha:
            print("❌ ddddocr không nhận diện được chữ nào!")
            return False # Báo lỗi để vòng lặp click lấy ảnh khác
            
        print(f"🤖 Đã giải mã được mã Captcha: {text_captcha}")
        
        # 4. Gõ kết quả vào ô
        await o_nhap.type(text_captcha, delay=100)
        print("✅ Đã nhập xong Captcha!")
        
        return True # BÁO CÁO THÀNH CÔNG ĐỂ BÊN KIA THOÁT VÒNG LẶP
        
    except Exception as e:
        print(f"❌ Lỗi khi xử lý captcha: {e}")
        return False # BÁO LỖI ĐỂ CHẠY LẠI

# async def xu_ly_captcha(page, cfg):
#     anh_selector = cfg.get("anh_captcha")
#     input_selector = cfg.get("input_captcha")
    
#     if not (anh_selector and input_selector):
#         return True

#     print("🔍 Bắt đầu xử lý Captcha số...")
#     try:
#         # 1. TÌM Ô NHẬP & CHUẨN BỊ
#         o_nhap = page.locator(input_selector).last
#         await o_nhap.scroll_into_view_if_needed()
#         await o_nhap.click() # Click vào để kích hoạt focus
        
#         # Xóa dữ liệu cũ
#         await page.keyboard.press("Control+A")
#         await page.keyboard.press("Backspace")

#         # 2. ĐỢI ẢNH HIỆN HÌNH (THAY ĐỔI QUAN TRỌNG TẠI ĐÂY)
#         anh_element = page.locator(anh_selector).last
        
#         # Thay vì đợi 1.5s mù quáng, ta đợi cho đến khi nó THỰC SỰ xuất hiện trên màn hình
#         try:
#             await anh_element.wait_for(state="visible", timeout=5000)
#             # Thêm 1 nhịp nghỉ ngắn 1s để chắc chắn nội dung ảnh đã render xong (chống chụp ra ảnh trắng)
#             await asyncio.sleep(1) 
#         except:
#             print("❌ Quá 5s mà không thấy ảnh Captcha hiện ra!")
#             return False

#         # 3. CHỤP ẢNH & GIẢI MÃ
#         # Tip: Đôi khi ảnh bị cache cũ, ta có thể click vào ảnh để lấy ảnh mới nếu cần
#         # await anh_element.click() 
#         # await asyncio.sleep(1)

#         image_bytes = await anh_element.screenshot()
        
#         with ocr_lock:
#             text_captcha = ocr.classification(image_bytes)
            
#         if not text_captcha:
#             print("❌ AI không đọc được, đang click đổi ảnh khác...")
#             await anh_element.click() # Click vào ảnh để web đổi mã mới
#             return False 
            
#         print(f"🤖 Captcha: {text_captcha}")
        
#         # 4. NHẬP TỪNG CHỮ (MÔ PHỎNG NGƯỜI THẬT)
#         # Không dùng .type vì nó quá nhanh, dùng keyboard.type với delay
#         await o_nhap.focus()
#         for char in text_captcha:
#             await page.keyboard.type(char, delay=random.randint(150, 300))
            
#         print("✅ Đã nhập xong Captcha!")
#         return True 
        
#     except Exception as e:
#         print(f"❌ Lỗi: {e}")
#         return False

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
    
async def get_final_distance(page, cfg, gap_x_opencv, bg_path):
    # 1. Lấy chiều rộng thực tế của khung Captcha trên màn hình web
    bg_box = await page.locator(cfg["captcha_bg_img"]).bounding_box()
    web_width = bg_box['width'] 

    # 2. Đọc ảnh từ file CỦA RIÊNG LUỒNG NÀY (Không dùng temp_bg.png nữa)
    import cv2
    img = cv2.imread(bg_path) 
    real_width = img.shape[1] 

    # 3. Tính tỉ lệ và quy đổi
    ratio = web_width / real_width
    final_distance = gap_x_opencv * ratio
    
    print(f"📏 Web Width: {web_width} | Real Width: {real_width} | Ratio: {ratio}")
    return final_distance

async def giai_captcha_keo_opencv(page, cfg):
        # 0. XÓA ẢNH CŨ
    # Tạo tên file tạm duy nhất cho luồng này để tránh xung đột đa luồng
    id_luong = random.randint(1000, 9999)
    bg_path = get_data_path(f"bg_{id_luong}.png")
    slice_path = get_data_path(f"slice_{id_luong}.png")

    try:
        # 1. Chờ khung captcha xuất hiện
        bg_selector = cfg["captcha_bg_img"]
        slice_selector = cfg["captcha_slice_img"]
        bg_locator = page.locator(bg_selector)
        
        await bg_locator.wait_for(state="visible", timeout=10000)

        # 2. Đợi ảnh load hoàn toàn
        await asyncio.sleep(2.5) 

        # 3. Chụp ảnh (Dùng file riêng cho luồng này)
        print(f"📸 [Luồng {id_luong}] Đang chụp ảnh Captcha...")
        await bg_locator.screenshot(path=bg_path)
        await page.locator(slice_selector).screenshot(path=slice_path)

        # 4. Tính toán khoảng cách bằng OpenCV
        gap_x_raw = calculate_distance_opencv(bg_path, slice_path)
        
        if gap_x_raw <= 0:
            print(f"⚠️ [Luồng {id_luong}] OpenCV không tìm thấy lỗ trống.")
            # Dọn rác nếu lỗi
            for f in [bg_path, slice_path]:
                if os.path.exists(f): os.remove(f)
            return False

        # Truyền đường dẫn ảnh vào để lấy chiều rộng
        distance = await get_final_distance(page, cfg, gap_x_raw, bg_path)

        # XONG XUÔI HẾT RỒI MỚI XÓA FILE ĐỂ DỌN RÁC
        for f in [bg_path, slice_path]:
            if os.path.exists(f): os.remove(f)

        print(f"📏 Độ lệch chuẩn: {gap_x_raw} | Distance cần kéo: {distance:.2f}px")

        # 5. Lấy tọa độ nút kéo
        slider_locator = page.locator(cfg["captcha_slider_btn"])
        box = await slider_locator.bounding_box()
        if not box:
            return False
            
        start_x = box['x'] + box['width'] / 2
        start_y = box['y'] + box['height'] / 2

        # 6. THỰC HIỆN KÉO THÔNG MINH (Smart Drag - Hỗ trợ cả Tap và Click)
        print(f"🚀 Đang bắt đầu kéo {distance:.2f}px...")
        
        # Kiểm tra xem có phải mobile profile không (dựa trên touch support)
        is_mobile = await page.evaluate("() => 'ontouchstart' in window || navigator.maxTouchPoints > 0")
        
        if is_mobile:
            print("📱 Chế độ Mobile: Dùng Touch/Pointer Events để kéo...")
            steps = []
            for i in range(1, 21):
                t = i / 20
                move_ratio = 1 - (1 - t) ** 3
                steps.append({
                    'x': start_x + (distance * move_ratio),
                    'y': start_y + random.uniform(-2, 2)
                })

            # Sử dụng JS để dispatch touch và pointer events đồng thời
            await page.evaluate(f"""
                async ({{selector, steps, startX, startY}}) => {{
                    const el = document.querySelector(selector);
                    if (!el) return;

                    const touchId = Date.now(); // ID cố định cho cả phiên kéo
                    
                    const dispatch = (type, x, y) => {{
                        const touch = new Touch({{
                            identifier: touchId,
                            target: el,
                            clientX: x,
                            clientY: y,
                            pageX: x,
                            pageY: y,
                        }});

                        // Gửi cả Touch và Pointer Events để chắc chắn web nhận được
                        const commonParams = {{ 
                            bubbles: true, cancelable: true, 
                            clientX: x, clientY: y, 
                            screenX: x, screenY: y,
                            pointerId: 1, pointerType: 'touch', isPrimary: true
                        }};

                        if (type.startsWith('touch')) {{
                            el.dispatchEvent(new TouchEvent(type, {{
                                ...commonParams,
                                touches: [touch],
                                targetTouches: [touch],
                                changedTouches: [touch]
                            }}));
                        }} else {{
                            el.dispatchEvent(new PointerEvent(type, commonParams));
                        }}
                    }};

                    // Trình tự: PointerDown -> TouchStart
                    dispatch('pointerdown', startX, startY);
                    dispatch('touchstart', startX, startY);
                    
                    for (const step of steps) {{
                        await new Promise(r => setTimeout(r, 15 + Math.random() * 20));
                        dispatch('pointermove', step.x, step.y);
                        dispatch('touchmove', step.x, step.y);
                    }}
                    
                    // Trình tự: PointerUp -> TouchEnd
                    dispatch('pointerup', steps[steps.length-1].x, steps[steps.length-1].y);
                    dispatch('touchend', steps[steps.length-1].x, steps[steps.length-1].y);
                }}
            """, {
                'selector': cfg["captcha_slider_btn"],
                'steps': steps,
                'startX': start_x,
                'startY': start_y
            })
        else:
            print("💻 Chế độ Desktop: Kéo bằng Mouse (Human-like)...")
            await page.mouse.move(start_x, start_y)
            await page.mouse.down()
            await asyncio.sleep(0.2)

            # Chia nhỏ quãng đường kéo để mượt hơn
            steps = 40
            for i in range(1, steps + 1):
                t = i / steps
                # Công thức Ease-Out để kéo chậm dần khi về đích
                move_ratio = 1 - (1 - t) ** 3 
                curr_x = start_x + (distance * move_ratio)
                curr_y = start_y + random.uniform(-1, 1)
                
                await page.mouse.move(curr_x, curr_y, steps=1)
                if i % 8 == 0: await asyncio.sleep(0.01)

            await asyncio.sleep(0.4) 
            await page.mouse.up() 
        
        print("🖱️ Đã kéo xong, đang đợi kiểm tra kết quả...")
        await asyncio.sleep(3.5) 

        #7. KIỂM TRA THỰC TẾ
        is_still_visible = await page.locator(bg_selector).is_visible(timeout=3000)
        
        if is_still_visible:
            print("❌ Kéo trượt hoặc bị hệ thống phát hiện bot!")
            return False
            
        print("✅ Thành công vượt qua Captcha!")
        return True

    except Exception as e:
        print(f"❌ Lỗi khi giải captcha: {e}")
        # Tự động refresh captcha nếu lỗi
        try:
            refresh_btn = page.locator("div[class*='botion_refresh'], .refresh_btn").first
            if await refresh_btn.is_visible(): await refresh_btn.click()
        except: pass
        return False

        return False
    
