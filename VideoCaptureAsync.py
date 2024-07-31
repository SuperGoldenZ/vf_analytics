import cv2
import threading
import queue

class VideoCaptureAsync:
    def __init__(self, src, queue_size=1024):
        self.src = src
        self.cap = cv2.VideoCapture(self.src)
        self.queue = queue.Queue(maxsize=queue_size)
        #self.queue_480 = queue.Queue(maxsize=queue_size)

        self.thread = threading.Thread(target=self._reader)
        self.thread.daemon = True
        self.thread.start()

    def get_frame_rate(self):
        return self.cap.get(cv2.CAP_PROP_FPS)

    def get_frame_count(self):
        return int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def _reader(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                self.queue.put(None)
                break

            #height, width, _ = frame.shape  # Get the dimensions of the frame
            #if (height != 480):
                #frame = (cv2.resize(frame, (854, 480)))

            self.queue.put(frame)

            #else:
                #self.queue_480.put(frame)


    def read(self):
        return self.queue.get()

    #def read_480(self):
        #return self.queue_480.get()

    def release(self):
        self.cap.release()