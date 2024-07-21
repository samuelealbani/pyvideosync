#!/usr/bin/env python
import cv2
import os
import asyncio
import glob
import websockets
import time

frame_files = []
frame_adjustment=False
sync_frame=0

async def periodic_task(frames_array, is_looping=True, max_fps=25, is_verbose=False, resize=False, resize_width=1920, resize_height=1080):
    global frame_adjustment
    global sync_frame

    print("Periodic task started.")
    index_frame = 0

    frame_duration = 1.0 / max_fps  # Duration each frame should be displayed to maintain the FPS


    length_sequence = len(frames_array)

    next_frame_time = time.time()  # Initialize the next frame time

    while True:
        start_time = time.time()  # Start time of the loop iteration

        await display_frame(index_frame)

        # Calculate the time to wait until the next frame
        # next_frame_time += 1.0 / max_fps
        # sleep_time = max(0, next_frame_time - time.time())
        processing_time = time.time() - start_time
        # Calculate how much time to sleep to maintain the frame duration
        sleep_duration = max(frame_duration - processing_time, 0)

        await asyncio.sleep(sleep_duration)  # Sleep for the calculated duration
        if frame_adjustment:
            if is_verbose:
                print(f"Frame adjusted to {sync_frame}, was {index_frame}")
            index_frame = sync_frame
            frame_adjustment=False
        else:    
            index_frame += 1
        if is_looping and index_frame == length_sequence - 1:
            index_frame = 0

        if is_verbose:
            # Optional: Calculate and print the actual fps for debugging purposes
            actual_fps = 1.0 / (time.time() - start_time)
            print(f"frame{index_frame} - Actual FPS: {actual_fps:.2f}")   

async def display_frame(_index, resize=False, resize_width=1920, resize_height=1080):
    global frame_files

    frame = cv2.imread(frame_files[_index])
    
    if frame is not None:
        if resize:
            frame = cv2.resize(frame, (resize_width, resize_height))
        cv2.imshow('Frame', frame)
          # Display the frame for 1 ms
        if cv2.waitKey(1) & 0xFF == 27:  # 27 is the ASCII value for the ESC key
            cv2.destroyAllWindows()  # Close the OpenCV window
            os._exit(0)  # Exit the program immediately
    else:
        print(f"Frame {_index} not found.")



async def send_hello_and_listen(uri, tot_frames):
    global sync_frame
    global frame_adjustment

    async with websockets.connect(uri) as websocket:
        try:
            await websocket.send("hello")
            print("Message 'hello' sent to the server.")
            # Continue to await and print messages from the server
            while True:
                message = await websocket.recv()
                print(f"Message from server: {message}")
                # Check if the message is an integer and less than the total number of frames
                if message.isdigit() and int(message) < tot_frames: # and int(message) != index_frame:
                    print(f"Alignement received: {message};")
                    sync_frame = int(message)
                    frame_adjustment=True
                else:
                    print(f"Invalid message: {message}\n message.isdigit(): {message.isdigit()} and int(message): {message.isdigit()} < tot_frames: {tot_frames} -> {int(message) < tot_frames}")
        except websockets.exceptions.ConnectionClosed:
            print("Connection with server closed. Continuing to play frames...")
        except Exception as e:
            print(f"An error occurred: {e}")


def setup(directory_path, is_fullscreen=False):

    if is_fullscreen:
        cv2.namedWindow('Frame', cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty('Frame',cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

    frame_files = glob.glob(os.path.join(directory_path, '*.jpg'))
    
    # Sort the frame files, assuming filenames have numbers indicating order
    frame_files.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
    tot_frames=len(frame_files)
    print(f"Total frames: {tot_frames}")
    return frame_files

async def main():

    global frame_files

    loop=True

    server_uri = "ws://192.168.1.11:8001"
    frames_directory = '/Volumes/Extreme SSD/Hydromancy PROJECT/Premiere/MessaInOnda/render/Montaggione-1/Input_100'

    fps=25

    verbose=True
    fullscreen=True

    resize=True
    resize_width=1920
    resize_height=1080

    loop=True

    
    frame_files = setup(frames_directory)
    communication_task = send_hello_and_listen(server_uri, len(frame_files))
    display_task = periodic_task(frame_files, loop, fps, verbose, resize, resize_width, resize_height)
    await asyncio.gather(communication_task, display_task)


if __name__ == "__main__":
    asyncio.run(main())