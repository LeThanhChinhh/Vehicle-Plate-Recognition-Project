import cv2

class CamService:
    def __init__(self, detector):
        """
        Khởi tạo dịch vụ Camera.
        Input: detector (Bộ não AI đã load model)
        """
        self.detector = detector

    def process_cam_stream(self, cam_id=0, skip_frames=5):
        """
        Hàm xử lý luồng Camera.
        Input: 
            - cam_id: 0 là webcam máy tính, hoặc đường dẫn IP Camera
            - skip_frames: Số frame bỏ qua không detect (để giảm lag)
        Output: 
            - Yield ra từng frame đã vẽ khung để hiển thị
        """
        # 1. Mở kết nối Camera
        cap = cv2.VideoCapture(cam_id)
        
        if not cap.isOpened():
            print(f"❌ Lỗi: Không mở được Camera ID {cam_id}")
            return

        print(f"📷 Camera {cam_id} đang chạy...")
        frame_count = 0
        

        last_result = None 

        while True:

            ret, frame = cap.read()
            if not ret:
                print("⚠️ Mất tín hiệu Camera hoặc đã kết thúc.")
                break

            frame = cv2.resize(frame, (800, 600))

            if frame_count % (skip_frames + 1) == 0:
                last_result = self.detector.detect_plate(frame)
            
            if last_result and last_result['has_plate']:
                box = last_result['box']
                text = last_result['text']
                conf = last_result['conf']
                
                # Vẽ khung chữ nhật
                x1, y1, x2, y2 = map(int, box)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Viết chữ biển số
                label = f"{text} ({conf})"
                cv2.putText(frame, label, (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            yield frame
            
            frame_count += 1

        cap.release()