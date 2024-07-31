import cv2
import threading
import queue

class VideoCaptureAsync:
    def __init__(self, src, queue_size=2048):
        self.src = src
        self.cap = cv2.VideoCapture(self.src)
        self.queue = queue.Queue(maxsize=queue_size)
        self.done = False

        self.thread = threading.Thread(target=self._reader)
        self.thread.daemon = True
        self.thread.start()

    def get_frame_rate(self):
        return self.cap.get(cv2.CAP_PROP_FPS)

    def get_frame_count(self):
        return int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def _reader(self):
        while not self.done:
            ret, frame = self.cap.read()
            if not ret:
                self.queue.put(None)
                break

            self.queue.put(frame)

    def read(self):
        return self.queue.get()

    def release(self):
        self.done = True
        self.thread.join()
        self.cap.release()