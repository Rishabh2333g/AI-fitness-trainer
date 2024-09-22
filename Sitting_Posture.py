import cv2
import math as m
import mediapipe as mp
import pygame
import time

# Initialize Pygame mixer
pygame.mixer.init()

# Calculate distance between two points
def findDistance(x1, y1, x2, y2):
    return m.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# Calculate angle between two points and a reference axis (vertical axis)
def find_angle(x1, y1, x2, y2):
    try:
        # Check if y1 is zero to avoid division by zero
        if y1 == 0:
            return 90  # Assume 90 degrees if y1 is zero (vertical line)
        theta = m.atan2(abs(y2 - y1), abs(x2 - x1))  # Calculate using arctangent for robustness
        degree = m.degrees(theta)  # Convert to degrees
        return degree
    except:
        return 0  # Return 0 degrees in case of error

# Function to send an alert (play sound) when bad posture is detected
def sendWarning():
    try:
        alert_sound = pygame.mixer.Sound("siren-alert.mp3")
        alert_sound.play()
    except pygame.error as e:
        print(f"Audio Error: {e}")

# Initialize frame counters
good_frames = 0
bad_frames = 0

# Font type and color settings
font = cv2.FONT_HERSHEY_SIMPLEX
green = (127, 255, 0)
red = (50, 50, 255)
light_green = (127, 233, 100)
yellow = (0, 255, 255)
pink = (255, 0, 255)

# Initialize MediaPipe Pose module
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

if __name__ == "__main__":
    # For webcam input replace with `0`
    file_name = 'input.mp4'  # Change this to 0 for webcam
    cap = cv2.VideoCapture(file_name)

    # Meta details for video
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_size = (width, height)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    # Video writer
    video_output = cv2.VideoWriter('output.mp4', fourcc, fps, frame_size)

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("No frames available.")
            break

        # Convert the BGR image to RGB for Mediapipe
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Process the image and get pose landmarks
        keypoints = pose.process(image)

        # Convert the image back to BGR for OpenCV
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Get the landmark data
        lm = keypoints.pose_landmarks

        if lm:  # Ensure landmarks are detected
            lmPose = mp_pose.PoseLandmark

            # Get relevant landmark positions
            l_shldr_x = int(lm.landmark[lmPose.LEFT_SHOULDER].x * width)
            l_shldr_y = int(lm.landmark[lmPose.LEFT_SHOULDER].y * height)
            r_shldr_x = int(lm.landmark[lmPose.RIGHT_SHOULDER].x * width)
            r_shldr_y = int(lm.landmark[lmPose.RIGHT_SHOULDER].y * height)
            l_ear_x = int(lm.landmark[lmPose.LEFT_EAR].x * width)
            l_ear_y = int(lm.landmark[lmPose.LEFT_EAR].y * height)
            l_hip_x = int(lm.landmark[lmPose.LEFT_HIP].x * width)
            l_hip_y = int(lm.landmark[lmPose.LEFT_HIP].y * height)

            # Check alignment of shoulders (for side view)
            offset = findDistance(l_shldr_x, l_shldr_y, r_shldr_x, r_shldr_y)
            if offset < 100:
                cv2.putText(image, f'{int(offset)} Aligned', (width - 150, 30), font, 0.9, green, 2)
            else:
                cv2.putText(image, f'{int(offset)} Not Aligned', (width - 150, 30), font, 0.9, red, 2)

            # Calculate angles
            neck_inclination = find_angle(l_shldr_x, l_shldr_y, l_ear_x, l_ear_y)
            torso_inclination = find_angle(l_hip_x, l_hip_y, l_shldr_x, l_shldr_y)

            # Check posture and display results
            angle_text_string = f'Neck: {int(neck_inclination)}  Torso: {int(torso_inclination)}'

            if neck_inclination < 40 and torso_inclination < 10:
                bad_frames = 0
                good_frames += 1
                color = light_green
            else:
                good_frames = 0
                bad_frames += 1
                color = red

            # Draw landmarks and lines
            cv2.putText(image, angle_text_string, (10, 30), font, 0.9, color, 2)
            cv2.line(image, (l_shldr_x, l_shldr_y), (l_ear_x, l_ear_y), color, 4)
            cv2.line(image, (l_shldr_x, l_shldr_y), (l_hip_x, l_hip_y), color, 4)

            # Calculate posture times
            good_time = (1 / fps) * good_frames
            bad_time = (1 / fps) * bad_frames

            if good_time > 0:
                cv2.putText(image, f'Good Posture Time: {round(good_time, 1)}s', (10, height - 20), font, 0.9, green, 2)
            else:
                cv2.putText(image, f'Bad Posture Time: {round(bad_time, 1)}s', (10, height - 20), font, 0.9, red, 2)

            # Play warning if bad posture persists for more than 3 minutes
            if bad_time > 180:
                sendWarning()

        # Write the processed frame to the output video
        video_output.write(image)

        # Show frame (optional, can be commented if running on a server without GUI)
        cv2.imshow('Posture Analysis', image)
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

    cap.release()
    video_output.release()
    cv2.destroyAllWindows()
