import os
import time
import PyPDF2
from gtts import gTTS
from google import genai
from dotenv import load_dotenv
import speech_recognition as sr
from playsound import playsound  # Faster, background audio

# --- 1. SETUP ---
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=API_KEY)
MODEL_ID = "gemini-2.5-flash" 
PDF_PATH = r"C:\Users\Computer User\Downloads\DCAP305_PRINCIPLES_OF_SOFTWARE_ENGINEERING (1).pdf"

def speak(text):
    """Converts text to speech and plays it immediately."""
    print(f"AI: {text}")
    try:
        tts = gTTS(text=text, lang='en')
        filename = "temp_voice.mp3"
        # Remove old file if it exists to avoid 'file in use' errors
        if os.path.exists(filename):
            os.remove(filename)
        tts.save(filename)
        playsound(filename) # This plays sound in the background
    except Exception as e:
        print(f"Audio Error: {e}")

def get_pdf_text(path):
    try:
        with open(path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            return "".join([p.extract_text() for p in reader.pages[:3]])
    except Exception as e:
        print(f"PDF Error: {e}")
        return None

# --- 2. MAIN EXECUTION ---
if __name__ == "__main__":
    # TEST GREETING - If you don't hear this, your speakers/gTTS are the issue
    print("Testing audio...")
    speak("Hello! I am starting the software engineering tutor. Please wait while I read your PDF.")
    
    context = get_pdf_text(PDF_PATH)
    score, total = 0, 0
    
    if context:
        while True:
            try:
                # Generate Question
                prompt = f"Context: {context}\nTask: Ask 1 short Software Engineering question."
                response = client.models.generate_content(model=MODEL_ID, contents=prompt)
                
                question = response.text
                speak(question)
                
                # Listen for Answer
                r = sr.Recognizer()
                with sr.Microphone() as source:
                    print("Listening...")
                    audio = r.listen(source, timeout=10)
                    user_reply = r.recognize_google(audio)
                
                if user_reply.lower() in ["stop", "exit"]:
                    speak(f"Final score: {score}/{total}. Goodbye!")
                    break
                
                # Grade Answer
                total += 1
                grade_req = f"Q: {question}\nAns: {user_reply}\nIs it correct? Say 'Correct' or 'Incorrect' and explain."
                feedback = client.models.generate_content(model=MODEL_ID, contents=grade_req).text
                
                if "CORRECT" in feedback.upper():
                    score += 1
                
                speak(f"{feedback} Score: {score} out of {total}.")
                time.sleep(2)

            except Exception as e:
                print(f"Session Error: {e}")
                speak("I had trouble hearing that. Let's try again.")
    else:
        print("Failed to start. Check your PDF path and API Key.")
