import cv2
import os
import sys

def test_video(video_path):
    print(f"Testing video file: {video_path}")
    if not os.path.exists(video_path):
        print("Error: File does not exist.")
        return

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error: Could not open video capture.")
        return

    print(f"Backend Name: {cap.getBackendName()}")
    print(f"FPS: {cap.get(cv2.CAP_PROP_FPS)}")
    print(f"Frame Count: {cap.get(cv2.CAP_PROP_FRAME_COUNT)}")
    print(f"Width: {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}")
    print(f"Height: {cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")

    print("Attempting to read first 5 frames...")
    for i in range(5):
        ret, frame = cap.read()
        if ret:
            print(f"Frame {i}: Success - Shape {frame.shape}")
        else:
            print(f"Frame {i}: Failed to read")

    cap.release()
    print("Test finished.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = "Download.mp4"

    test_video(path)
