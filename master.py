import cv2
import os
import glob

tot_frames=0
frames_directory = './frames'

def setup(directory_path):
    global tot_frames
    global frame_files
    # List all jpg files in the directory
    frame_files = glob.glob(os.path.join(directory_path, '*.jpg'))
    
    # Sort the frame files, assuming filenames have numbers indicating order
    frame_files.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
    tot_frames=len(frame_files)
    

def play_frame_sequence():
    for frame_file in frame_files:
        frame = cv2.imread(frame_file)
        cv2.imshow('Frame Sequence', frame)
        
        # Wait for 25 ms between frames, break loop on pressing 'q'
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    
    cv2.destroyAllWindows()

# Example usage
setup(frames_directory)
print(tot_frames)
play_frame_sequence()
