import cv2

class VideoService:
    def __init__(self, detector):
        self.detector = detector
        self.last_result = None
        self.frame_count = 0

    def reset(self):
        self.last_result = None
        self.frame_count = 0

    def process_frame(self, frame):
        if frame is None:
            return None, None, None

        self.frame_count += 1
        
        # --- 1. LOGIC FRAME SKIPPING (Chạy AI mỗi 3 frame) ---
        if self.frame_count % 3 == 0:
            result = self.detector.detect_plate(frame)
            if result and result['has_plate']:
                self.last_result = result
        
        # --- 2. VẼ KẾT QUẢ ---
        processed_frame = frame.copy()
        text_display = ""
        
        if self.last_result:
            # Gọi hàm vẽ (đã bao gồm logic mở rộng khung)
            processed_frame = self.draw_result(processed_frame, self.last_result)
            text_display = self.last_result['text'].replace('\n', ' - ')
            
        return processed_frame, text_display, self.last_result

    def process_static_image(self, image):
        if image is None: return None, None
        
        result = self.detector.detect_plate(image)
        processed_frame = image.copy()
        
        if result and result['has_plate']:
            # Vẽ và tính toán box mở rộng
            processed_frame = self.draw_result(processed_frame, result)
            return processed_frame, result
            
        return processed_frame, None

    def draw_result(self, img, result):
        box = result['box']
        text = result['text']
        x1, y1, x2, y2 = map(int, box)
        h_img, w_img = img.shape[:2]

        #  CẤU HÌNH PADDING
        padding_x = 15
        padding_y = 60

        # Tính toán tọa độ mới
        x1 = max(0, x1 - padding_x)
        y1 = max(0, y1 - padding_y)
        x2 = min(w_img, x2 + padding_x)
        y2 = min(h_img, y2 + padding_y)

        # Lưu box đã mở rộng ngược lại vào result
        result['box_expanded'] = [x1, y1, x2, y2]

        # Vẽ khung chữ nhật
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Vẽ chữ 
        lines = text.split('\n')
        # Tính vị trí vẽ chữ dựa trên số dòng
        start_y = y1 - 25 - (len(lines)-1)*30
        if start_y < 10: start_y = y2 + 25

        for i, line in enumerate(lines):
            y_line = start_y + (i * 35)
            (w, h), _ = cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            
            # Vẽ nền đen cho chữ
            cv2.rectangle(img, (x1, y_line - h - 8), (x1 + w, y_line + 6), (0, 0, 0), -1)
            # Vẽ chữ trắng
            cv2.putText(img, line, (x1, y_line), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
        return img