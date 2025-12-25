import streamlit as st
import os
import PyPDF2
from google import genai
from gtts import gTTS
import base64
from streamlit_mic_recorder import speech_to_text
from dotenv import load_dotenv

# --- INITIALIZATION ---
load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL_ID = "gemini-2.5-flash"

st.set_page_config(page_title="AI SE Tutor", page_icon="🎓", layout="wide")

# Persistent State
if "score" not in st.session_state:
    st.session_state.score = 0
    st.session_state.total = 0
    st.session_state.current_question = ""
    st.session_state.pdf_text = ""

# --- FUNCTIONS ---
def autoplay_audio(text):
    tts = gTTS(text=text, lang='en')
    tts.save("temp.mp3")
    with open("temp.mp3", "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
        st.markdown(md, unsafe_allow_html=True)

def get_new_question():
    prompt = f"Context: {st.session_state.pdf_text}\nTask: Ask 1 short Software Engineering question."
    response = client.models.generate_content(model=MODEL_ID, contents=prompt)
    st.session_state.current_question = response.text

# --- UI LAYOUT ---
st.title("🎓 Software Engineering AI Tutor")

with st.sidebar:
    st.header("Settings")
    uploaded_file = st.file_uploader("Upload your SE PDF", type="pdf")
    if uploaded_file and not st.session_state.pdf_text:
        reader = PyPDF2.PdfReader(uploaded_file)
        st.session_state.pdf_text = "".join([p.extract_text() for p in reader.pages[:5]])
        st.success("PDF Loaded!")

    st.divider()
    st.metric("Score", f"{st.session_state.score} / {st.session_state.total}")
    if st.button("Reset Score"):
        st.session_state.score = 0
        st.session_state.total = 0
        st.rerun()

# --- MAIN INTERFACE ---
if st.session_state.pdf_text:
    if st.button("Generate Next Question") or not st.session_state.current_question:
        get_new_question()
        autoplay_audio(st.session_state.current_question)

    st.info(f"**Question:** {st.session_state.current_question}")

    st.write("Click the mic to answer:")
    # Browser-based Microphone
    text_input = speech_to_text(language='en', start_prompt="🎤 Start Speaking", stop_prompt="⏹️ Stop", just_once=True)

    if text_input:
        st.write(f"**You said:** {text_input}")
        st.session_state.total += 1
        
        grade_req = f"Q: {st.session_state.current_question}\nAns: {text_input}\nIs it correct? Say 'CORRECT' or 'INCORRECT' and explain."
        feedback = client.models.generate_content(model=MODEL_ID, contents=grade_req).text
        
        if "CORRECT" in feedback.upper():
            st.session_state.score += 1
            st.balloons() # Visual celebration!
        
        st.success(feedback) if "CORRECT" in feedback.upper() else st.error(feedback)
        autoplay_audio(feedback)
else:
    st.warning("Please upload a PDF in the sidebar to start.")