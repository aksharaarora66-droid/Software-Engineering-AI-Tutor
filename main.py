import streamlit as st
from google import genai
from dotenv import load_dotenv
import speech_recognition as sr
import os

# --- 1. SETUP ---
load_dotenv()

# Streamlit UI Header
st.title("Software Engineering AI Tutor")
st.write("Click the button below and speak to start.")

# --- 2. AUDIO FUNCTION ---
def play_response_audio(file_path):
    """
    Plays audio through the user's browser.
    'playsound' is removed because it doesn't work on cloud servers.
    """
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            audio_bytes = f.read()
            st.audio(audio_bytes, format="audio/mp3", autoplay=True)
    else:
        st.error("Audio file not found.")

# --- 3. CORE LOGIC ---
# Example placement of audio trigger
if st.button("Listen to Tutor"):
    # Insert your speech-to-text or GenAI logic here
    st.info("Playing response...")
    
    # Replace 'response.mp3' with your actual filename
    # play_response_audio("response.mp3")
