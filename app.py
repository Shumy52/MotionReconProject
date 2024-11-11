from flask import Flask, render_template, Response, request, redirect, url_for
import cv2

app = Flask(__name__)

# Initialize with the default camera feed
video_source = 0  # Default to local webcam

def generate_frames(source):
    # Initialize the video capture with the specified source
    cap = cv2.VideoCapture(source)
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        else:
            # Encode the frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    cap.release()

@app.route('/')
def index():
    # Main page that displays the video stream and form
    return render_template('index.html')

@app.route('/set_feed', methods=['POST'])
def set_feed():
    global video_source
    feed_url = request.form['feed_url']
    # Check if the feed URL is empty; if so, use the default camera
    if feed_url.strip() == '':
        video_source = 0  # Default camera
    else:
        video_source = feed_url  # Set to custom URL
    return redirect(url_for('index'))

@app.route('/video_feed')
def video_feed():
    # Route to serve the video stream
    return Response(generate_frames(video_source), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
