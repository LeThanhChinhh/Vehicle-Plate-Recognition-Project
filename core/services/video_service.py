import cv2
import os

class VideoService:
    def __init__(self, detector):
        self.detector = detector

    def process_video_stream(self, video_path, skip_frames=3):
        if not os.path.exists(video_path):
            print(f"Lỗi: Không tìm thấy video tại {video_path}")
            return

        cap = cv2.VideoCapture(video_path)
        frame_count = 0
        last_result = None

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Resize về 800px chiều ngang cho nhẹ
            h, w = frame.shape[:2]
            if w > 800:
                frame = cv2.resize(frame, (800, int(h * 800/w)))

            # Logic Detect
            if frame_count % (skip_frames + 1) == 0:
                result = self.detector.detect_plate(frame)
                if result['has_plate']:
                    last_result = result
            
            # Logic Vẽ lên frame
            if last_result and last_result['has_plate']:
                box = last_result['box']
                text = last_result['text']
                conf = last_result['conf']
                
                x1, y1, x2, y2 = map(int, box)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{text} ({conf})", (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Trả hàng (Yield) frame và kết quả
            yield frame, last_result
            
            frame_count += 1

        cap.release()