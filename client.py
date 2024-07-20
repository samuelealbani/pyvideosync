#!/usr/bin/env python
import cv2
import os
import asyncio
import glob
import websockets

server_uri = "ws://localhost:8001"

frames_directory = './frames'
frame_files = []

async def display_frame(_index):
    global frame_files
    frame = cv2.imread(frame_files[_index])
    # frame_path = os.path.join(frames_directory, f"frame{_index}.jpg")
    # frame = cv2.imread(frame_path)
    if frame is not None:
        cv2.imshow('Frame', frame)
        cv2.waitKey(1)  # Display the frame for 1 ms
    else:
        print(f"Frame {_index} not found.")

async def send_hello_and_listen(uri):
    async with websockets.connect(uri) as websocket:
        await websocket.send("hello")
        print("Message 'hello' sent to the server.")
        # Continue to await and print messages from the server
        while True:
            message = await websocket.recv()
            print(f"Message from server: {message}")
            # Check if the message is an integer and less than the total number of frames
            if message.isdigit() and int(message) < len(frame_files):
                await display_frame(int(message))
            else:
                print(f"Invalid message: {message}")

def setup(directory_path):
    global tot_frames
    global frame_files
    # List all jpg files in the directory
    frame_files = glob.glob(os.path.join(directory_path, '*.jpg'))
    
    # Sort the frame files, assuming filenames have numbers indicating order
    frame_files.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
    tot_frames=len(frame_files)

async def main():
    global server_uri
    global frames_directory

    setup(frames_directory)
    await send_hello_and_listen(server_uri)

if __name__ == "__main__":
    asyncio.run(main())