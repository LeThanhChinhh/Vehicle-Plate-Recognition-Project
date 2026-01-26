import customtkinter as ctk
from PIL import Image, ImageTk
import cv2

def show_result_popup(parent, cv_crop_img, text_content):
    """
    Hiển thị cửa sổ popup chứa ảnh biển số đã cắt và text
    """
    if cv_crop_img is None or cv_crop_img.size == 0:
        return

    # Tạo cửa sổ con (Toplevel)
    window = ctk.CTkToplevel(parent)
    window.title("Chi tiết biển số")
    window.geometry("400x350")
    
    # Đảm bảo cửa sổ con nổi lên trên
    window.transient(parent) 
    window.grab_set() 

    # --- 1. Xử lý ảnh để hiển thị ---
    # Resize ảnh crop cho to lên để dễ nhìn (ví dụ width = 300)
    h, w, _ = cv_crop_img.shape
    target_w = 300
    ratio = target_w / w
    target_h = int(h * ratio)
    
    img_rgb = cv2.cvtColor(cv_crop_img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img_rgb)
    ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(target_w, target_h))

    # --- 2. Giao diện Popup ---
    lbl_img = ctk.CTkLabel(window, text="", image=ctk_img)
    lbl_img.pack(pady=20)
    
    lbl_text = ctk.CTkLabel(window, text=text_content, 
                            font=ctk.CTkFont(size=30, weight="bold"),
                            text_color="#E67E22")
    lbl_text.pack(pady=10)
    
    btn_close = ctk.CTkButton(window, text="Đóng", command=window.destroy)
    btn_close.pack(pady=10)