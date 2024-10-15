#!/usr/bin/env python
import cv2
import os
import asyncio
import glob
import websockets
import time  # Import time module
import numpy as np  # Import numpy for creating a black image
from typing import List

# Constants
SERVER_URI = "ws://192.168.100.82:8001"
FRAMES_DIRECTORY = '/media/pi/Piccilla/Input_1280-720'
FPS = 18
RESIZE_WIDTH = 1920
RESIZE_HEIGHT = 1080
ESC_KEY = 27
RECONNECT_DELAY = 5  # Delay in seconds before attempting to reconnect

# Global Variables
frame_files: List[str] = []
tot_frames = 0
index_frame = 0
loop = True
verbose = False
fullscreen = True
resize = True
is_playing = True
play_event = asyncio.Event()

def str_to_bool(s: str) -> bool:
    return s == "True"

async def periodic_task():
    global index_frame, tot_frames, loop, FPS

    next_frame_time = time.time()

    while True:
        await play_event.wait()  # Wait until play_event is set

        start_time = time.time()
        await display_frame(index_frame)

        next_frame_time += 1.0 / FPS
        sleep_time = max(0, next_frame_time - time.time())
        await asyncio.sleep(sleep_time)

        index_frame += 1
        if loop and index_frame == tot_frames - 1:
            index_frame = 0

        if verbose:
            actual_fps = 1.0 / (time.time() - start_time)
            print(f"frame{index_frame} - Actual FPS: {actual_fps:.2f}")

async def display_frame(_index: int):
    global frame_files, fullscreen, resize, RESIZE_WIDTH, RESIZE_HEIGHT, is_playing

    if fullscreen:
        cv2.namedWindow('Frame', cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty('Frame', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    if is_playing:
        frame = cv2.imread(frame_files[_index])
        if frame is not None:
            if resize:
                frame = cv2.resize(frame, (RESIZE_WIDTH, RESIZE_HEIGHT))
            cv2.imshow('Frame', frame)
        else:
            print(f"Frame {_index} not found.")
    else:
        # Create a black image
        black_frame = np.zeros((RESIZE_HEIGHT, RESIZE_WIDTH, 3), dtype=np.uint8)
        cv2.imshow('Frame', black_frame)

    if cv2.waitKey(1) & 0xFF == ESC_KEY:
        cv2.destroyAllWindows()
        os._exit(0)

async def send_hello_and_listen(uri: str):
    global index_frame, tot_frames, is_playing

    while True:
        try:
            async with websockets.connect(uri) as websocket:
                await websocket.send("hello")
                print("Message 'hello' sent to the server.")
                while True:
                    message = await websocket.recv()
                    print(f"Message from server: {message}")

                    if message.isdigit() and int(message) < tot_frames:
                        index_frame = int(message)
                    elif isinstance(message, str) and str_to_bool(message) in [True, False]:
                        is_playing = str_to_bool(message)
                        if not is_playing:
                            print('im here')
                        else:
                            play_event.set()
                    else:
                        print(f"Invalid message: {message}")
        except websockets.exceptions.ConnectionClosed:
            print("Connection with server closed. Attempting to reconnect...")
        except Exception as e:
            print(f"An error occurred: {e}")
        await asyncio.sleep(RECONNECT_DELAY)

def setup(directory_path: str):
    global tot_frames, frame_files
    frame_files = glob.glob(os.path.join(directory_path, '*.jpg'))
    frame_files.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
    tot_frames = len(frame_files)
    print(f"Total frames: {tot_frames}")

async def main():
    setup(FRAMES_DIRECTORY)
    play_event.set()
    await asyncio.gather(send_hello_and_listen(SERVER_URI), periodic_task())

if __name__ == "__main__":
    asyncio.run(main())