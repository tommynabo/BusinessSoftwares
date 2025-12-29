import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from contextlib import asynccontextmanager
from .transcribe import transcribe_audio, mock_transcribe_audio
from .research import scrape_linkedin_profile, scrape_website, mock_research
from .strategist import generate_proposal_data, mock_generate_strategy
from .generate_pdf import generate_pdf, mock_generate_pdf

app = FastAPI()

# Configuration
DRY_RUN = os.environ.get("DRY_RUN", "False").lower() == "true"

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for Vercel previews/prod
    allow_credentials=False, # Must be False when allow_origins is "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "service": "Autonomous Sales Engineering Agent"}

import asyncio
from concurrent.futures import ThreadPoolExecutor

@app.post("/api/generate-proposal") # Prefix with /api for Vercel rewrite matching
async def generate_proposal(
    linkedin_url: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Main orchestration endpoint.
    1. Save Audio
    2. Transcribe & Research (PARALLEL)
    3. Strategize
    4. Generate PDF
    """
    # Vercel only allows writing to /tmp
    temp_filename = f"/tmp/temp_{file.filename}"
    
    try:
        # 1. Save File
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        loop = asyncio.get_event_loop()
        executor = ThreadPoolExecutor()

        # Define wrapper functions for blocking calls
        def run_transcription():
            if DRY_RUN:
                return mock_transcribe_audio()
            return transcribe_audio(temp_filename)

        def run_research():
            if DRY_RUN:
                return mock_research(linkedin_url)
            
            l_data = scrape_linkedin_profile(linkedin_url)
            w_data = {}
            if "website" in l_data and l_data["website"]:
                w_data = scrape_website(l_data["website"])
            
            return {
                "linkedin": l_data,
                "website": w_data
            }

        # 2. Upload & Transcribe + 3. Research (PARALLEL EXECUTION)
        # using run_in_executor to not block the main loop
        future_transcript = loop.run_in_executor(executor, run_transcription)
        future_research = loop.run_in_executor(executor, run_research)

        transcript, research_data = await asyncio.gather(future_transcript, future_research)

        # 4. Strategize
        if DRY_RUN:
            proposal_json = mock_generate_strategy()
        else:
            proposal_json = generate_proposal_data(transcript, research_data)
        
        # 5. Generate PDF
        if DRY_RUN:
            pdf_url = mock_generate_pdf(proposal_json)
        else:
            pdf_url = generate_pdf(proposal_json)
            if not pdf_url:
                raise HTTPException(status_code=500, detail="PDF Generation failed")

        return {
            "status": "success",
            "pdf_url": pdf_url,
            "data_used": {
                "transcript_snippet": transcript[:100] + "...",
                "company_detected": proposal_json.get("company_name", "N/A")
            }
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Cleanup
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
