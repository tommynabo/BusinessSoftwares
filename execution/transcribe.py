import os
import time
from groq import Groq

# Initialize Groq client
# Ensure GROQ_API_KEY is set in your environment variables
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def transcribe_audio(file_path: str, fallback: bool = True) -> str:
    """
    Transcribes audio file using Groq's Distil-Whisper model.
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found at {file_path}")
        
        print(f"Starting transcription for {file_path} using Groq...")
        start_time = time.time()
        
        with open(file_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(file_path, file.read()),
                model="distil-whisper-large-v3-en",
                response_format="text" # or json/verbose_json
            )
        
        duration = time.time() - start_time
        print(f"Transcription complete in {duration:.2f}s")
        
        return transcription

    except Exception as e:
        print(f"Groq Transcription failed: {str(e)}")
        if fallback:
             # Placeholder for OpenAI Whisper fallback if needed
             # return transcribe_with_openai(file_path)
             raise e
        else:
            raise e

# Mock function for local testing without API
def mock_transcribe_audio() -> str:
    return "This is a mock transcription of a sales call where the client expressed interest in the Sales Sniper system and mentioned a budget of $2000 for setup. They are currently struggling with manual prospecting and low conversion rates."
