# --- TRONG FILE: flows.py ---
import asyncio
from CLIENT_TOOL.actions import bam_nut_dang_ky, don_dep_popup, kiem_tra_va_cho_captcha, bam_vao_tab_toi, bam_vao_rut_tien, cai_dat_mat_khau_rut_tien, tai_khoan_ngan_hang, xac_minh_mat_khau_truoc_khi_them, dien_thong_tin_ngan_hang, xu_ly_captcha, giai_captcha_keo_opencv, bam_vao_them_tai_khoan

async def run_full_flow(page, target_url, user_data, cfg):
    try:

        print(f"🚀 Bắt đầu chạy: {target_url}")
        await page.goto(target_url, timeout=30000)
        await page.wait_for_selector(cfg["input_username"], timeout=15000)

        # ==========================================
        # DỌN POPUP
        # ========================================== 
        # await don_dep_popup(page, cfg.get("nut_dong_popup"))
        # await asyncio.sleep(1)
        
        # ==========================================
        # 1. NHẬP THÔNG TIN TÀI KHOẢN
        # ==========================================
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

        await xu_ly_captcha(page, cfg)
            
        # ==========================================
        # 2. GỌI HÀM BẤM NÚT ĐĂNG KÝ
        # ==========================================
        print("\n--- BẮT ĐẦU QUÁ TRÌNH BẤM ĐĂNG KÝ ---")
        thanh_cong = await bam_nut_dang_ky(page, cfg["nut_dangky"])
        
        if not thanh_cong:
            return 
            
        # 3. CHỐT CHẶN CAPTCHA (ĐÃ SỬA LOGIC)
        # ==========================================
        
        # 3.1. Nếu là Captcha kéo (Slide)
        if cfg.get("captcha_slider_btn"):
            max_retries = 3
            da_thanh_cong = False

            for i in range(max_retries):
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

        # 3.2. Nếu là Captcha chữ/số (OCR) - giữ nguyên
        if cfg.get("input_captcha"):
            tiep_tuc = await kiem_tra_va_cho_captcha(page) 
            if not tiep_tuc:
               return 
        # ==========================================
        # 4. GỌI HÀM QUÉT POPUP
        # ==========================================
        # Sau khi giải captcha xong, web mới hiện Popup thành công hoặc thông báo
        await don_dep_popup(page, cfg.get("nut_dong_popup"))
        await asyncio.sleep(1)
        

        # ==========================================
        # 5. TỰ ĐỘNG BẤM VÀO TAB "TÔI"
        # ==========================================
        print("\n--- BƯỚC CUỐI: KIỂM TRA TÀI KHOẢN ---")
        # Truyền cấu hình từ cfg vào hàm
        vao_toi_thanh_cong = await bam_vao_tab_toi(page, cfg.get("nut_toi"))
        await asyncio.sleep(1)
        

        # ==========================================
        # 6. TỰ ĐỘNG BẤM "RÚT TIỀN" (MỚI THÊM)
        # ==========================================
        if vao_toi_thanh_cong:
            print("\n--- BƯỚC 6: VÀO MỤC RÚT TIỀN ---")
            vao_rut_tien_thanh_cong = await bam_vao_rut_tien(page, cfg.get("nut_rut_tien"))
            # Nghỉ 2s để nhìn thấy form Rút tiền hiện ra
            await asyncio.sleep(1)
        
        # ==========================================
        # 7. CÀI ĐẶT MẬT KHẨU RÚT TIỀN (MỚI)
        # ==========================================
        if vao_rut_tien_thanh_cong:
            print("\n--- BƯỚC 7: CÀI ĐẶT MẬT KHẨU RÚT TIỀN ---")
            cai_dat_mat_khau_thanh_cong = await cai_dat_mat_khau_rut_tien(
                page, 
                mat_khau=user_data['pin_bank'], # Bạn có thể đổi MK ở đây
                selector_o_nhap=cfg.get("o_nhap_pass_rut"),
                selector_xac_nhan=cfg.get("nut_xacnhan_pass_rut")
            )
        await asyncio.sleep(1)

        # ==========================================
        # 8. BẤM VÀO THÊM TÀI KHOẢN (MỚI)
        # ==========================================
        if cai_dat_mat_khau_thanh_cong:
            print("\n--- BƯỚC 8: THÊM TÀI KHOẢN ---")
            await asyncio.sleep(1)
            da_bam_them = await bam_vao_them_tai_khoan(page, cfg.get("nut_them_tai_khoan"))


        # ==========================================
        # 9. CHỌN TÀI KHOẢN NGÂN HÀNG (MỚI)
        # ==========================================
        if da_bam_them:
            print("\n--- BƯỚC 9: THÊM TÀI KHOẢN NGÂN HÀNG ---")
            da_chon_loai = await tai_khoan_ngan_hang(page, cfg.get("nut_tai_khoan_ngan_hang"))
            
        # ==========================================
        # 10 XÁC MINH MẬT KHẨU (BƯỚC BẠN VỪA NÓI)
        # ==========================================
        if da_chon_loai:
            print("\n--- BƯỚC 10: NHẬP LẠI MẬT KHẨU RÚT TIỀN ---")
            da_xac_minh = await xac_minh_mat_khau_truoc_khi_them(
            page, 
            mat_khau=user_data['pin_bank'], 
            selector_o_nhap=cfg.get("o_nhap_pass_xac_minh"),
            selector_xac_nhan=cfg.get("nut_xac_nhan_verify")
            )     
                
        # ==========================================
        # 11 XÁC NHẬN TÀI KHOẢN NGÂN HÀNG (BƯỚC BẠN VỪA NÓI)
        # ==========================================
        if da_xac_minh:
            print("\n--- BƯỚC 11: ĐIỀN FORM NGÂN HÀNG ---")
            thanh_cong = await dien_thong_tin_ngan_hang(
                page, 
                so_tai_khoan=user_data['stk_bank'], 
                ten_ngan_hang=user_data['ten_bank'], 
                cfg=cfg
            )
            
        if thanh_cong:
            print(f"✅ THÀNH CÔNG: Đã thêm thẻ {user_data['ten_bank']} cho acc này!")
            return True

        # ==========================================
        # KẾT THÚC LUỒNG
        # ==========================================
        print(f"🏆 HOÀN THÀNH TOÀN BỘ QUY TRÌNH CHO: {target_url}\n")
        
    except Exception as e:
        print(f"❌ Lỗi tổng thể tại {target_url}: {e}")