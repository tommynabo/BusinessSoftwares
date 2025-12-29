import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are an expert AI Solutions Architect creating a high-converting business proposal.
Your goal is to analyze the provided Sales Call Transcript and Research Data to generate a JSON payload for a proposal PDF.

Resources:
- Pricing Structure: {pricing_info}

Input Data:
- Transcript: {transcript}
- LinkedIn/Web Data: {research_data}

Instructions:
1. Analyze the transcript for identifying client pain points and their specific needs.
2. Determine which Systems (Sales Sniper, Content Engine, Custom Architecture) are relevant.
3. Check if specific pricing was negotiated in the call. If yes, use that. If no, use the Standard Pricing.
4. Output STRICT JSON matching the following schema structure. Do not include markdown code blocks.

JSON Schema:
{{
  "company_name": "string",
  "prospect_name": "string",
  "date": "string",
  "executive_summary": "string (The hook)",
  "diagnosis_text": "string (Why current state is bad)",
  "pain_points": ["string", "string", ...],
  "systems": [
    {{
      "title": "string",
      "description": "string",
      "impact": "string"
    }}
  ],
  "roi_metrics": [
    {{ "value": "string", "label": "string" }}
  ],
  "efficiency_charts": [
    {{ "label": "string", "percentage": number 0-100 }}
  ],
  "pricing_items": [
    {{ "name": "string", "setup_price": "string", "monthly_price": "string" }}
  ],
  "total_setup": "string",
  "total_monthly": "string",
  "cta_link": "string"
}}
"""

def load_pricing():
    try:
        with open("assets/pricing.md", "r") as f:
            return f.read()
    except:
        return "Standard Pricing: Sales Sniper ($2.5k setup, $500/mo), Content Engine ($3k setup, $750/mo)."

def generate_proposal_data(transcript: str, research_data: dict) -> dict:
    pricing_info = load_pricing()
    
    formatted_prompt = SYSTEM_PROMPT.format(
        pricing_info=pricing_info,
        transcript=transcript,
        research_data=json.dumps(research_data)
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", # or o1-mini if available/needed
            messages=[
                {"role": "system", "content": "You are a helpful assistant that outputs JSON only."},
                {"role": "user", "content": formatted_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
        
    except Exception as e:
        print(f"Strategy generation failed: {str(e)}")
        # Return fallback dummy data in case of error
        return {
            "company_name": "Unknown",
             "prospect_name": "Valued Client",
             "executive_summary": "Error generating strategy.",
             "systems": []
        }

def mock_generate_strategy() -> dict:
    return {
        "company_name": "Acme Corp",
        "prospect_name": "John Doe",
        "date": "2023-10-27",
        "executive_summary": "Acme Corp is struggling to scale outreach. We propose automating the sales pipeline.",
        "diagnosis_text": "Current manual processes are bottlenecking growth.",
        "pain_points": ["Low conversion", "Manual data entry", "Inconsistent content"],
        "systems": [
            {"title": "The Sales Sniper", "description": "Automated outreach system.", "impact": "10x Leads"},
            {"title": "The Content Engine", "description": "Auto-generate LinkedIn posts.", "impact": "Thought Leadership"}
        ],
        "roi_metrics": [
            {"value": "10h+", "label": "Saved Weekly"},
            {"value": "3x", "label": "Lead Volume"}
        ],
        "efficiency_charts": [
             {"label": "Current Efficiency", "percentage": 20},
             {"label": "With AI Systems", "percentage": 95}
        ],
        "pricing_items": [
             {"name": "The Sales Sniper", "setup_price": "$2,500", "monthly_price": "$500"},
             {"name": "The Content Engine", "setup_price": "$3,000", "monthly_price": "$750"}
        ],
        "total_setup": "$5,500",
        "total_monthly": "$1,250",
        "cta_link": "https://calendly.com/example"
    }
