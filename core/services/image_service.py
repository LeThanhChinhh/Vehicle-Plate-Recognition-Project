import cv2
import os

class ImageService:
    def __init__(self, detector):
        self.detector = detector 

    def process_image(self, file_path):
        if not os.path.exists(file_path):
            print(f"Không tìm thấy file {file_path}")
            return None, None

        #doc anh
        img = cv2.imread(file_path)
        
        if img is None:
            print("File không phải là ảnh hoặc bị hỏng.")
            return None, None

        #goi detector de phat hien bien so va doc bien so
        result = self.detector.detect_plate(img)

        #neu tim thay bien so thi moi thuc hien ve len anh
        if result['has_plate']:
            box = result['box']   
            text = result['text'] 
            conf = result['conf'] 
            
            #ve khung chu nhat
            x1, y1, x2, y2 = map(int, box)
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            #gan label cho anh bien so
            label = f"{text} ({conf})"
            
            #tinh vi tri dat text de no nam ben tren khung chu nhat
            text_x = x1
            text_y = y1 - 10 if y1 - 10 > 10 else y1 + 20
            
            cv2.putText(img, label, (text_x, text_y), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            #log console
            print(f"Đã tìm thấy: {label}")
        else:
            print("Không tìm thấy biển số nào trong ảnh này.")
        return img, result