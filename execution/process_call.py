import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from contextlib import asynccontextmanager
from execution.transcribe import transcribe_audio, mock_transcribe_audio
from execution.research import scrape_linkedin_profile, scrape_website, mock_research
from execution.strategist import generate_proposal_data, mock_generate_strategy
from execution.generate_pdf import generate_pdf, mock_generate_pdf

app = FastAPI()

# Configuration
DRY_RUN = os.environ.get("DRY_RUN", "False").lower() == "true"

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for Vercel previews/prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "service": "Autonomous Sales Engineering Agent"}

@app.post("/api/generate-proposal") # Prefix with /api for Vercel rewrite matching
async def generate_proposal(
    linkedin_url: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Main orchestration endpoint.
    1. Save Audio
    2. Transcribe
    3. Research
    4. Strategize
    5. Generate PDF
    """
    # Vercel only allows writing to /tmp
    temp_filename = f"/tmp/temp_{file.filename}"
    
    try:
        # 1. Save File
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 2. Transcribe
        if DRY_RUN:
            transcript = mock_transcribe_audio()
        else:
            transcript = transcribe_audio(temp_filename)

        # 3. Research
        if DRY_RUN:
            research_data = mock_research(linkedin_url)
        else:
            linkedin_data = scrape_linkedin_profile(linkedin_url)
            website_data = {}
            # If scraping found a website, scrape it too
            if "website" in linkedin_data and linkedin_data["website"]:
                website_data = scrape_website(linkedin_data["website"])
            
            research_data = {
                "linkedin": linkedin_data,
                "website": website_data
            }

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
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Cleanup
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
