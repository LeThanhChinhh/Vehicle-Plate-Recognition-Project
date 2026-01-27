import cv2

class CamService:
    def __init__(self, detector, db_manager=None):
        self.detector = detector
        self.db_manager = db_manager

    def process_cam_stream(self, cam_id=0, skip_frames=5):
        cap = cv2.VideoCapture(cam_id)
        frame_count = 0
        last_result = None

        while True:
            ret, frame = cap.read()
            if not ret: break

            frame = cv2.resize(frame, (800, 600))

            if frame_count % (skip_frames + 1) == 0:
                result = self.detector.detect_plate(frame)
                if result['has_plate']:
                    last_result = result
                    if self.db_manager:
                        pass

            if last_result and last_result['has_plate']:
                box = last_result['box']
                text = last_result['text']
                x1, y1, x2, y2 = map(int, box)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, text, (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            yield frame, last_result
            frame_count += 1
            
        cap.release()