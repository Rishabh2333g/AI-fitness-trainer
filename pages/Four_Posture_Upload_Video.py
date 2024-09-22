import cv2
import mediapipe as mp
import streamlit as st
import numpy as np
from utils import find_angle, findDistance, sendWarning
from tempfile import NamedTemporaryFile

# Streamlit page configuration
# st.set_page_config(page_title="Upload Video for Posture Detection", layout="wide")

st.title("AI Fitness Trainer: Fix Sitting Posture Detection")

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

# Upload video option in Streamlit
uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    # Save the uploaded video to a temporary file
    temp_file = NamedTemporaryFile(delete=False)
    temp_file.write(uploaded_file.read())
    temp_file_name = temp_file.name

    # Display the uploaded video in Streamlit
    st.video(uploaded_file)

    # Start processing the uploaded video
    cap = cv2.VideoCapture(temp_file_name)

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Placeholder for displaying video frames with pose analysis
    frame_window = st.image([])

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        # Get frame dimensions
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

            # Calculate distances and angles
            offset = findDistance(l_shldr_x, l_shldr_y, r_shldr_x, r_shldr_y)
            neck_inclination = find_angle(l_shldr_x, l_shldr_y, l_ear_x, l_ear_y)
            torso_inclination = find_angle(l_hip_x, l_hip_y, l_shldr_x, l_shldr_y)

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

    # Release video capture object
    cap.release()
else:
    st.write("Please upload a video file to start posture detection.")
