"""This module provides classes to extract information from VF5es videos"""

import threading
import queue
import time

import cv2
from line_profiler import profile


class VideoCaptureAsync:
    """Read a video and convert into images async"""

    def __init__(self, src, queue_size=1028 * 4):
        self.src = src
        self.cap = cv2.VideoCapture(self.src)
        # self.cap = cv2.VideoCapture(self.src, cv2.CAP_FFMPEG)
        # self.cap.set(cv2.CAP_PROP_HW_ACCELERATION, cv2.VIDEO_ACCELERATION_ANY)

        # Check if the property was set
        if not self.cap.isOpened():
            print("Failed to open video with hardware acceleration.")
            print(cv2.getBuildInformation())

        self.queue = queue.Queue(maxsize=queue_size)
        self.done = False
        self.frames_read = 0
        self.thread = threading.Thread(target=self._reader)
        self.thread.daemon = True
        self.thread.start()

    def get_frame_rate(self):
        return self.cap.get(cv2.CAP_PROP_FPS)

    def get_frame_count(self):
        return int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    @profile
    def _reader(self):
        while not self.done:
            ret, frame = self.cap.read()
            if not ret:
                self.queue.put(None)
                break

            while self.queue.qsize() >= self.queue.maxsize - 8:
                time.sleep(1)

            self.queue.put(frame, timeout=3)

    @profile
    def read(self):
        result = self.queue.get(timeout=10)
        self.frames_read += 1
        return result

    def release(self):
        self.done = True
        self.thread.join()
        self.cap.release()
