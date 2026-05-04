import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from SERVER_API.db import URI
from pymongo import MongoClient

WEB_CONFIG = {
    "f1686s.com": {
       "input_username": "input[data-input-name='account']",
        "input_password": "input[data-input-name='userpass']",
        "input_phone": "input[data-input-name='phone']",
        "cat_so_0": True,
        "input_realName": "input[data-input-name='realName']",
        "nut_dangky": "#insideRegisterSubmitClick",
       # Sửa lại phần Captcha theo ảnh mới nhất:
        "captcha_slider_btn": "div[class^='botion_btn']",     # Nút tròn màu xanh có mũi tên
        "captcha_bg_img": "div[class^='botion_bg']",             # Ảnh nền to có lỗ trống
        "captcha_slice_img": "div[class^='botion_slice_bg']",    # Mảnh ghép nhỏ
        "captcha_slice_img_tag": "div[class^='botion_slice_bg']", # Chính là thẻ này chứa background-image
        "nut_dong_popup": [".ui-dialog-close-box__icon", 
            ".ui-dialog-close",
            ".close-icon", 
            "[aria-label*='close' i]",
            "i[class*='close']",
            "span.web-push-tip-cancel",],
        "nut_toi": "span:text-is('Tôi')",
        "nut_rut_tien": "p:text-is('Rút Tiền')",
        "o_nhap_pass_rut": ".ui-password-input__security.hairline--surround",
        "nut_xacnhan_pass_rut": "button:has-text('Xác Nhận')",
        "nut_them_tai_khoan": "span:text-is('Thêm Tài Khoản')",
        "nut_tai_khoan_ngan_hang": "p:text-is('Tài khoản ngân hàng')",
        "o_nhap_pass_xac_minh": ".ui-password-input__security.hairline--surround", # Selector ô nhập pass hiện ra sau khi chọn Loại Ngân hàng
        "nut_xac_nhan_verify": "span:text-is('Tiếp Theo')",
        "input_stk": "input[placeholder*='Vui lòng nhập số tài khoản ngân hàng']", 
        "input_tim_ngan_hang": "input[placeholder*='Chọn ngân hàng phát hành']", # Đổi sang tìm ô Search
        "item_ngan_hang": ".ui-options__option",
        "nut_luu_ngan_hang": "button:has-text('Xác Nhận')"
    },
    "c168a.vip":{
        "input_username": "input[data-input-name='account']",
        "input_password": "input[data-input-name='userpass']",
        "input_phone": "input[data-input-name='phone']",
        "cat_so_0": True,
        "input_realName": "input[data-input-name='realName']",
        "nut_dangky": "#insideRegisterSubmitClick",
       # Sửa lại phần Captcha theo ảnh mới nhất:
        "captcha_slider_btn": "div[class^='botion_btn']",     # Nút tròn màu xanh có mũi tên
        "captcha_bg_img": "div[class^='botion_bg']",             # Ảnh nền to có lỗ trống
        "captcha_slice_img": "div[class^='botion_slice_bg']",    # Mảnh ghép nhỏ
        "captcha_slice_img_tag": "div[class^='botion_slice_bg']", # Chính là thẻ này chứa background-image
        "nut_dong_popup": [".ui-dialog-close-box__icon", 
            ".ui-dialog-close",
            ".close-icon", 
            "[aria-label*='close' i]",
            "i[class*='close']",
            "span.web-push-tip-cancel",],
        "nut_toi": "span:text-is('Tôi')",
        "nut_rut_tien": "p:text-is('Rút Tiền')",
        "o_nhap_pass_rut": ".ui-password-input__security.hairline--surround",
        "nut_xacnhan_pass_rut": "button:has-text('Xác Nhận')",
        "nut_them_tai_khoan": "span:text-is('Thêm Tài Khoản')",
        "nut_tai_khoan_ngan_hang": "p:text-is('Tài khoản ngân hàng')",
        "o_nhap_pass_xac_minh": ".ui-password-input__security.hairline--surround", # Selector ô nhập pass hiện ra sau khi chọn Loại Ngân hàng
        "nut_xac_nhan_verify": "span:text-is('Tiếp Theo')",
        "input_stk": "input[placeholder*='Vui lòng nhập số tài khoản ngân hàng']", 
        "input_tim_ngan_hang": "input[placeholder*='Chọn ngân hàng phát hành']", # Đổi sang tìm ô Search
        "item_ngan_hang": ".ui-options__option",
        "nut_luu_ngan_hang": "button:has-text('Xác Nhận')"
    },
    "m.sc8888.com":{
      "input_username": "input[data-input-name='account']",
        "input_password": "input[data-input-name='userpass']",
        "input_phone": "input[data-input-name='phone']",
        "cat_so_0": True,
        "input_realName": "input[data-input-name='realName']",
        "nut_dangky": "#insideRegisterSubmitClick",
       # Sửa lại phần Captcha theo ảnh mới nhất:
        "captcha_slider_btn": "div[class^='botion_btn']",     # Nút tròn màu xanh có mũi tên
        "captcha_bg_img": "div[class^='botion_bg']",             # Ảnh nền to có lỗ trống
        "captcha_slice_img": "div[class^='botion_slice_bg']",    # Mảnh ghép nhỏ
        "captcha_slice_img_tag": "div[class^='botion_slice_bg']", # Chính là thẻ này chứa background-image
        "nut_dong_popup": [".ui-dialog-close-box__icon", 
            ".ui-dialog-close",
            ".close-icon", 
            "[aria-label*='close' i]",
            "i[class*='close']",
            "span.web-push-tip-cancel",],
        "nut_toi": "span:text-is('Tôi')",
        "nut_rut_tien": "p:text-is('Rút Tiền')",
        "o_nhap_pass_rut": ".ui-password-input__security.hairline--surround",
        "nut_xacnhan_pass_rut": "button:has-text('Xác Nhận')",
        "nut_them_tai_khoan": "span:text-is('Thêm Tài Khoản')",
        "nut_tai_khoan_ngan_hang": "p:text-is('Tài khoản ngân hàng')",
        "o_nhap_pass_xac_minh": ".ui-password-input__security.hairline--surround", # Selector ô nhập pass hiện ra sau khi chọn Loại Ngân hàng
        "nut_xac_nhan_verify": "span:text-is('Tiếp Theo')",
        "input_stk": "input[placeholder*='Vui lòng nhập số tài khoản ngân hàng']", 
        "input_tim_ngan_hang": "input[placeholder*='Chọn ngân hàng phát hành']", # Đổi sang tìm ô Search
         "item_ngan_hang": ".ui-options__option",
        "nut_luu_ngan_hang": "button:has-text('Xác Nhận')"
    },
    "hi1444.com": {
        "input_username": "input[placeholder*='Vui lòng nhập tên tài khoản']",
        "input_password": "input[placeholder*='Vui lòng nhập mật khẩu']",
        "input_realName": "input[placeholder*='Họ và tên']",
        "input_phone": "input[placeholder*='Số điện thoại']",
        "cat_so_0": False,
        "input_captcha": "input[placeholder*='Vui lòng nhập mã xác minh']",
        "anh_captcha": "img.absolute.right-7.top-1",
        "nut_dangky": "span[translate='Login_RegisterBtn']",
        "xac_nhan":"button:has-text('xác nhận')",
        "nut_dong_popup": [".ui-dialog-close-box__icon", 
            ".ui-dialog-close",
            ".close-icon", 
            "[aria-label*='close' i]",
            "i[class*='close']", 
            "span:has-text('Đóng')",
            "i.fa-times-circle",                 # Bắt thẳng vào cái icon chữ X
            "button[ng-click*='$ctrl.ok']",      # Bắt vào sự kiện click tắt của Angular
            ".modal-content button.btn-link",
            "button:has-text('Đóng')",
            "button:has-text('Tôi Biết Rồi')",
        ],
        "nut_toi": "span:text-is('TÀI KHỎAN')",
        "nut_rut_tien": "a:has(span:has-text('Rút Tiền'))",
        "nut_cai_dat": "a:has(span:has-text('Mật khẩu rút tiền chưa cài đặt, vui lòng cài đặt mật khẩu rút tiền trước (chọn vào đây để cài đặt)'))",
        "o_nhap_pass_rut": "input[formcontrolname='newPassword']",
        "o_nhap_xac_nhan_pass_rut":"input[formcontrolname='confirm']",
        "nut_xacnhan_pass_rut": "span:has-text('Gửi đi')",
        "input_stk": "input[formcontrolname='account']", 
        "input_tim_ngan_hang": "mat-label:has-text('Vui lòng chọn ngân hàng')", # Đổi sang tìm ô Search
        "input_ten_ngan_hang": "input[placeholder*='Vui lòng chọn ngân hàng']",
        "item_ngan_hang": "mat-option",
        "chi_nhanh": "input[formcontrolname='city']",
        "nut_luu_ngan_hang": "button:has-text('Gửi đi')"
            
    },
    "www.qq8894.com": {
        "input_username": "input[placeholder*='Vui lòng nhập tên đăng nhập']",
        "input_password": "input[placeholder*='Vui lòng nhập mật khẩu đăng nhập']",
        "input_realName": "input[placeholder*='Vui lòng nhập họ và tên đầy đủ']",
        "input_phone": "input[placeholder*='Vui lòng nhập chính xác SĐT']",
        "cat_so_0": False,
        # "input_captcha": "input[placeholder*='Vui lòng nhập mã xác minh']",
        # "anh_captcha": "img.absolute.right-7.top-1",
        "nut_dangky": "button:has-text('ĐĂNG KÝ')",
        "nut_dong_popup": [".ui-dialog-close-box__icon", 
            ".ui-dialog-close",
            ".close-icon", 
            "[aria-label*='close' i]",
            "i[class*='close']", 
            "span:has-text('Đóng')",
            "i.fa-times-circle",
            "div.close-btn",
            "div.deposit-guide-close",                 # Bắt thẳng vào cái icon chữ X
            "button[ng-click*='$ctrl.ok']",      # Bắt vào sự kiện click tắt của Angular
            ".modal-content button.btn-link"],
        "nut_toi": "span:text-is('Tài Khoản')",
        "nut_rut_tien": "span:text-is('Rút Tiền')",
        "nut_cai_dat": "div.withdraw-bkdbtn",
        "o_nhap_pass_rut": "input[formcontrolname='newPassword']",
        "o_nhap_xac_nhan_pass_rut":"input[formcontrolname='confirm']",
        "nut_xacnhan_pass_rut": "span:has-text('Gửi đi')",
        "input_stk": "input[formcontrolname='account']", 
        "input_tim_ngan_hang": "mat-label:has-text('Vui lòng chọn ngân hàng')", # Đổi sang tìm ô Search
        "input_ten_ngan_hang": "input[placeholder*='Vui lòng chọn ngân hàng']",
        "item_ngan_hang": "mat-option",
        "chi_nhanh": "input[formcontrolname='city']",
        "nut_luu_ngan_hang": "button:has-text('Gửi đi')"
            
    },
    "m.new8826.xyz": {
        "input_username": "input[formcontrolname='account']",
        "input_password": "input[formcontrolname='password']",
        "input_realName": "input[formcontrolname*='name']",
        "input_phone": "input[formcontrolname*='mobile']",
        "cat_so_0": False,
        "nut_dangky": "button:has-text('ĐĂNG KÝ NGAY')",
        "nut_dong_popup": [".ui-dialog-close-box__icon", 
            ".ui-dialog-close",
            ".close-icon", 
            "[aria-label*='close' i]",
            "i[class*='close']", 
            "button:has-text('Đóng')",
            "mat-dialog-container span:has-text('x')",
            "mat-dialog-container span:has-text('X')",
            "i.fa-times-circle",                 # Bắt thẳng vào cái icon chữ X
            "button[ng-click*='$ctrl.ok']",      # Bắt vào sự kiện click tắt của Angular
            ".modal-content button.btn-link",
            "mat-dialog-container button:has-text('Đóng')",
            "button[translate='Common_Closed']",
            ".text-right.ng-star-inserted button",
            "button.mt-4.rounded-\\[4px\\]",
            "button:has-text('ĐÓNG')"
            ],
        "nut_toi": "span:text-is('Tài Khoản')",
        "nut_rut_tien": "a:has(span:has-text('Rút Tiền'))",
        "nut_cai_dat": "a:has(span:has-text('Mật khẩu rút tiền chưa cài đặt, vui lòng cài đặt mật khẩu rút tiền trước (chọn vào đây để cài đặt)'))",
        "o_nhap_pass_rut": "input[formcontrolname='newPassword']",
        "o_nhap_xac_nhan_pass_rut":"input[formcontrolname='confirm']",
        "nut_xacnhan_pass_rut": "span:has-text('Gửi đi')",
        "input_stk": "input[formcontrolname='account']", 
        "input_tim_ngan_hang": "mat-label:has-text('Vui lòng chọn ngân hàng')", # Đổi sang tìm ô Search
        "input_ten_ngan_hang": "input[placeholder*='Vui lòng chọn ngân hàng']",
        "item_ngan_hang": "mat-option",
        "chi_nhanh": "input[formcontrolname='city']",
        "nut_luu_ngan_hang": "button:has-text('Gửi đi')"
    },
    "m.f8betf.cool": {
        "input_username": "input[formcontrolname='account']",
        "input_password": "input[formcontrolname='password']",
        "input_realName": "input[formcontrolname*='name']",
        "input_phone": "input[formcontrolname*='mobile']",
        "cat_so_0": False,
        "nut_dangky": "button:has-text('ĐĂNG KÝ NGAY')",
        "nut_dong_popup": [".ui-dialog-close-box__icon", 
            ".ui-dialog-close",
            ".close-icon", 
            "[aria-label*='close' i]",
            "i[class*='close']", 
            "button:has-text('Đóng')",
            "mat-dialog-container span:has-text('x')",
            "mat-dialog-container span:has-text('X')",
            "i.fa-times-circle",                 # Bắt thẳng vào cái icon chữ X
            "button[ng-click*='$ctrl.ok']",      # Bắt vào sự kiện click tắt của Angular
            ".modal-content button.btn-link",
            "mat-dialog-container button:has-text('Đóng')",
            "button[translate='Common_Closed']",
            ".text-right.ng-star-inserted button",
            "button.mt-4.rounded-\\[4px\\]",
            "button:has-text('ĐÓNG')"
            ],
        "nut_toi": "span:text-is('Tài khoản')",
        "nut_rut_tien": "a:has(span:has-text('Rút Tiền'))",
        "nut_cai_dat": "a:has(span:has-text('Mật khẩu rút tiền chưa cài đặt, vui lòng cài đặt mật khẩu rút tiền trước (chọn vào đây để cài đặt)'))",
        "o_nhap_pass_rut": "input[formcontrolname='newPassword']",
        "o_nhap_xac_nhan_pass_rut":"input[formcontrolname='confirm']",
        "nut_xacnhan_pass_rut": "span:has-text('Gửi đi')",
        "input_stk": "input[formcontrolname='account']", 
        "input_tim_ngan_hang": "mat-label:has-text('Vui lòng chọn ngân hàng')", # Đổi sang tìm ô Search
        "input_ten_ngan_hang": "input[placeholder*='Vui lòng chọn ngân hàng']",
        "item_ngan_hang": "mat-option",
        "chi_nhanh": "input[formcontrolname='city']",
        "nut_luu_ngan_hang": "button:has-text('Gửi đi')"
    },
    "default": {
        "input_username": "input[type='text']",
        "input_password": "input[type='password']",
        "nut_dangky": "button"
    }
}

def day_du_lieu():
    client = MongoClient(URI)
    db = client["ToolAutoDB"]
    collection = db["Configs"]
    collection.delete_many({})
    collection.insert_one({"name": "main_web_config", "data": WEB_CONFIG})
    print("✅ Đã cập nhật Cấu hình Web lên MongoDB thành công!")

if __name__ == "__main__":
    day_du_lieu()