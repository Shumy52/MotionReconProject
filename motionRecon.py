# import cv2
# import time
#
# # Open the default camera
# cap = cv2.VideoCapture(0)
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)  # Lower resolution to 320x240 for performance
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
#
# # Check if the camera opened successfully
# if not cap.isOpened():
#     print("Error: Could not open camera.")
#     exit()
#
# # Read the first frame, resize it for performance, and convert it to grayscale
# ret, previous_frame = cap.read()
# if not ret:
#     print("Error: Failed to grab frame.")
#     cap.release()
#     cv2.destroyAllWindows()
#     exit()
#
# # Convert to grayscale and apply Gaussian blur for smooth frame differences
# previous_frame = cv2.cvtColor(previous_frame, cv2.COLOR_BGR2GRAY)
# previous_frame = cv2.GaussianBlur(previous_frame, (5, 5), 0)
#
# motion_flag = False
# motion_start_time = None
#
# while cap.isOpened():
#     # Discard any buffered frames to get the latest frame (try experimenting with fewer skips if it’s too aggressive)
#     for _ in range(4):
#         cap.grab()
#
#     # Capture the next frame
#     ret, current_frame = cap.read()
#     if not ret:
#         break
#
#     # Convert current frame to grayscale and apply Gaussian blur
#     current_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
#     current_gray = cv2.GaussianBlur(current_gray, (5, 5), 0)
#
#     # Calculate the absolute difference between current and previous frames
#     frame_diff = cv2.absdiff(previous_frame, current_gray)
#
#     # Apply a threshold to get a binary image
#     _, thresh = cv2.threshold(frame_diff, 20, 255, cv2.THRESH_BINARY)
#
#     # Find contours in the thresholded image
#     contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#
#     significant_motion = False
#     for contour in contours:
#         # Ignore small contours to reduce noise
#         if cv2.contourArea(contour) < 500:
#             continue
#
#         significant_motion = True
#         # Draw a bounding box around the motion
#         (x, y, w, h) = cv2.boundingRect(contour)
#         cv2.rectangle(current_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
#
#     # Check if significant motion has been detected for at least 0.5 seconds
#     if significant_motion:
#         if not motion_flag:
#             motion_flag = True
#             motion_start_time = time.time()
#         elif time.time() - motion_start_time >= 0.5:
#             print("Significant motion detected for 0.5 seconds!")
#     else:
#         motion_flag = False
#         motion_start_time = None
#
#     # Display the regular camera feed with motion boxes
#     cv2.imshow('Camera Feed', current_frame)
#
#     # Update the previous frame
#     previous_frame = current_gray
#
#     # Exit on pressing 'q'
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#
# # Release the capture and close windows
# cap.release()
# cv2.destroyAllWindows()
