import cv2
import os
from datetime import datetime

class ImageService:
    def __init__(self, detector, db_manager=None): # <--- [NEW] Thêm db_manager
        self.detector = detector 
        self.db_manager = db_manager # <--- [NEW]
        
        # [NEW] Tạo thư mục lưu ảnh
        self.save_folder = "captured_images"
        os.makedirs(self.save_folder, exist_ok=True)

    def process_image(self, file_path):
        if not os.path.exists(file_path):
            print(f"Không tìm thấy file {file_path}")
            return None, None

        # doc anh
        img = cv2.imread(file_path)
        
        if img is None:
            print("File không phải là ảnh hoặc bị hỏng.")
            return None, None

        # goi detector de phat hien bien so va doc bien so
        result = self.detector.detect_plate(img)

        # neu tim thay bien so thi moi thuc hien ve len anh
        if result['has_plate']:
            box = result['box']   
            text = result['text'] 
            conf = result['conf'] 
            
            # ve khung chu nhat
            x1, y1, x2, y2 = map(int, box)
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # gan label cho anh bien so
            label = f"{text} ({conf})"
            
            # tinh vi tri dat text
            text_x = x1
            text_y = y1 - 10 if y1 - 10 > 10 else y1 + 20
            cv2.putText(img, label, (text_x, text_y), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            # --- [NEW] LƯU VÀO DATABASE ---
            if self.db_manager:
                self.save_to_database(img, result)

        return img, result

    # --- [NEW] HÀM LƯU DB ---
    def save_to_database(self, img, result):
        try:
            plate_text = result['text']
            conf = result['conf']
            
            # 1. Lưu ảnh ra folder
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"IMG_{timestamp}_{plate_text}.jpg"
            save_path = os.path.join(self.save_folder, filename)
            cv2.imwrite(save_path, img)
            
            # 2. Lưu thông tin vào SQLite
            self.db_manager.save_plate(plate_text, save_path, conf)
            print(f"💾 [IMAGE] Đã lưu DB: {plate_text}")
        except Exception as e:
            print(f"⚠️ Lỗi lưu Image DB: {e}")