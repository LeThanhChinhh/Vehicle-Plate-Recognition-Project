import cv2

class CamService:
    def __init__(self, detector):
        self.detector = detector

    def process_cam_stream(self, cam_id=0, skip_frames=5):
        # 1. MO KET NOI CAMERA, SO 0 LA WEBCAM MAY TINH 
        cap = cv2.VideoCapture(cam_id)
        
        if not cap.isOpened():
            print(f"Không mở được Camera ")
            return

        print(f"Camera đang chạy...")
        frame_count = 0
        

        last_result = None 

        while True:

            ret, frame = cap.read()
            if not ret:
                print("Mất tín hiệu Camera hoặc đã kết thúc.")
                break

            frame = cv2.resize(frame, (800, 600))

            if frame_count % (skip_frames + 1) == 0:
                last_result = self.detector.detect_plate(frame)
            
            if last_result and last_result['has_plate']:
                box = last_result['box']
                text = last_result['text']
                conf = last_result['conf']
                
                # VE KHUNG HINH CHU NHAT
                x1, y1, x2, y2 = map(int, box)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # VIET CHU BIEN SO
                label = f"{text} ({conf})"
                cv2.putText(frame, label, (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            yield frame
            
            frame_count += 1

        cap.release()
