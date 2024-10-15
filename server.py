#!/usr/bin/env python
import asyncio
import glob
import os
import cv2  # Import OpenCV
import websockets
import time
from gpiozero import Button
from typing import List

# Constants
SERVER_URI = "ws://192.168.100.82:8001"
FRAMES_DIRECTORY = '/media/pi/Piccilla/Input_1280-720'
FPS = 18
SYNC_INTERVAL = 100
VERBOSE = True
BUTTON_PIN = 2

# Global Variables
frame_files: List[str] = []
tot_frames = 0
index_frame = 0
is_playing = True
prev_playing_status = True
clients = []  # List to keep track of connected clients
loop = True

button = Button(BUTTON_PIN)

def start_stop():
    global is_playing
    is_playing = not is_playing
    print('Pressed button, is_playing is', is_playing)
    time.sleep(0.5)

def str_to_bool(s: str) -> bool:
    if s == "True":
        return True
    elif s == "False":
        return False
    else:
        raise ValueError("Input string must be 'True' or 'False'")

async def handler(websocket):
    global clients
    clients.append(websocket)
    print(f"New client connected. Currently {len(clients)} clients connected.")
    try:
        while True:
            message = await websocket.recv()
            print(f"Received message: {message}")
            if message == "hello":
                print(f"Client said hello. Currently {len(clients)} clients connected.")
    except websockets.ConnectionClosedOK:
        print("Client disconnected.")
    finally:
        clients.remove(websocket)
        print(f"Client removed. Currently {len(clients)} clients connected.")

async def periodic_task():
    global index_frame, loop, FPS, is_playing, prev_playing_status

    next_frame_time = time.time()  # Initialize the next frame time

    while True:
        button.when_pressed = start_stop

        if is_playing != prev_playing_status:
            print('is_playing != prev_playing_status', is_playing)
            if clients:
                tasks = [asyncio.create_task(client.send(f"{is_playing}")) for client in clients]
                await asyncio.wait(tasks)
            prev_playing_status = is_playing

        if is_playing:
            start_time = time.time()  # Start time of the loop iteration

            if clients and index_frame % SYNC_INTERVAL == 0:
                tasks = [asyncio.create_task(client.send(f"{index_frame}")) for client in clients]
                await asyncio.wait(tasks)

            next_frame_time += 1.0 / FPS
            sleep_time = max(0, next_frame_time - time.time())
            await asyncio.sleep(sleep_time)  # Sleep for the calculated duration

            index_frame += 1
            if loop and index_frame == tot_frames - 1:
                index_frame = 0

            actual_fps = 1.0 / (time.time() - start_time)
            if VERBOSE:
                print(f"frame{index_frame} - Actual FPS: {actual_fps:.2f}")

def setup(directory_path: str):
    global tot_frames, frame_files
    frame_files = glob.glob(os.path.join(directory_path, '*.jpg'))
    tot_frames = len(frame_files)
    print(f"Found {tot_frames} frames in the directory.")

async def main():
    setup(FRAMES_DIRECTORY)
    print("Server starting...")
    server = websockets.serve(handler, "", 8001)
    await asyncio.gather(server, periodic_task())

if __name__ == "__main__":
    asyncio.run(main())