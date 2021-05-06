# MIT License
# Copyright (c) 2019,2020 JetsonHacks
# See license in root folder
# CSI_Camera is a class which encapsulates an OpenCV VideoCapture element
# The VideoCapture element is initialized via a GStreamer pipeline
# The camera is read in a separate thread 
# The class also tracks how many frames are read from the camera;
# The calling application tracks the frames_displayed

# Let's use a repeating Timer for counting FPS
import cv2
import threading
from utils.parameters import *

class RepeatTimer(threading.Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

class CSI_Camera:

    def __init__ (self) :
        # Initialize instance variables
        # OpenCV video capture element
        self.video_capture = None
        # The last captured image from the camera
        self.frame = None
        self.grabbed = False
        # The thread where the video capture runs
        self.read_thread = None
        self.read_lock = threading.Lock()
        self.running = False

        # The parameter for reading fps
        self.fps_timer=None
        self.frames_read=0
        self.frames_displayed=0
        self.last_frames_read=0
        self.last_frames_displayed=0

    def open(self):
        try:
            # Jetson
            self.video_capture = cv2.VideoCapture(
                self.create_gstreamer_pipeline(), cv2.CAP_GSTREAMER
            )

            # Macos
            # self.video_capture = cv2.VideoCapture(0)
            
        except RuntimeError:
            self.video_capture = None
            print("Unable to open camera")
            print("Pipeline: " + gstreamer_pipeline_string)
            return
        # Grab the first frame to start the video capturing
        self.grabbed, self.frame = self.video_capture.read()

    def start(self):
        if self.running:
            print('Video capturing is already running')
            return None

        # create a thread to read the camera image
        if self.video_capture != None:
            self.running=True
            self.read_thread = threading.Thread(target=self.updateCamera)
            self.read_thread.start()
        return self

    def updateCamera(self):
        # This is the thread to read images from the camera
        while self.running:
            try:
                grabbed, frame = self.video_capture.read()
                with self.read_lock:
                    self.grabbed=grabbed
                    self.frame=frame
                    self.frames_read += 1
            except RuntimeError:
                print("Could not read image from camera")
        # FIX ME - stop and cleanup thread
        # Something bad happened
        
    def read(self):
        with self.read_lock:
            # Jetson
            # frame = self.frame.copy()
            # Macos
            frame = self.frame
            
            grabbed=self.grabbed
        return grabbed, frame

    def update_fps_stats(self):
        self.last_frames_read=self.frames_read
        self.last_frames_displayed=self.frames_displayed
        # Start the next measurement cycle
        self.frames_read=0
        self.frames_displayed=0

    def start_counting_fps(self):
        self.fps_timer=RepeatTimer(1.0,self.update_fps_stats)
        self.fps_timer.start()

    def stop(self):
        self.running=False
        self.read_thread.join()

    def release(self):
        if self.video_capture != None:
            self.video_capture.release()
            self.video_capture = None
                # Now kill the thread
        if self.read_thread != None:
            self.read_thread.join()

        if show_fps:
            # Kill the timer
            self.fps_timer.cancel()
            self.fps_timer.join()

    @property
    def gstreamer_pipeline(self):
        return self._gstreamer_pipeline

    # Currently there are setting frame rate on CSI Camera on Nano through gstreamer
    # Here we directly select sensor_mode 3 (1280x720, 59.9999 fps)
    def create_gstreamer_pipeline(
        self,
        capture_width = 1920,
        capture_height = 1080,
        display_width=1920,
        display_height=1080,
        framerate=23,
        flip_method = 2
    ):

        return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height
        )
    )


    
