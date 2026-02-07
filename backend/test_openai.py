import os
import sys
from dotenv import load_dotenv

# Add the current directory to sys.path to find 'app'
sys.path.append(os.getcwd())

from app.services.openai_service import get_openai_service

def test_openai():
    load_dotenv()
    service = get_openai_service()
    
    print(f"API Key available: {bool(service.api_key)}")
    print(f"Client available: {service.is_available()}")
    
    if not service.is_available():
        print("Error: OpenAI client not initialized.")
        return

    print("Testing narrative generation...")
    context = {
        "sector": "Tech / B2B SaaS",
        "financial_highlights": "Available",
        "text_summary": "The Company belongs to the SaaS space, offering a subscription-based platform for enterprise resource planning. They have grown 20% year-on-year."
    }
    
    try:
        res = service.generate_dense_narrative("slide_1", "Tech / B2B SaaS", context)
        print("Result for slide_1:")
        import json
        print(json.dumps(res, indent=2))
        
        if res and "biz_desc" in res and res["biz_desc"] != "Business description unavailable.":
            print("SUCCESS: OpenAI generated real content.")
        else:
            print("FAILURE: OpenAI returned defaults or empty content.")
            
    except Exception as e:
        print(f"CRITICAL ERROR during OpenAI call: {e}")

if __name__ == "__main__":
    test_openai()
