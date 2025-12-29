import os
import requests
from bs4 import BeautifulSoup
from apify_client import ApifyClient

# Ensure APIFY_API_TOKEN is set in env
apify_client = ApifyClient(os.environ.get("APIFY_API_TOKEN"))

def scrape_linkedin_profile(profile_url: str) -> dict:
    """
    Scrapes LinkedIn profile using Apify's linkedin-profile-scraper.
    """
    print(f"Scraping LinkedIn profile: {profile_url}")
    try:
        run_input = {
            "startUrls": [{"url": profile_url}],
            "minDelay": 1,
            "maxDelay": 10,
            "proxy": {
                "useApifyProxy": True,
                "apifyProxyGroups": ["RESIDENTIAL"]
            }
        }
        
        # Run the actor
        run = apify_client.actor("use-compiled-actor-id-here").call(run_input=run_input)
        
        # Fetch results
        dataset = apify_client.dataset(run["defaultDatasetId"]).list_items().items
        if dataset:
            return dataset[0] # Return first result
        return {}

    except Exception as e:
        print(f"LinkedIn scraping failed: {str(e)}")
        return {}

def scrape_website(url: str) -> dict:
    """
    Scrapes the homepage and 'About' page for meta tags and headers.
    """
    data = {"url": url, "homepage_text": "", "about_text": ""}
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        # Homepage
        print(f"Scraping homepage: {url}")
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            # Extract H1, H2, Meta Description
            data["homepage_text"] += " ".join([h.get_text() for h in soup.find_all(['h1', 'h2'])])
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                data["homepage_text"] += " " + meta_desc.get('content')

        # About page (guess URL)
        # Simple heuristic: try /about, /about-us
        about_url = url.rstrip('/') + "/about"
        print(f"Scraping about page: {about_url}")
        resp_about = requests.get(about_url, headers=headers, timeout=10)
        if resp_about.status_code == 200:
             soup_about = BeautifulSoup(resp_about.text, 'html.parser')
             data["about_text"] += " ".join([h.get_text() for h in soup_about.find_all(['h1', 'h2', 'p'])[:5]]) # First few paragraphs

    except Exception as e:
        print(f"Website scraping failed: {str(e)}")
    
    return data

# Mock function
def mock_research(linkedin_url: str) -> dict:
    return {
        "linkedin": {
            "fullName": "John Doe",
            "occupation": "CEO",
            "company": "Acme Corp",
            "website": "https://example.com"
        },
        "website": {
            "homepage_text": "We help companies scale with manual labor.",
            "about_text": "Founded in 2010 to provide manual services."
        }
    }
