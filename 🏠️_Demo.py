import streamlit as st
from streamlit_option_menu import option_menu

# Set page configuration
st.set_page_config(page_title="Posture & Squats Analysis", page_icon="🔥", layout="wide")

# Sidebar for navigation
with st.sidebar:
    selected = option_menu(
        menu_title="Main Menu",  # required
        options=["Home", "Live Posture Detection", "Upload Video for Posture", "Live Squat Detection", "Upload Video for Squats"],  # required
        icons=["house", "camera-video", "file-earmark-arrow-up", "camera-reels", "upload"],  # optional
        menu_icon="cast",  # optional
        default_index=0,  # optional
    )

# Main Section
if selected == "Home":
    st.title("Welcome to the Posture & Squats Analysis App! 🔥")
    st.write("""
        ## Features:
        - **Posture Detection**: Analyze your posture through live webcam or by uploading a video.
        - **Squat Analysis**: Get feedback on your squat form, either live or through a video upload.
        
        Select an option from the sidebar to get started.
    """)
    # st.image("https://cdn.pixabay.com/photo/2017/01/31/17/13/sports-2021510_960_720.png", use_column_width=True)
    # Display the local home.webp image instead of the URL
    st.image("img/home.webp", use_column_width=True)

# Lazy load the imports for each page to prevent the webcam from auto-starting
elif selected == "Live Posture Detection":
    st.title("Live Posture Detection")
    st.write("Start the webcam to analyze your posture in real-time.")
    # Import and run the live posture detection module only when selected
    import pages.Three_Posture_Live_Stream

elif selected == "Upload Video for Posture":
    st.title("Posture Detection from Uploaded Video")
    st.write("Upload a video to analyze your posture.")
    # Import and run the upload video posture detection module only when selected
    import pages.Four_Posture_Upload_Video

elif selected == "Live Squat Detection":
    st.title("Live Squat Detection")
    st.write("Start the webcam to analyze your squats in real-time.")
    # Import and run the live squat detection module only when selected
    import pages.One_Live_Stream

elif selected == "Upload Video for Squats":
    st.title("Squat Analysis from Uploaded Video")
    st.write("Upload a video to analyze your squats.")
    # Import and run the upload video squat detection module only when selected
    import pages.Two_Upload_Video
