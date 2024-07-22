#!/usr/bin/env python
import asyncio
import glob
import os
import cv2  # Import OpenCV
import websockets
import time

clients = []  # List to keep track of connected clients
loop=True
frames_directory = '/media/pi/BIENCA/GAN_50'
'/Volumes/Extreme SSD/Hydromancy PROJECT/Premiere/MessaInOnda/render/Montaggione-1/Input_100'
tot_frames=0
index_frame=0
fps=18
sync_interval=100
verbose=True

# this manages the connection
async def handler(websocket):
    while True:
        try:
            message = await websocket.recv()
        except websockets.ConnectionClosedOK:
            break
        print(f"Received message: {message}")
        if message == "hello":
            clients.append(websocket)
            print(f"New client connected. Currently {len(clients)} clients connected.")
        print(message, message == "hello")

# async def periodic_task():
#     global index_frame
#     global loop
#     global fps
#     while True:
#         # print("This is called every second")
#         # print(f"Playing frame {index_frame}")
#         if clients:
#             # Create tasks from coroutines before passing them to asyncio.wait
#             if index_frame==0:
#                 tasks = [asyncio.create_task(client.send(f"{index_frame}")) for client in clients]
#                 await asyncio.wait(tasks)
#         await asyncio.sleep(1/fps)
#         index_frame += 1
#         if loop:
#             if index_frame >= tot_frames-1:
#                 index_frame = 0
        
async def periodic_task():
    global index_frame
    global loop
    global fps
    next_frame_time = time.time()  # Initialize the next frame time

    while True:
        start_time = time.time()  # Start time of the loop iteration

        # check every sync_interval frames if there are clients connected
        # if clients and index_frame == 0:
        if clients and index_frame % sync_interval == 0:
            # Send the frame index to all clients at the beginning of the sequence
            tasks = [asyncio.create_task(client.send(f"{index_frame}")) for client in clients]
            await asyncio.wait(tasks)

        # Calculate the time to wait until the next frame
        next_frame_time += 1.0 / fps
        sleep_time = max(0, next_frame_time - time.time())

        await asyncio.sleep(sleep_time)  # Sleep for the calculated duration

        index_frame += 1
        if loop and index_frame == tot_frames - 1:
            index_frame = 0

        # Calculate and print the actual fps for debugging purposes
        actual_fps = 1.0 / (time.time() - start_time)
        if verbose:
            print(f"frame{index_frame} - Actual FPS: {actual_fps:.2f}")

def setup(directory_path):
    global tot_frames
    # List all jpg files in the directory
    frame_files = glob.glob(os.path.join(directory_path, '*.jpg'))
    tot_frames=len(frame_files)
    print(f"Found {tot_frames} frames in the directory.")


async def main():

    setup(frames_directory)

    print("Server starting...")
    # async with websockets.serve(handler, "", 8001):
    #     await asyncio.Future()  # run forever
    server = websockets.serve(handler, "", 8001)
    task = periodic_task()
    await asyncio.gather(server, task)



if __name__ == "__main__":
    asyncio.run(main())