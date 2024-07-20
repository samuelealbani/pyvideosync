#!/usr/bin/env python
import cv2
import os
import asyncio
import glob
import websockets
import time

server_uri = "ws://192.168.1.11:8001"

frames_directory = './frames'
frame_files = []
tot_frames=0
index_frame=0
loop=True
fps=25

# async def periodic_task():
#     global index_frame
#     global tot_frames
#     global loop
#     global fps
#     while True:
#         await display_frame(int(index_frame))
#         await asyncio.sleep(1/fps)
#         index_frame += 1
#         if loop:
#             if index_frame >= tot_frames-1:
#                 index_frame = 0
 
async def periodic_task():
    global index_frame
    global tot_frames
    global loop
    global fps

    next_frame_time = time.time()  # Initialize the next frame time

    while True:
        start_time = time.time()  # Start time of the loop iteration

        await display_frame(int(index_frame))

        # Calculate the time to wait until the next frame
        next_frame_time += 1.0 / fps
        sleep_time = max(0, next_frame_time - time.time())

        await asyncio.sleep(sleep_time)  # Sleep for the calculated duration

        index_frame += 1
        if loop and index_frame >= tot_frames - 1:
            index_frame = 0

        # Optional: Calculate and print the actual fps for debugging purposes
        actual_fps = 1.0 / (time.time() - start_time)
        print(f"Actual FPS: {actual_fps:.2f}")      

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
    global index_frame
    async with websockets.connect(uri) as websocket:
        await websocket.send("hello")
        print("Message 'hello' sent to the server.")
        # Continue to await and print messages from the server
        while True:
            message = await websocket.recv()
            print(f"Message from server: {message}")
            # Check if the message is an integer and less than the total number of frames
            if message.isdigit() and int(message) <= len(frame_files) and int(message) != index_frame:
                index_frame = int(message)
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
    communication_task = send_hello_and_listen(server_uri)
    display_task = periodic_task()
    await asyncio.gather(communication_task, display_task)

if __name__ == "__main__":
    asyncio.run(main())