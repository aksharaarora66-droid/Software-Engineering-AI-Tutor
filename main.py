import streamlit as st
import os
from google import genai
import PyPDF2
import io

# --- 1. SETUP & CONFIGURATION ---
# Using version 1.56.0 of the GenAI SDK
st.set_page_config(page_title="Software Engineering AI Tutor", page_icon="🎓", layout="wide")

# Get API Key from Streamlit Secrets (Professional Security Standard)
api_key = st.secrets.get("GOOGLE_API_KEY")

if not api_key:
    st.error("API Key not found. Please check your Streamlit Secrets.")
    st.stop()

# Initialize the Client for version 1.56.0
# Initialize the Client with explicit API version
client = genai.Client(api_key=api_key, http_options={'api_version': 'v1'})

# The correct Model ID format for this SDK version
MODEL_ID = "gemini-1.5-flash-latest"

# --- 2. APP UI ---
st.title("🎓 Software Engineering AI Tutor")

# --- 3. THE ONBOARDING GUIDANCE (UX Design) ---
if "uploaded_file" not in st.session_state or st.session_state.uploaded_file is None:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("### ⬅️ Start Here")
        st.info("Please use the **sidebar on the left** to upload your Software Engineering PDF notes.")
    with col2:
        st.markdown("""
        ### How it works:
        1. **Upload** your PDF in the sidebar.
        2. **Wait** for the AI to read your notes.
        3. **Quiz Yourself** with AI-generated questions!
        """)
    st.divider()

# Sidebar for PDF Upload
with st.sidebar:
    st.header("📂 Upload Section")
    uploaded_file = st.file_uploader("Upload your SE Notes (PDF)", type="pdf", key="pdf_uploader")
    st.session_state.uploaded_file = uploaded_file 
    
    if st.button("Clear History"):
        st.session_state.chat_history = []
        st.session_state.last_question = None
        st.rerun()

# --- 4. LOGIC ---
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

if uploaded_file:
    # PDF Processing Feedback
    with st.spinner("Reading PDF..."):
        context_text = extract_text_from_pdf(uploaded_file)
    st.success(f"✅ Successfully loaded: {uploaded_file.name}")

    st.subheader("📝 Practice Quiz")
    
    if st.button("✨ Generate a New Question"):
        # Spinner for professional UI during API latency
        with st.spinner("🧠 AI is analyzing your notes and thinking..."):
            try:
                prompt = f"""
                You are a Software Engineering Professor. 
                Based on the following text, generate ONE multiple-choice question.
                Format:
                **Question:** (The question here)
                **Options:** (A, B, C, D)
                **Correct Answer:** (The answer)
                **Explanation:** (Why it's correct)
                
                Context: {context_text[:5000]}
                """
                
                # API Call using version 1.56.0 syntax
                response = client.models.generate_content(model=MODEL_ID, contents=prompt)
                st.session_state.last_question = response.text
                
            except Exception as e:
                # Handle Quota (429) or other API errors gracefully
                st.error(f"Technical Error: {e}")

    # Display the generated question in a professional card
    if st.session_state.get('last_question'):
        st.container(border=True).markdown(st.session_state.last_question)

# --- 5. FOOTER ---
st.markdown("---")
st.caption("Developed with Google GenAI SDK v1.56.0 | AI Tutor v1.0")
