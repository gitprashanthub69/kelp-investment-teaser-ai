import os
import sys

# Add the backend directory to sys.path so we can import app
sys.path.append(os.path.join(os.getcwd()))

from app.services.ppt_generator import PPTGenerator
from app.services.intelligence import IntelligenceService
import json

def test_dynamic_financials():
    print("Testing dynamic financials for two different scales...")
    
    # 1. Test case: Startup (Small scale)
    startup_data = {
        "company_name": "TechStart Solutions",
        "sector": "Technology / SaaS",
        "tagline": "Disrupting the Enterprise",
        "scraped_text": "TechStart is a seed-stage startup with early traction. The team of 5 has built a prototype."
    }
    
    # 2. Test case: Enterprise (Large scale)
    enterprise_data = {
        "company_name": "Global Manufacturing Corp",
        "sector": "B2B Manufacturing",
        "tagline": "Industrial Excellence",
        "scraped_text": "Global Manufacturing Corp is a Fortune 500 company with 50,000 employees and hundreds of factories worldwide. Annual revenues exceed 10 billion dollars."
    }
    
    for case in [startup_data, enterprise_data]:
        print(f"\nProcessing: {case['company_name']}")
        narrative = IntelligenceService.generate_narrative(
            sector=case['sector'],
            financial_data={}, # No real data, force fallback
            kpis={},
            scraped_text=case['scraped_text']
        )
        
        # Check if AI estimated financials
        fin = narrative.get("financials", {})
        print(f"Estimated Revenue: {fin.get('revenue', 'Missing')}")
        
        # Generate PPT
        output = f"test_dynamic_{case['company_name'].replace(' ', '_')}.pptx"
        gen = PPTGenerator(output, {
            "project_name": case['company_name'],
            "sector": case['sector'],
            "financials": fin,
            "narrative": narrative
        })
        gen.generate()
        print(f"Saved: {output}")

if __name__ == "__main__":
    test_dynamic_financials()
