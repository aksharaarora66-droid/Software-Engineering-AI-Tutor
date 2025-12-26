import streamlit as st
import os
from google import genai
from google.genai import types
import speech_recognition as sr
from io import BytesIO

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="AI Voice Tutor", page_icon="🎤")
st.title("🎓 Software Engineering AI Tutor")

# Configure GenAI (Use secrets for deployment)
# Locally, this falls back to an environment variable
api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

# --- 2. THE LOGIC ---

def get_ai_response(user_text):
    """Sends transcribed text to Gemini and returns the text response."""
    prompt = f"You are a helpful Software Engineering Tutor. Answer this: {user_text}"
    response = client.models.generate_content(
        model="gemini-2.0-flash", 
        contents=prompt
    )
    return response.text

def transcribe_audio(audio_bytes):
    """Converts the recorded audio bytes into text."""
    recognizer = sr.Recognizer()
    audio_file = BytesIO(audio_bytes)
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio_data)
    except:
        return "Could not understand audio."

# --- 3. THE UI ---

# Streamlit's built-in microphone widget
audio_value = st.audio_input("Record your question")

if audio_value:
    st.audio(audio_value) # Play back what you recorded
    
    with st.spinner("Transcribing..."):
        user_text = transcribe_audio(audio_value.read())
        st.write(f"**You said:** {user_text}")
    
    with st.spinner("Tutor is thinking..."):
        ai_text = get_ai_response(user_text)
        st.subheader("Tutor Response:")
        st.write(ai_text)
        
        # Note: For actual Voice output, you would use a TTS library 
        # or Gemini's native TTS features here.
