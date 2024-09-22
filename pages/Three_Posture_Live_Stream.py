import cv2
import mediapipe as mp
import time
import streamlit as st
import numpy as np
# from utils import find_angle, findDistance, sendWarning
from utils import find_angle, findDistance, sendWarning


# Streamlit page configuration
# st.set_page_config(page_title="Live Posture Detection", layout="wide")

st.title("AI Fitness Trainer: Squats Analysis")
st.write("Ensure that the camera is positioned such that the side view is visible for better results.")

# Set up columns for layout
col1, col2 = st.columns(2)

# Placeholder for the webcam video feed
frame_window = col1.image([])

# Initialize mediapipe pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Frame counters
good_frames = 0
bad_frames = 0

# Colors
green = (127, 255, 0)
red = (50, 50, 255)
light_green = (127, 233, 100)

# Capture webcam input
cap = cv2.VideoCapture(0)

fps = 30  # Initialize default FPS (can be updated by webcam)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        st.write("Unable to access the webcam. Please check your device.")
        break

    # Get height and width of the frame
    h, w = frame.shape[:2]

    # Convert the BGR image to RGB for mediapipe
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame with mediapipe pose detection
    keypoints = pose.process(frame_rgb)

    # Convert back to BGR for OpenCV visualization
    frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

    if keypoints.pose_landmarks:
        lm = keypoints.pose_landmarks.landmark
        lmPose = mp_pose.PoseLandmark

        # Acquire the landmark coordinates
        l_shldr_x = int(lm[lmPose.LEFT_SHOULDER].x * w)
        l_shldr_y = int(lm[lmPose.LEFT_SHOULDER].y * h)
        r_shldr_x = int(lm[lmPose.RIGHT_SHOULDER].x * w)
        r_shldr_y = int(lm[lmPose.RIGHT_SHOULDER].y * h)
        l_ear_x = int(lm[lmPose.LEFT_EAR].x * w)
        l_ear_y = int(lm[lmPose.LEFT_EAR].y * h)
        l_hip_x = int(lm[lmPose.LEFT_HIP].x * w)
        l_hip_y = int(lm[lmPose.LEFT_HIP].y * h)

        
        # neck_inclination = find_angle(l_shldr_x, l_shldr_y, l_ear_x, l_ear_y)
        # torso_inclination = find_angle(l_hip_x, l_hip_y, l_shldr_x, l_shldr_y)

        # Create points from the x, y coordinates
        l_shldr = np.array([l_shldr_x, l_shldr_y])
        l_ear = np.array([l_ear_x, l_ear_y])
        l_hip = np.array([l_hip_x, l_hip_y])

        # Calculate the angles
        neck_inclination = find_angle(l_shldr, l_ear)  # Two points, no reference point
        torso_inclination = find_angle(l_hip, l_shldr)  # Two points, no reference point

        # Calculate distances and angles
        offset = findDistance(l_shldr_x, l_shldr_y, r_shldr_x, r_shldr_y)

        # Determine posture condition
        if neck_inclination < 40 and torso_inclination < 10:
            bad_frames = 0
            good_frames += 1
            posture_status = "Good Posture"
            color = light_green

        else:
            good_frames = 0
            bad_frames += 1
            posture_status = "Bad Posture"
            color = red

        # Draw landmarks and lines
        cv2.circle(frame, (l_shldr_x, l_shldr_y), 7, color, -1)
        cv2.circle(frame, (l_ear_x, l_ear_y), 7, color, -1)
        cv2.circle(frame, (l_hip_x, l_hip_y), 7, color, -1)

        cv2.line(frame, (l_shldr_x, l_shldr_y), (l_ear_x, l_ear_y), color, 3)
        cv2.line(frame, (l_shldr_x, l_shldr_y), (l_hip_x, l_hip_y), color, 3)

        # Calculate the time for good/bad posture
        good_time = good_frames / fps
        bad_time = bad_frames / fps

        # If bad posture persists for more than 3 minutes (180 seconds), send an alert
        if bad_time > 180:
            sendWarning()

        # Display posture status and angle info
        cv2.putText(frame, f'Posture: {posture_status}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
        cv2.putText(frame, f'Neck Angle: {int(neck_inclination)}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
        cv2.putText(frame, f'Torso Angle: {int(torso_inclination)}', (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

    # Update frame window in Streamlit
    frame_window.image(frame, channels="BGR")

    # Break the loop if the user presses 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
