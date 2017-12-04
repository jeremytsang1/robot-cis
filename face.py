from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
from config import config_pi_camera


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


def find_face():
    count_up = 0
    timeout = 5  # allow 5 seconds of not finding faces before rescanning
    x_res = config_pi_camera['x_res']
    y_res = config_pi_camera['y_res']
    camera = PiCamera()
    camera.resolution = (x_res, y_res)
    camera.framerate = config_pi_camera['framerate']
    raw_capture = PiRGBArray(camera, size=(x_res, y_res))
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    time.sleep(0.1)  # let camera warm up

    bounds = {'x': {'lower': int(x_res * (2/5)),
                    'upper': int(x_res * (3/5))},
              'y': {'lower': int(x_res * (2/5)),
                    'upper': int(x_res * (3/5))}}

    for frame in camera.capture_continuous(raw_capture,
                                           format='bgr',
                                           use_video_port=True):
        image = frame.array
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) == 0 and count_up == 0:
            count_up = time.time()
        elif len(faces) == 0 or len(faces) > 1:
            if time.time() - count_up > timeout:
                scan()
        else:
            for dims in faces:
                rect = (dims[0], dims[1])
                center = get_center(dims)
                opp = get_opp(dims)

                check_y(center[1], bounds['y'])
                check_x(center[0], bounds['x'])
                cv2.rectangle(image, rect, opp, (255, 0, 0), 2)

                print("Faces: {}, X: {}, Y: {}".format(len(faces),
                                                       center[0],
                                                       center[1]))

        cv2.imshow('robot eye', image)
        key = cv2.waitKey(1) & 0xFF
        raw_capture.truncate(0)
        if key == ord('q'):
            break

    cv2.destroyAllWindows()


def check_y(y, bound):
    if y < bound['lower']:
        # tilt down
        print('y LOW')
        pass
    elif y > bound['upper']:
        # tilt up
        print('y HIGH')
        pass
    else:
        # do nothing
        print('y good')
        pass


def check_x(x, bound):
    if x < bound['lower']:
        # set car to drive left
        print('x HIGH')
        pass
    elif x > bound['upper']:
        # set car to drive right
        print('x HIGH')
        pass
    else:
        # set car to drive straight
        print('x good')
        pass

def scan():
    # do some turns and tilt the camera up and down to try to find a
    # face to follow
    pass

    
find_face()
