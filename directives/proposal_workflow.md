# Proposal Generation Workflow

## Objective
Generate a hyper-personalized Business Proposal PDF from a sales call audio file and a LinkedIn URL.

## Inputs
- **Audio File**: `mp3` or `m4a` file of the sales call.
- **LinkedIn URL**: URL of the prospect's LinkedIn profile.

## Outputs
- **PDF URL**: Download link for the generated PDF proposal.

## Workflow Steps

### 1. Ingest
- Receive audio file and LinkedIn URL via API endpoint.

### 2. Transcribe (Layer 1)
- **Tool**: Groq API (Distil-Whisper).
- **Fallback**: OpenAI Whisper API.
- **Output**: Full transcript text.

### 3. Research (Layer 2)
- **LinkedIn**: Scrape profile using Apify (`linkedin-profile-scraper`). Extract role, company, and website.
- **Company Website**: If website URL exists, scrape Homepage and About page for value proposition.
- **Constraint**: Limit scraping to essential context to save time.

### 4. Strategize (Layer 3)
- **Model**: OpenAI `gpt-4o-mini` (or `o1-mini`).
- **Context**: Transcript + LinkedIn Data + Web Data + `assets/pricing.md`.
- **Logic**:
    - Identify pain points.
    - Match to "Systems" (Sales Sniper, Content Engine, Custom Architecture).
    - Detect price negotiations (override standard pricing if found).
- **Output**: JSON payload matching PDFMonkey template variables.

### 5. Generate PDF (Layer 4)
- **Tool**: PDFMonkey.
- **Template**: `templates/proposal_layout.html` + `templates/proposal_style.css`.
- **Action**: Send JSON payload to PDFMonkey API.
- **Result**: Return PDF download URL.

## Edge Cases
- **No Website Found**: Skip website scraping, rely on LinkedIn and Audio.
- **Transcription Fail**: Retry with fallback provider.
- **No Pricing Mentioned**: Use standard pricing from `assets/pricing.md`.
