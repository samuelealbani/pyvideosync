#!/usr/bin/env python
import cv2
import os
import glob
import asyncio
import websockets

tot_frames=0
frames_directory = './frames'
frame_files = []
clients = []  # List to keep track of connected clients
loop=True
frame_counter=0

async def register_client(websocket):
    clients.append(websocket)
    print("New client connected.")
    try:
        await websocket.wait_closed()
    finally:
        clients.remove(websocket)

async def notify_clients(message):
    if clients:  # Check if there are any connected clients
        await asyncio.wait([client.send(message) for client in clients])

async def handler(websocket, path):
    while True:
        try:
            message = await websocket.recv()
        except websockets.ConnectionClosedOK:
            break
        # check if message is "hello" and add the client to the list
        if message == "hello":
            clients.append(websocket)
            print(f"New client connected. Currently {len(clients)} clients connected.")
        print(message, message == "hello")

def setup(directory_path):
    global tot_frames
    global frame_files
    # List all jpg files in the directory
    frame_files = glob.glob(os.path.join(directory_path, '*.jpg'))
    
    # Sort the frame files, assuming filenames have numbers indicating order
    frame_files.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
    tot_frames=len(frame_files)
    
# await notify_clients(f"Playing frame {index}")

async def play_frame_sequence():
    global frame_files
    global loop
    index = 0  # Initialize the index outside the loop

    while True:  # Use a while True loop for continuous playback
        frame_file = frame_files[index]
        frame = cv2.imread(frame_file)
        cv2.imshow('Frame Sequence', frame)
        
        # Notify clients about the current frame
        await notify_clients(f"Playing frame {index}")

        # print("Playing frame ", index)

        # Increment the index for the next frame
        index += 1

        # If at the end of the list and looping is enabled, reset index to 0
        if index == len(frame_files) and loop:
            index = 0
        elif index == len(frame_files) and not loop:
            break  # Exit the loop if not looping

        # Wait for 25 ms between frames, break loop on pressing 'q'
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever

    await play_frame_sequence()


if __name__ == "__main__":
    asyncio.run(main())

# Example usage
# Start WebSocket server
# start_server = websockets.serve(handler, "localhost", 6789)
# setup(frames_directory)
# print(tot_frames)
# play_frame_sequence()

# async def main():
#     setup(frames_directory)  # Assuming setup is defined elsewhere

#     # Start WebSocket server
#     start_server = websockets.serve(handler, "localhost", 6789)

#     # Run the server
#     server = await start_server
#     print("WebSocket server started.")

#     # Run the play_frame_sequence concurrently
#     await play_frame_sequence()

#     # Keep the server running
#     await server.wait_closed()

# try:
#     asyncio.run(main())
# except Exception as e:
#     print(f"An error occurred: {e}")



