from flask import Flask, render_template, Response, request, redirect, url_for
import cv2
import time
import threading
from playsound import playsound

app = Flask(__name__)

# Global variable to hold the video source
video_source = 0  # Default to local webcam
motion_thread = None  # Thread for motion detection
stop_thread = False  # Flag to control the motion detection thread

import threading

# Function to play sound in a separate thread
def play_sound_async(sound_file):
    # Define a thread to play the sound asynchronously
    # Cooldown mechanism to limit sound playback
    if not hasattr(play_sound_async, "last_played"):
        play_sound_async.last_played = 0

    current_time = time.time()
    if current_time - play_sound_async.last_played >= 1 :  # 0.2 seconds cooldown (5 times per second)
        play_sound_async.last_played = current_time
        threading.Thread(target=playsound, args=(sound_file,), daemon=True).start()


def generate_frames():
    # Use the global video_source for motion detection
    global video_source, stop_thread
    cap = cv2.VideoCapture(video_source)
    ret, previous_frame = cap.read()
    if not ret:
        print("Error: Failed to grab initial frame.")
        cap.release()
        return

    previous_frame = cv2.cvtColor(previous_frame, cv2.COLOR_BGR2GRAY)
    previous_frame = cv2.GaussianBlur(previous_frame, (5, 5), 0)
    motion_start_time = None
    motion_flag = False

    while not stop_thread:
        success, current_frame = cap.read()
        if not success:
            break

        current_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
        current_gray = cv2.GaussianBlur(current_gray, (5, 5), 0)

        # Perform frame differencing
        frame_diff = cv2.absdiff(previous_frame, current_gray)
        _, thresh = cv2.threshold(frame_diff, 5, 255, cv2.THRESH_BINARY)

        # Detect contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        significant_motion = False
        for contour in contours:
            if cv2.contourArea(contour) < 500:
                continue
            significant_motion = True
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(current_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Check if significant motion persists for 0.5 seconds
        if significant_motion:
            if not motion_flag:
                motion_flag = True
                motion_start_time = time.time()
            elif time.time() - motion_start_time >= 0.25:
                play_sound_async('C:/Users/Shumy/Downloads/WhatsApp Video 2024-11-11 at 10.48.05.mp3')
                print("Significant motion detected for 0.5 seconds!")
        else:
            motion_flag = False
            motion_start_time = None

        # Encode the frame as JPEG and yield
        ret, buffer = cv2.imencode('.jpg', current_frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        # Update the previous frame for the next loop
        previous_frame = current_gray

    cap.release()


@app.route('/')
def index():
    # Main page with video feed form
    return render_template('index.html')


@app.route('/set_feed', methods=['POST'])
def set_feed():
    global video_source, stop_thread, motion_thread

    # Stop existing motion detection thread, if any
    stop_thread = True
    if motion_thread and motion_thread.is_alive():
        motion_thread.join()

    # Update the video source from user input
    feed_url = request.form['feed_url']
    video_source = feed_url if feed_url else 0  # Default to webcam if URL is empty

    # Reset stop flag and start a new motion detection thread
    stop_thread = False
    motion_thread = threading.Thread(target=generate_frames)
    motion_thread.start()

    return redirect(url_for('index'))


@app.route('/video_feed')
def video_feed():
    # Route to serve the motion detection video stream
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True)