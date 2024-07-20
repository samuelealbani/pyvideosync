#!/usr/bin/env python
import asyncio
import glob
import os
import cv2  # Import OpenCV
import websockets

clients = []  # List to keep track of connected clients
loop=True
frames_directory = './frames'
tot_frames=0
index_frame=0
fps=12

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

async def periodic_task():
    global index_frame
    global loop
    global fps
    while True:
        # print("This is called every second")
        # print(f"Playing frame {index_frame}")
        if clients:
            # Create tasks from coroutines before passing them to asyncio.wait
            if index_frame==0:
                tasks = [asyncio.create_task(client.send(f"{index_frame}")) for client in clients]
                await asyncio.wait(tasks)
        await asyncio.sleep(1/fps)
        index_frame += 1
        if loop:
            if index_frame >= tot_frames-1:
                index_frame = 0
        

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