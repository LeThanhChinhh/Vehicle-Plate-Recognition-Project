import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2

from core.detector import LicensePlateDetector
from core.service.video_service import VideoService

try:
    from gui.windows import show_result_popup
except ImportError:
    def show_result_popup(root, crop, text):
        pass

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class LicensePlateApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Cấu hình cửa sổ
        self.title("HỆ THỐNG NHẬN DIỆN BIỂN SỐ XE - AI PRO")
        self.geometry("1280x760")
        
        # Khởi tạo Service
        print("⏳ Đang khởi tạo Service...")
        detector = LicensePlateDetector()
        self.service = VideoService(detector) 

        # Biến trạng thái
        self.current_image_cv2 = None
        self.cap = None
        self.is_streaming = False
        self.after_id = None
        
        # Dựng Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.setup_sidebar()
        self.setup_main_area()
        self.change_mode("Image")

    def setup_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="AI LICENSE\nPLATE DETECTOR", 
                                       font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=20)

        self.mode_selector = ctk.CTkSegmentedButton(self.sidebar_frame, 
                                                    values=["Image", "Video", "Camera"],
                                                    command=self.change_mode)
        self.mode_selector.set("Image")
        self.mode_selector.grid(row=1, column=0, padx=20, pady=(10, 20))

        self.btn_source = ctk.CTkButton(self.sidebar_frame, text="📂 Chọn Ảnh", height=40, 
                                        fg_color="#3B8ED0", hover_color="#36719F",
                                        command=self.handle_source)
        self.btn_source.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.btn_stop = ctk.CTkButton(self.sidebar_frame, text="⏹ Dừng Phát", height=40,
                                      fg_color="#E74C3C", hover_color="#C0392B",
                                      state="disabled", command=self.stop_stream)
        self.btn_stop.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        ctk.CTkFrame(self.sidebar_frame, height=2, fg_color="gray30").grid(row=4, column=0, sticky="ew", padx=20, pady=20)

        self.btn_detect = ctk.CTkButton(self.sidebar_frame, text="🔍 QUÉT ẢNH NÀY", height=50,
                                        font=ctk.CTkFont(size=16, weight="bold"),
                                        fg_color="#E67E22", hover_color="#D35400",
                                        command=self.run_process_image_mode)
        self.btn_detect.grid(row=5, column=0, padx=20, pady=10, sticky="ew")

        self.lbl_result = ctk.CTkLabel(self.sidebar_frame, text="---", 
                                       font=ctk.CTkFont(size=24, weight="bold"),
                                       text_color="#2ECC71")
        self.lbl_result.grid(row=7, column=0, padx=20, pady=20, sticky="n")

    def setup_main_area(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#1a1a1a")
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        self.video_label = ctk.CTkLabel(self.main_frame, text="Vui lòng chọn nguồn dữ liệu...", font=("Arial", 16))
        self.video_label.pack(fill="both", expand=True, padx=10, pady=10)

    # logic điều khiển

    def change_mode(self, value):
        self.stop_stream()
        self.lbl_result.configure(text="---")
        
        if value == "Image":
            self.btn_source.configure(text="📂 Chọn File Ảnh", state="normal")
            self.btn_stop.configure(state="disabled")
            self.btn_detect.configure(state="normal", text="🔍 QUÉT ẢNH NÀY")
        elif value == "Video":
            self.btn_source.configure(text="🎞️ Chọn File Video", state="normal")
            self.btn_stop.configure(state="disabled")
            self.btn_detect.configure(state="disabled", text="⚡ ĐANG QUÉT TỰ ĐỘNG")
        elif value == "Camera":
            self.btn_source.configure(text="📹 Bật Camera", state="normal")
            self.btn_stop.configure(state="disabled")
            self.btn_detect.configure(state="disabled", text="⚡ ĐANG QUÉT TỰ ĐỘNG")

    def handle_source(self):
        mode = self.mode_selector.get()
        if mode == "Image":
            path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png *.jpeg")])
            if path:
                self.current_image_cv2 = cv2.imread(path)
                self.display_image(self.current_image_cv2)
        elif mode == "Video":
            path = filedialog.askopenfilename(filetypes=[("Videos", "*.mp4 *.avi *.mkv")])
            if path:
                self.start_stream(path)
        elif mode == "Camera":
            self.start_stream(0)

    def start_stream(self, source):
        self.stop_stream()
        self.cap = cv2.VideoCapture(source)
        if not self.cap.isOpened():
            messagebox.showerror("Lỗi", "Không thể mở nguồn phát!")
            return
        
        self.is_streaming = True
        self.btn_source.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        
        # reset trạng thái
        if hasattr(self.service, 'reset'):
            self.service.reset()
        
        self.video_loop()

    def stop_stream(self):
        self.is_streaming = False
        if self.cap:
            self.cap.release()
            self.cap = None
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None
        self.btn_stop.configure(state="disabled")
        self.btn_source.configure(state="normal")
        self.video_label.configure(image=None, text="Đã dừng phát.")

    # Logic gọi service (video)
    def video_loop(self):
        if self.is_streaming and self.cap:
            ret, frame = self.cap.read()
            if not ret:
                self.stop_stream()
                return

            # GỌI SERVICE ĐỂ XỬ LÝ FRAME
            processed_frame, text_result, _ = self.service.process_frame(frame)
            
            # Cập nhật UI Label
            if text_result:
                self.lbl_result.configure(text=text_result)
            
            # Hiển thị ảnh (dùng hàm đã fix resize)
            self.display_image(processed_frame)
            
            # Loop
            self.after_id = self.after(30, self.video_loop)

    # Logic gọi service (image)
    def run_process_image_mode(self):
        if self.current_image_cv2 is None:
            return

        # Gọi Service để xử lý ảnh
        processed_frame, result = self.service.process_static_image(self.current_image_cv2)
        
        # Hiển thị ảnh kết quả lên màn hình chính
        self.display_image(processed_frame)

        # Xử lý kết quả phụ (Text, Popup)
        if result and result.get('has_plate'):
            text = result['text']
            self.lbl_result.configure(text=text.replace('\n', ' - '))
            
            box_key = 'box_expanded' if 'box_expanded' in result else 'box'
            if box_key in result:
                x1, y1, x2, y2 = map(int, result[box_key])
                
                # Ensure coordinates are within image bounds for cropping
                h_img, w_img = self.current_image_cv2.shape[:2]
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w_img, x2), min(h_img, y2)
                
                plate_crop = self.current_image_cv2[y1:y2, x1:x2]
                show_result_popup(self, plate_crop, text)
        else:
            self.lbl_result.configure(text="Không tìm thấy")

    # hàm hiển thị ảnh với resize fit center
    def display_image(self, cv_img):
        if cv_img is None: return
        try:
            if not self.winfo_exists(): return
        except: return

        # lấy kích thước
        h, w, _ = cv_img.shape
        c_w = self.main_frame.winfo_width() - 20
        c_h = self.main_frame.winfo_height() - 20
        if c_w < 50 or c_h < 50: c_w, c_h = 800, 600

        # tính toán tỷ lệ Fit Center (Không zoom vỡ hình)
        ratio = min(c_w / w, c_h / h)
        new_w = int(w * ratio)
        new_h = int(h * ratio)
        
        # convert & Resize
        img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)
        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(new_w, new_h))
        
        # hiển thị & Neo biến ảnh
        self.video_label.configure(image=ctk_img, text="")
        self.video_label.image = ctk_img