#!/usr/bin/bash

# Path to the virtual environment
VENV_PATH="/home/pi/Desktop/pyvideosync/.venv"

# Path to the Python program
PYTHON_PROGRAM="/home/pi/Desktop/pyvideosync/server.py"
CLIENT_PROGRAM="/home/pi/Desktop/pyvideosync/client.py"

# Open a new terminal window and run the commands
lxterminal --command="bash -c 'source $VENV_PATH/bin/activate && sudo python3 $PYTHON_PROGRAM; exec bash'" &

sleep 5

lxterminal --command="bash -c 'source $VENV_PATH/bin/activate && sudo python3 $CLIENT_PROGRAM; exec bash'"
