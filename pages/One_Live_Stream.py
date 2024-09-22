# import av
# import os
# import sys
# import streamlit as st
# from streamlit_webrtc import VideoHTMLAttributes, webrtc_streamer
# from aiortc.contrib.media import MediaRecorder
# # import json
# # import mediapipe as mp
# # mp_pose = mp.solutions.pose


# BASE_DIR = os.path.abspath(os.path.join(__file__, '../../'))
# sys.path.append(BASE_DIR)


# from utils import get_mediapipe_pose
# from process_frame import ProcessFrame
# from thresholds import get_thresholds_beginner, get_thresholds_pro


# st.title('AI Fitness Trainer: Squats Analysis')

# mode = st.radio('Select Mode', ['Beginner', 'Pro'], horizontal=True)

# thresholds = None 

# if mode == 'Beginner':
#     thresholds = get_thresholds_beginner()

# elif mode == 'Pro':
#     thresholds = get_thresholds_pro()


# live_process_frame = ProcessFrame(thresholds=thresholds, flip_frame=True)
# # Initialize face mesh solution
# pose = get_mediapipe_pose()


# if 'download' not in st.session_state:
#     st.session_state['download'] = False

# output_video_file = f'output_live.flv'

  
# def video_frame_callback(frame: av.VideoFrame):
#     frame = frame.to_ndarray(format="rgb24")  # Decode and get RGB frame
#     frame, _ = live_process_frame.process(frame, pose)  # Process frame
#     return av.VideoFrame.from_ndarray(frame, format="rgb24")  # Encode and return BGR frame


# def out_recorder_factory() -> MediaRecorder:
#         return MediaRecorder(output_video_file)


# ctx = webrtc_streamer(
#                         key="Squats-pose-analysis",
#                         video_frame_callback=video_frame_callback,
#                         rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},  # Add this config
#                         media_stream_constraints={"video": {"width": {'min':480, 'ideal':480}}, "audio": False},
#                         video_html_attrs=VideoHTMLAttributes(autoPlay=True, controls=False, muted=False),
#                         out_recorder_factory=out_recorder_factory
#                     )


# download_button = st.empty()

# if os.path.exists(output_video_file):
#     with open(output_video_file, 'rb') as op_vid:
#         download = download_button.download_button('Download Video', data = op_vid, file_name='output_live.flv')

#         if download:
#             st.session_state['download'] = True



# if os.path.exists(output_video_file) and st.session_state['download']:
#     os.remove(output_video_file)
#     st.session_state['download'] = False
#     download_button.empty()


    

import av
import os
import sys
import streamlit as st
from streamlit_webrtc import VideoHTMLAttributes, webrtc_streamer
from aiortc.contrib.media import MediaRecorder

BASE_DIR = os.path.abspath(os.path.join(__file__, '../../'))
sys.path.append(BASE_DIR)

from utils import get_mediapipe_pose
from process_frame import ProcessFrame
from thresholds import get_thresholds_beginner, get_thresholds_pro

# Set up the Streamlit page title
st.title('AI Fitness Trainer: Squats Analysis')

# Radio button to select mode (Beginner or Pro)
mode = st.radio('Select Mode', ['Beginner', 'Pro'], horizontal=True)

# Load thresholds based on selected mode
thresholds = get_thresholds_beginner() if mode == 'Beginner' else get_thresholds_pro()

# Initialize Pose Detection and processing
live_process_frame = ProcessFrame(thresholds=thresholds, flip_frame=True)
pose = get_mediapipe_pose()

# Initialize session state to handle video download
if 'download' not in st.session_state:
    st.session_state['download'] = False

# Output file for recording the video
output_video_file = f'output_live.flv'

# Define the function to process each video frame
def video_frame_callback(frame: av.VideoFrame):
    frame = frame.to_ndarray(format="rgb24")  # Decode the frame to an RGB format
    frame, _ = live_process_frame.process(frame, pose)  # Process the frame for squat analysis
    return av.VideoFrame.from_ndarray(frame, format="rgb24")  # Encode the processed frame

# Function to handle video recording output
def out_recorder_factory() -> MediaRecorder:
    return MediaRecorder(output_video_file)

# WebRTC streamer to handle real-time webcam input
ctx = webrtc_streamer(
    key="Squats-pose-analysis",
    video_frame_callback=video_frame_callback,
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},  # STUN server for NAT traversal
    media_stream_constraints={"video": {"width": {'min': 480, 'ideal': 480}}, "audio": False},  # Set media constraints
    video_html_attrs=VideoHTMLAttributes(autoPlay=True, controls=False, muted=True),  # Video player attributes
    out_recorder_factory=out_recorder_factory  # Handle video output
)

# Empty placeholder for the download button
download_button = st.empty()

# Check if output video file exists and provide download option
if os.path.exists(output_video_file):
    with open(output_video_file, 'rb') as op_vid:
        download = download_button.download_button('Download Video', data=op_vid, file_name='output_live.flv')

        # Handle download state
        if download:
            st.session_state['download'] = True

# Remove the video file once it's downloaded
if os.path.exists(output_video_file) and st.session_state['download']:
    os.remove(output_video_file)
    st.session_state['download'] = False
    download_button.empty()


