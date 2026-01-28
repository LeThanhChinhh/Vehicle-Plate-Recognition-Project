import cv2
import os

class VideoService:
    def __init__(self, detector):
        self.detector = detector
        
        self.best_result = None
        # Đếm số frame mất dấu liên tiếp
        self.missing_count = 0
        self.RESET_THRESHOLD = 20

    def process_video_stream(self, video_path, skip_frames=3):
        if not os.path.exists(video_path):
            print(f"Lỗi: Không tìm thấy video tại {video_path}")
            return

        cap = cv2.VideoCapture(video_path)
        frame_count = 0

        global_best_result = None
        global_best_frame = None

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Resize
            h, w = frame.shape[:2]
            if w > 800:
                frame = cv2.resize(frame, (800, int(h * 800/w)))

            # Logic dectect 
            if frame_count % (skip_frames + 1) == 0:
                current_result = self.detector.detect_plate(frame)

                if current_result['has_plate']:
                    # Cập nhật session
                    self.missing_count = 0
                    if self.best_result is None:
                        self.best_result = current_result
                    else:
                        if current_result['conf'] > self.best_result['conf']:
                            self.best_result = current_result
                        else:
                            # Cập nhật text
                            current_result['text'] = self.best_result['text']
                            current_result['conf'] = self.best_result['conf']
                            self.best_result = current_result

                    # lưu lại độ tin cậy cao nhất video
                    if global_best_result is None or current_result['conf'] > global_best_result['conf']:
                        global_best_result = current_result
                        global_best_frame = frame.copy() # Phải copy frame gốc để lưu trữ

                        self._draw_on_frame(global_best_frame, global_best_result)

                else:
                    self.missing_count += 1
            
            # Reset Session nếu mất dấu quá lâu
            if self.missing_count > self.RESET_THRESHOLD:
                self.best_result = None
                self.missing_count = 0

            # Trả frame hiện tại
            if self.best_result and self.best_result['has_plate']:
                self._draw_on_frame(frame, self.best_result)

            yield frame, self.best_result
            frame_count += 1

        cap.release()
        
        # kết thúc video
        # Trả về kết quả tốt nhất toàn video
        if global_best_result is not None and global_best_frame is not None:
            final_text = global_best_result['text']
            final_conf = global_best_result['conf']
            
            print(f"\n[INFO] HOÀN THÀNH VIDEO. KẾT QUẢ TỐT NHẤT: {final_text} (Conf: {final_conf})")
            
            # Yield lần cuối cùng
            yield global_best_frame, global_best_result

    def _draw_on_frame(self, frame, result):
        if not result or 'box' not in result:
            return
        box = result['box']
        text = result['text']
        conf = result['conf']
        x1, y1, x2, y2 = map(int, box)
        
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        label = f"{text} ({conf:.2f})"
        (w_text, h_text), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        cv2.rectangle(frame, (x1, y1 - 30), (x1 + w_text, y1), (0, 255, 0), -1)
        
        # Vẽ chữ
        cv2.putText(frame, label, (x1, y1 - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)