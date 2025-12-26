import streamlit as st
import os
from google import genai
import PyPDF2
import io

# --- 1. SETUP & CONFIGURATION ---
st.set_page_config(page_title="Software Engineering AI Tutor", page_icon="🎓", layout="wide")

# Securely fetch API Key from Streamlit Secrets
api_key = st.secrets.get("GOOGLE_API_KEY")

if not api_key:
    st.error("API Key not found. Please add GOOGLE_API_KEY to your Streamlit Secrets.")
    st.stop()

# Initialize Client with explicit stable API version to prevent 404 errors
client = genai.Client(api_key=api_key, http_options={'api_version': 'v1'})

# Using the most stable model ID for the current GenAI SDK
MODEL_ID = "gemini-1.5-flash"

# --- 2. UI LAYOUT ---
st.title("🎓 Software Engineering AI Tutor")

if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "last_question" not in st.session_state:
    st.session_state.last_question = None

# Sidebar for Uploads
with st.sidebar:
    st.header("📂 Study Materials")
    uploaded_file = st.file_uploader("Upload SE Notes (PDF)", type="pdf")
    
    if st.button("Clear History"):
        st.session_state.last_question = None
        st.rerun()

# --- 3. LOGIC & EXTRACTION ---
def extract_text(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        # Limit to first 5 pages to stay within free tier limits
        for page in pdf_reader.pages[:5]:
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

# --- 4. MAIN APP CONTENT ---
if uploaded_file:
    with st.spinner("AI is reading your notes..."):
        context_text = extract_text(uploaded_file)
    st.success(f"✅ Loaded: {uploaded_file.name}")

    st.subheader("📝 Practice Quiz")
    
    if st.button("✨ Generate a New Question"):
        with st.spinner("🧠 Thinking..."):
            try:
                prompt = f"""
                You are a Software Engineering Professor. 
                Based on this context, generate ONE multiple-choice question.
                Format clearly with:
                - Question
                - Options (A, B, C, D)
                - Correct Answer
                - Brief Explanation
                
                Context: {context_text[:5000]}
                """
                
                # Generating content using the stable v1 API
                response = client.models.generate_content(model=MODEL_ID, contents=prompt)
                st.session_state.last_question = response.text
                
            except Exception as e:
                st.error(f"Technical Error: {e}")

    # Display the result
    if st.session_state.last_question:
        st.info("### Your AI-Generated Question:")
        st.markdown(st.session_state.last_question)
else:
    st.info("Please upload a PDF in the sidebar to begin!")

# --- 5. FOOTER ---
st.markdown("---")
st.caption("Built with Google GenAI SDK v1.56.0 | Deployment: Streamlit Cloud")
