from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2


def get_center(dims):
    """Computes the coordinates of the center corner of a
rectangle. Assumes dims is a len 4 iterable (x, y, w, h) where (x, y)
is the defining corner and (w, h) are the width and height of
rectangle."""
    return dims[0] + int(dims[2]/2), dims[1] + int(dims[3]/2)


def get_opp(dims):
    """Computes the coordinates of the opposite corner of a
rectangle. Assumes dims is a len 4 iterable (x, y, w, h) where (x, y)
is the defining corner and (w, h) are the width and height of
rectangle."""
    return dims[0] + dims[2], dims[1] + dims[3]


x_res = 320
y_res = 249
camera = PiCamera()
camera.resolution = (x_res, y_res)
camera.framerate = 32
raw_capture = PiRGBArray(camera, size=(x_res, y_res))

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

time.sleep(0.1) # let camera warm up

for frame in camera.capture_continuous(raw_capture,
                                       format='bgr',
                                       use_video_port=True):
    image = frame.array
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for dims in faces:
        rect, center, opp = (dims[0], dims[1]), get_center(dims), get_opp(dims)
        cv2.rectangle(image, rect, opp, (255, 0, 0), 2)

    print("Faces: {}, X: {}, Y: {}".format(len(faces),
                                           center[0],
                                           center[1]))
    
    cv2.imshow('robot eye', image)
    key = cv2.waitKey(1) & 0xFF
    raw_capture.truncate(0)
    if key == ord('q'):
        break
    
cv2.destroyAllWindows
