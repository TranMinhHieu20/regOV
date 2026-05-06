# --- TRONG FILE: flows.py ---
import asyncio
from CLIENT_TOOL.actions import bam_nut_dang_ky, don_dep_popup, kiem_tra_va_cho_captcha, bam_vao_tab_toi, bam_vao_rut_tien, cai_dat_mat_khau_rut_tien, tai_khoan_ngan_hang, xac_minh_mat_khau_truoc_khi_them, dien_thong_tin_ngan_hang, xu_ly_captcha, giai_captcha_keo_opencv, bam_vao_them_tai_khoan, smart_click

async def run_full_flow(page, target_url, user_data, cfg, report_status=None, is_aborted=None):
    def update_status(msg):
        if report_status:
            report_status(msg)
            
    try:
        if is_aborted and is_aborted(): return
        
        # Khởi tạo các biến trạng thái để tránh lỗi "not defined"
        vao_toi_thanh_cong = False
        vao_rut_tien_thanh_cong = False
        cai_dat_mat_khau_thanh_cong = False
        da_bam_them = False
        
        update_status(f"Mở trang {target_url}...")
        print(f"🚀 Bắt đầu chạy: {target_url}")
        await page.goto(target_url, timeout=40000)
        
        # CHỐNG ĐÓNG BĂNG TAB: Đánh lừa trang web luôn ở trạng thái Visible để chạy ngầm
        await page.add_init_script("""
            Object.defineProperty(document, 'visibilityState', {value: 'visible', writable: true});
            Object.defineProperty(document, 'hidden', {value: false, writable: true});
            document.dispatchEvent(new Event('visibilitychange'));
        """)
        
        await page.wait_for_selector(cfg["input_username"], timeout=15000)

        # ==========================================
        # DỌN POPUP
        # ========================================== 
        # await don_dep_popup(page, cfg.get("nut_dong_popup"))
        # await asyncio.sleep(1)
        
        # ==========================================
        # 1. NHẬP THÔNG TIN TÀI KHOẢN
        # ==========================================
        if is_aborted and is_aborted(): return
        update_status("Đang nhập thông tin Đăng ký...")
        await page.type(cfg["input_username"], user_data["username"])
        await page.type(cfg["input_password"], user_data["password"])
        
        if "input_realName" in cfg:
            await page.type(cfg["input_realName"], user_data["ten_that"])

        if "input_phone" in cfg:
            sdt_goc = user_data["sdt"]
            if cfg.get("cat_so_0") == True and sdt_goc.startswith("0"):
                sdt_de_dien = sdt_goc[1:]
                print(f"📱 SĐT: Đã cắt số 0 còn {sdt_de_dien}")
            else:
                sdt_de_dien = sdt_goc
                print(f"📱 SĐT: Giữ nguyên {sdt_de_dien}")
            await page.type(cfg["input_phone"], sdt_de_dien)

        if "input_email" in cfg:
            await page.type(cfg["input_email"], user_data['email'])

        # ==========================================
        # BƯỚC: GIẢI CAPTCHA SỐ (TRƯỚC KHI BẤM ĐĂNG KÝ)
        # ==========================================
        # if cfg.get("input_captcha"):
        #     update_status("Đang xử lý Captcha số...")
        #     max_retries = 3
        #     da_giai_xong = False
                

        #     for i in range(max_retries):
        #         # Kiểm tra nếu người dùng bấm Dừng tool giữa chừng
        #         if is_aborted and is_aborted(): return 

        #         print(f"🔄 Thử giải Captcha lần {i+1}...")
                
        #         # Gọi hàm từ file actions mà chúng ta vừa nâng cấp
        #         ket_qua = await xu_ly_captcha(page, cfg)
                
        #         if ket_qua is True:
        #             print("✅ Captcha đã được điền xong!")
        #             da_giai_xong = True
        #             break # Thoát vòng lặp thử lại, chuyển sang bấm nút
        #         else:
        #             print(f"❌ Lần {i+1} lỗi (AI đọc sai hoặc web lag).")
        #             if i < max_retries - 1:
        #                 # Bấm đổi ảnh khác để thử lại cho chắc ăn
        #                 try:
        #                     print("      -> Đang đổi ảnh Captcha mới...")
        #                     await page.locator(cfg.get("anh_captcha")).click()
        #                     await asyncio.sleep(1.5) # Đợi ảnh mới load
        #                 except:
        #                     pass
            
        #     if not da_giai_xong:
        #         print("🚨 Thử 3 lần đều thất bại. Dừng luồng để bảo vệ tài khoản!")
        #         update_status("Lỗi: Không giải được Captcha số")
        #         return False
        
        if cfg.get("input_captcha"):
            update_status("Đang xử lý Captcha số...")
            max_retries = 3
            da_giai_xong = False

            for i in range(max_retries):
                # Kiểm tra nếu người dùng bấm Dừng tool
                if is_aborted and is_aborted(): return 

                print(f"🔄 Thử giải Captcha lần {i+1}...")
                
                # 1. Gọi hàm giải Captcha
                ket_qua = await xu_ly_captcha(page, cfg)
                
                if ket_qua is True:
                    print("✅ Captcha đã được điền xong!")
                    da_giai_xong = True
                    break 
                else:
                    print(f"❌ Lần {i+1} lỗi (AI đọc sai hoặc web lag).")
                    
                    if i < max_retries - 1:
                        # BƯỚC QUAN TRỌNG: Kiểm tra và bấm nút xác nhận lỗi nếu có
                        xac_nhan_selector = cfg.get('xac_nhan')
                        if xac_nhan_selector:
                            try:
                                # Đợi nút xác nhận lỗi hiện ra trong thời gian ngắn (ví dụ 2s)
                                nut_confirm = page.locator(xac_nhan_selector).first
                                if await nut_confirm.is_visible(timeout=2000):
                                    print(" ⚠️ Phát hiện popup báo sai Captcha, đang bấm đóng...")
                                    await nut_confirm.click()
                                    await asyncio.sleep(0.5)
                            except:
                                # Nếu không thấy nút xác nhận thì thôi, bỏ qua để làm bước tiếp theo
                                pass

                        # 2. Đổi ảnh Captcha mới để thử lại
                        try:
                            print("      -> Đang đổi ảnh Captcha mới...")
                            # Dùng evaluate click để chắc chắn đổi được ảnh
                            await page.locator(cfg.get("anh_captcha")).first.evaluate("node => node.click()")
                            await asyncio.sleep(1.5) 
                        except:
                            pass
            
            if not da_giai_xong:
                print("🚨 Thử 3 lần đều thất bại. Dừng luồng!")
                update_status("Lỗi: Không giải được Captcha số")
                return False
        

        # ==========================================
        # 2. GỌI HÀM BẤM NÚT ĐĂNG KÝ
        # ==========================================
        if is_aborted and is_aborted(): return
        update_status("Chuẩn bị bấm Đăng ký...")
        print("\n--- BẮT ĐẦU QUÁ TRÌNH BẤM ĐĂNG KÝ ---")
        thanh_cong = await bam_nut_dang_ky(page, cfg["nut_dangky"])

        
        if not thanh_cong:
            return 
            
        # 3. CHỐT CHẶN CAPTCHA (ĐÃ SỬA LOGIC)
        # ==========================================
        
        # 3.1. Nếu là Captcha kéo (Slide)
        if cfg.get("captcha_slider_btn"):
            update_status("Đang giải Captcha hình ảnh...")
            max_retries = 3
            da_thanh_cong = False

            for i in range(max_retries):
                if is_aborted and is_aborted(): return
                update_status(f"Giải Captcha (lần {i+1})...")
                print(f"🔄 Đang giải Slide Captcha lần {i+1}...")
                
                # Gọi hàm giải và nhận kết quả trả về
                ket_qua = await giai_captcha_keo_opencv(page, cfg)
                
                if ket_qua is True:
                    print("✅ Hệ thống xác nhận: Giải Captcha thành công!")
                    da_thanh_cong = True
                    break  # Thoát vòng lặp for ngay lập tức
                else:
                    print(f"❌ Lần {i+1} không khớp. Đang chuẩn bị thử lại...")
                    # Đoạn Refresh đã được xử lý bên trong hàm giai_captcha_keo_opencv
                    # Chỉ cần đợi một chút để ảnh mới ổn định
                    await asyncio.sleep(2.0)

            if not da_thanh_cong:
                print("🚨 Đã thử 3 lần nhưng không qua được Captcha. Dừng flow!")
                return # Thoát ra nếu thử hết số lần mà vẫn lỗi

       # 3.2. Nếu là Captcha chờ thủ công (Trường hợp web có loại captcha lạ)
        # Sửa lại thành kiểm tra cờ 'captcha_thu_cong' thay vì 'input_captcha'
        if cfg.get("captcha_thu_cong"):
            update_status("Phát hiện Captcha lạ. Đang chờ giải thủ công...")
            tiep_tuc = await kiem_tra_va_cho_captcha(page) 
            if not tiep_tuc:
               return
        # ==========================================
        # 4. GỌI HÀM QUÉT POPUP
        # ==========================================
        # Sau khi giải captcha xong, web mới hiện Popup thành công hoặc thông báo
        if is_aborted and is_aborted(): return
        update_status("Đang dọn dẹp Popup rác...")
        await don_dep_popup(page, cfg.get("nut_dong_popup"))
        await asyncio.sleep(1)
        

        # ==========================================
        # 5. TỰ ĐỘNG BẤM VÀO TAB "TÔI"
        # ==========================================
        update_status("Truy cập trang Cá nhân...")
        print("\n--- BƯỚC CUỐI: KIỂM TRA TÀI KHOẢN ---")
        # Truyền cấu hình từ cfg vào hàm
        vao_toi_thanh_cong = await bam_vao_tab_toi(page, cfg.get("nut_toi"))
        await asyncio.sleep(1)
        

        # ==========================================
        # 6. TỰ ĐỘNG BẤM "RÚT TIỀN" (MỚI THÊM)
        # ==========================================
        if vao_toi_thanh_cong:
            update_status("Vào mục Rút Tiền...")
            print("\n--- BƯỚC 6: VÀO MỤC RÚT TIỀN ---")
            vao_rut_tien_thanh_cong = await bam_vao_rut_tien(page, cfg.get("nut_rut_tien"))
            # Nghỉ 2s để nhìn thấy form Rút tiền hiện ra
            await asyncio.sleep(1)
        
        # --- TRONG flows.py ---
        current_url = page.url.lower()

        if "qq88" in current_url:
            from special_flows import flow_full_qq88
            # Chạy toàn bộ luồng QQ88 và dừng lại
            await flow_full_qq88(page, cfg, user_data)
            return
        
        # ==========================================
        # 7. CÀI ĐẶT MẬT KHẨU RÚT TIỀN (MỚI - ĐÃ NÂNG CẤP)
        # ==========================================
        if is_aborted and is_aborted(): return
        if vao_rut_tien_thanh_cong:
            update_status("Cài đặt MK Rút Tiền...")
            print("\n--- BƯỚC 7: CÀI ĐẶT MẬT KHẨU RÚT TIỀN ---")

            # KIỂM TRA: Nếu có selector 'o_nhap_lai_pass', chạy luồng đặc biệt 3 ô
            if cfg.get("o_nhap_lai_pass"):
                from special_flows import flow_rut_tien_3_o_dac_biet
                print("🛡️ Phát hiện Layout 3 ô - Chạy luồng từ special_flows.py...")
                
                # Gọi file mới bạn vừa tạo
                cai_dat_mat_khau_thanh_cong = await flow_rut_tien_3_o_dac_biet(page, cfg, user_data)
                
                # Nếu chạy xong luồng đặc biệt này, bạn có thể cho nó tiếp tục hoặc dừng tùy ý
                # Thường là return True nếu đây là bước cuối cùng bạn muốn thực hiện
            else:
            

            # 7.1. KIỂM TRA NÚT "CÀI ĐẶT" (Bản sửa lỗi đặc trị mạng lag)
                selector_cai_dat = cfg.get("nut_cai_dat")
                if selector_cai_dat:
                    try:
                        # Tìm locator
                        nut_cai_dat_locator = page.locator(selector_cai_dat).first
                        
                        # 1. Đợi nó xuất hiện trong cấu trúc code trước (bất kể ẩn hiện)
                        await nut_cai_dat_locator.wait_for(state="attached", timeout=60000)
                        
                        # 2. Cuộn tới nó (giúp kích hoạt trạng thái visible trên nhiều web)
                        await nut_cai_dat_locator.scroll_into_view_if_needed()
                        
                        # 3. Kiểm tra visible, nếu mạng quá lag mà không hiện thì dùng JS Click luôn
                        if await nut_cai_dat_locator.is_visible(timeout=60000):
                            print(f"   -> 🛠️ Bấm nút Cài đặt bằng smart_click...")
                            await smart_click(nut_cai_dat_locator)
                        else:
                            print(f"   ⚠️ Nút chưa hiện nhưng đã có trong code, dùng JS Click cưỡng chế...")
                            await nut_cai_dat_locator.evaluate("node => node.click()")
                        
                        # Đợi trang chuyển hướng
                        await asyncio.sleep(2.5) 
                        
                    except Exception as e:
                        print(f"   ⚠️ Bỏ qua hoặc đã cài đặt: {e}")
                # 7.2. GỌI HÀM ĐIỀN MẬT KHẨU
                # Điểm khác biệt: Bây giờ ta truyền thẳng TẤT CẢ 'cfg' vào, 
                # hàm bên actions.py sẽ tự biết bốc selector nào ra dùng.
                cai_dat_mat_khau_thanh_cong = await cai_dat_mat_khau_rut_tien(
                    page, 
                    mat_khau=user_data['pin_bank'],
                    cfg=cfg, # TRUYỀN CFG VÀO ĐÂY LÀ ĐỦ
                )
            
        await asyncio.sleep(1)

        # # ==========================================
        # # 8. BẤM VÀO THÊM TÀI KHOẢN (MỚI)
        # # ==========================================
        # if cai_dat_mat_khau_thanh_cong:
        #     update_status("Mở form thêm thẻ Ngân hàng...")
        #     print("\n--- BƯỚC 8: THÊM TÀI KHOẢN ---")
        #     await asyncio.sleep(1)
        #     da_bam_them = await bam_vao_them_tai_khoan(page, cfg.get("nut_them_tai_khoan"))


        # # ==========================================
        # # 9. CHỌN TÀI KHOẢN NGÂN HÀNG (MỚI)
        # # ==========================================
        # if da_bam_them:
        #     print("\n--- BƯỚC 9: THÊM TÀI KHOẢN NGÂN HÀNG ---")
        #     da_chon_loai = await tai_khoan_ngan_hang(page, cfg.get("nut_tai_khoan_ngan_hang"))
            
        # # ==========================================
        # # 10 XÁC MINH MẬT KHẨU (BƯỚC BẠN VỪA NÓI)
        # # ==========================================
        # if is_aborted and is_aborted(): return
        # if da_chon_loai:
        #     update_status("Xác minh MK trước khi thêm thẻ...")
        #     print("\n--- BƯỚC 10: NHẬP LẠI MẬT KHẨU RÚT TIỀN ---")
        #     da_xac_minh = await xac_minh_mat_khau_truoc_khi_them(
        #     page, 
        #     mat_khau=user_data['pin_bank'], 
        #     selector_o_nhap=cfg.get("o_nhap_pass_xac_minh"),
        #     selector_xac_nhan=cfg.get("nut_xac_nhan_verify")
        #     )     
                
        # # ==========================================
        # # 11 XÁC NHẬN TÀI KHOẢN NGÂN HÀNG (BƯỚC BẠN VỪA NÓI)
        # # ==========================================
        # if is_aborted and is_aborted(): return
        # if da_xac_minh:
        #     update_status("Đang nhập STK Ngân Hàng...")
        #     print("\n--- BƯỚC 11: ĐIỀN FORM NGÂN HÀNG ---")
        #     thanh_cong = await dien_thong_tin_ngan_hang(
        #         page, 
        #         so_tai_khoan=user_data['stk_bank'], 
        #         ten_ngan_hang=user_data['ten_bank'], 
        #         cfg=cfg
        #     )
            
        # if thanh_cong:
        #     print(f"✅ THÀNH CÔNG: Đã thêm thẻ {user_data['ten_bank']} cho acc này!")
        #     return True
        # ==========================================
        # 8, 9, 10: CÁC BƯỚC TRUNG GIAN (Chỉ chạy nếu có cấu hình)
        # ==========================================
        san_sang_dien_bank = False # Cờ xác nhận đã đến được form bank

        if cai_dat_mat_khau_thanh_cong:
            # KIỂM TRA: Nếu trang có nút "Thêm tài khoản" (kiểu c168)
            if cfg.get("nut_them_tai_khoan"):
                update_status("Mở form thêm thẻ Ngân hàng...")
                print("\n--- BƯỚC 8: THÊM TÀI KHOẢN (Kiểu c168) ---")
                da_bam_them = await bam_vao_them_tai_khoan(page, cfg.get("nut_them_tai_khoan"))
                
                if da_bam_them:
                    print("\n--- BƯỚC 9: CHỌN LOẠI THẺ ---")
                    da_chon_loai = await tai_khoan_ngan_hang(page, cfg.get("nut_tai_khoan_ngan_hang"))
                    
                    if da_chon_loai:
                        # Kiểm tra xem có cần xác minh mật khẩu lại không
                        if cfg.get("o_nhap_pass_xac_minh"):
                            print("\n--- BƯỚC 10: XÁC MINH MẬT KHẨU ---")
                            san_sang_dien_bank = await xac_minh_mat_khau_truoc_khi_them(
                                page, 
                                mat_khau=user_data['pin_bank'], 
                                selector_o_nhap=cfg.get("o_nhap_pass_xac_minh"),
                                selector_xac_nhan=cfg.get("nut_xac_nhan_verify")
                            )
                        else:
                            san_sang_dien_bank = True
            else:
                # Nếu KHÔNG CÓ nút "Thêm tài khoản" (kiểu hi144)
                print("\n⏩ Trang này vào thẳng Form Bank, bỏ qua bước 8, 9, 10.")
                san_sang_dien_bank = True

        # ==========================================
        # 11. XÁC NHẬN TÀI KHOẢN NGÂN HÀNG (DÙNG CHUNG)
        # ==========================================
        if is_aborted and is_aborted(): return
        if san_sang_dien_bank:
            update_status("Đang nhập STK Ngân Hàng...")
            print("\n--- BƯỚC 11: ĐIỀN FORM NGÂN HÀNG ---")

            # KIỂM TRA: Nếu có ô 'nhap_lai_pass' trong phần bank thì chạy luồng special
            if cfg.get("nhap_lai_pass"):
                from special_flows import flow_nhap_bank_78win
                thanh_cong = await flow_nhap_bank_78win(page, cfg, user_data)
            else:
                thanh_cong = await dien_thong_tin_ngan_hang(
                    page, 
                    so_tai_khoan=user_data['stk_bank'], 
                    ten_ngan_hang=user_data['ten_bank'], 
                    chi_nhanh=user_data.get('branch', 'Hà Nội'),
                    cfg=cfg
                )
            
            if thanh_cong:
                print(f"✅ THÀNH CÔNG: Đã thêm thẻ {user_data['ten_bank']}!")
                return True

        # ==========================================
        # KẾT THÚC LUỒNG
        # ==========================================
        print(f"🏆 HOÀN THÀNH TOÀN BỘ QUY TRÌNH CHO: {target_url}\n")
        
    except Exception as e:
        print(f"❌ Lỗi tổng thể tại {target_url}: {e}")