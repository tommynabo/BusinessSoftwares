import os
import requests
import json

# Ensure PDFMONKEY_API_KEY is set in env
PDFMONKEY_API_KEY = os.environ.get("PDFMONKEY_API_KEY")

def generate_pdf(data: dict, template_key: str = None) -> str:
    """
    Sends data to PDFMonkey to generate a document.
    """
    url = "https://api.pdfmonkey.io/api/v1/documents"
    
    # If using a specific template ID created in PDFMonkey dashboard:
    # payload = {"document": {"document_template_id": template_key, "payload": data, "status": "pending"}}
    
    # For dynamic HTML (if PDFMonkey allows custom HTML payload via API directly, typically you reference a Template ID)
    # Assuming we have a registered Template ID in env or passed in. 
    # NOTE: The User Instructions implied creating a template locally. 
    # Usually you upload the template to PDFMonkey and get an ID. 
    # For this script, we'll assume we pass the data to a template ID.
    
    # REAL implementation requires a Template ID. 
    template_id = os.environ.get("PDFMONKEY_TEMPLATE_ID", "your-template-id")
    
    payload = {
        "document": {
            "document_template_id": template_id,
            "payload": data,
            "status": "pending" 
        }
    }
    
    headers = {
        "Authorization": f"Bearer {PDFMONKEY_API_KEY}",
        "Content-Type": "application/json"
    }

    print(f"Generating PDF with Template ID: {template_id}")
    
    try:
        resp = requests.post(url, json=payload, headers=headers)
        if resp.status_code in [200, 201]:
            doc = resp.json()
            # PDFMonkey processes async? Usually returns a document object.
            # We might need to poll or if it's instant (or returns a download_url if complete)
            
            # Simple assumption: return the download_url or preview_url
            # Often need to confirm 'status' is 'success'
            doc_id = doc["document"]["id"]
            return f"https://dashboard.pdfmonkey.io/documents/{doc_id}/download" 
        else:
            print(f"PDFMonkey Error: {resp.text}")
            return None
    except Exception as e:
        print(f"PDF Generation Failed: {str(e)}")
        return None

def mock_generate_pdf(data: dict) -> str:
    return "https://pdfmonkey.io/mock-download-url.pdf"
