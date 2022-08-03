import datetime
import os
import subprocess
import time
import sys
import pathlib

import csv

import cv2
import msvcrt

import explorepy
import numpy as np


def construct_marker(counter, gesture, start, gesture_count=32):
    """
    A marker can be in range 0-65535 for explore (16 bit), thus the following structure is used:

    0bxxxxxxxxxx xxxxx x

    [experiment number: 10 bits] [gesture type: 5 bits] [start/stop: 1 bit]

    This marker can hold start/stop info for 2^5 = 32 gestures for 2^10 = 1024 experiments
    The experiment number uniquely identifies the experiment
    If less gestures are checked for, the experiment count can be increased


    :param counter: int from 0-1023, encoding the experiment number
    :type counter: int
    :param gesture: int from 0-31, encoding the gesture type
    :type gesture: int
    :param start: bool indicating whether the marker indicates start or end of experiment
    :type start: bool
    :param gesture_count: max number of gestures to differentiate, has to be a power of 2
    :type gesture_count: int
    :return: A marker encoding experiment number, gesture type and start/stop
    """
    if (gesture_count & (gesture_count - 1)) != 0:
        raise ValueError("Passed gesture count not a power of 2!")
    return counter << int(np.log2(gesture_count)) | gesture << 1 | start


# TODO allow input of up to 32 gestures / markers instead of 10
def await_key():
    """
    Waits until user enters a number key (no newline / enter necessary) and
    starts video recording if the user inputs a valid number
    """
    is_recording = False
    key = ''
    while key != b'q' and not is_recording:
        capture, writer, target = open_capture_writer()
        print("Press a number key to start recording for the specified marker")
        print("Press [q] to quit")
        print("(0) -- Marker")
        print("(1) -- Marker")
        print("(2) -- Marker")
        print("(3) -- Marker")
        print("(4) -- Marker")
        print("(5) -- Marker")
        print("(6) -- Marker")
        print("(7) -- Marker")
        print("(8) -- Marker")
        print("(9) -- Marker")
        print("Waiting for key input...")
        key = msvcrt.getch()
        print(f"Key input: {key}")
        if key in key_mask:
            print("Starting video recording")
            print("Press [r] during recording to stop current recording and start a new one")
            print("Press [q] during recording to stop current recording and quit program")
            record_video(int(key), capture, writer, target)
            is_recording = True


def open_capture_writer(fourcc='XVID'):
    """
    Utility function to handle preparing recording with openCV.
    Instantiates VideoCapture and VideoWriter object with necessary settings.

    :param fourcc: FourCC code indicating video format (default is XVID for .avi)
    :type fourcc: str
    :return: VideoCapture object, VideoWriter object and video file to write to
    """
    prev = time.time()
    capture = cv2.VideoCapture(0)
    d = time.time() - prev
    print(f"Took {d:.2f} seconds to open video capture")

    ret, example = capture.read()

    codec = cv2.VideoWriter_fourcc(*fourcc)
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    target = f'data\\videos\\exg_{now}.avi'
    print(capture.get(cv2.CAP_PROP_FPS))
    writer = cv2.VideoWriter(target, codec, capture.get(cv2.CAP_PROP_FPS), (example.shape[1], example.shape[0]))
    return capture, writer, target


def record_video(marker, capture, writer, target):
    """
    Records video until the user inputs q to save and quit the program or r
    to save and stop recording and await a new key
    :param marker: Marker / gesture type as indicated by the user
    :param capture: VideoCapture object
    :param writer: VideoWriter object
    :param target: Target video file
    """
    if not capture.isOpened():
        print("Error: Could not open video capture!")
        exp.stop_recording()
        sys.exit(-1)

    if not writer.isOpened():
        print("Error: Could not open video writer!")
        exp.stop_recording()
        sys.exit(-1)

    stop = False
    first_frame = True
    start_time = -1.
    device_marker = construct_marker(0, marker, True)
    exp.set_marker(code=device_marker)
    while not stop:
        ret, frame = capture.read()  # TODO A safety check is in order here
        if first_frame:
            start_time = time.time()  # timestamp in s
            first_frame = False
        writer.write(frame)
        cv2.imshow("Video feed", frame)

        p = cv2.waitKey(1)

        # Close feed when q or r is pressed
        if p == ord('q') or p == ord('r'):
            stop = True

    exp.set_marker(code=(device_marker & 0b1111111111111110))  # set last bit to 0
    d = time.time() - start_time
    print(f"Video record time: {d}s")

    with open(f"data\\{filename}-videos.csv", "a", newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=",")
        csvwriter.writerow([target, start_time, d, f"sw_{device_marker}"])

    capture.release()
    cv2.destroyAllWindows()
    if p == ord('r'): await_key()


if __name__ == "__main__":
    print(len(sys.argv))
    device = "Explore_CA14"
    if len(sys.argv) > 1:
        if len(sys.argv[1]) == 12:
            if sys.argv[1][:8] == "Explore_":
                device = sys.argv[1]

    sys.exit(0)
    pathlib.Path("data\\videos").mkdir(parents=True, exist_ok=True)

    filename = datetime.datetime.now().strftime("exg_%Y-%m-%d_%H-%M-%S")
    exp = explorepy.Explore()
    exp.connect(device_name=device)
    exp.record_data(f"data\\{filename}")
    # exp.acquire()
    # os.system("explorepy record-data -n Explore_CA14 -f \"test_18-07.csv\" -d 30")
    # subprocess.run("explorepy record-data -n Explore_CA14 -f \"test_18-07.csv\" -d 30")
    # subprocess.Popen(["explorepy", "record-data", "-n", "Explore_CA14", "-f", "test_whatever_3.csv", "-d", "30"],
    #                 creationflags=subprocess.CREATE_NEW_CONSOLE)
    key_mask = [b'0', b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9']  #
    with open(f"data\\{filename}-videos.csv", "a", newline='') as csvfile:
        csv.writer(csvfile, delimiter=",").writerow(
            ["file_location", "start_time_from_epoch_s", "video_length_s", "marker"])
    await_key()
    exp.stop_recording()
