#!/usr/bin/env python

import asyncio
import websockets

async def send_hello_and_listen(uri):
    async with websockets.connect(uri) as websocket:
        await websocket.send("hello")
        print("Message 'hello' sent to the server.")
        # Continue to await and print messages from the server
        while True:
            message = await websocket.recv()
            print(f"Message from server: {message}")

async def main():
    server_uri = "ws://localhost:8001"
    await send_hello_and_listen(server_uri)

if __name__ == "__main__":
    asyncio.run(main())