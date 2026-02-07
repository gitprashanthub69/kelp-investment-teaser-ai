import os
import sys
from dotenv import load_dotenv

# Add the current directory to sys.path
sys.path.append(os.getcwd())

from app.services.ppt_generator import PPTGenerator
from app.services.intelligence import IntelligenceService

def test_generation():
    load_dotenv()
    
    output_path = "test_output_v2.pptx"
    
    # Dummy data designed to trigger various logic paths
    data = {
        "project_id": 999,
        "company_name": "Reliance Industries", 
        "sector": "Chemicals / Specialty",
        "financials": {
            "years": ["FY21", "FY22", "FY23", "FY24"],
            "revenue": [1000, 1200, 1500, 1900],
            "ebitda": [150, 200, 280, 380],
            "pat": [80, 110, 160, 240]
        },
        "narrative": {
            "slide_1": {
                "biz_desc": "The Company is a leading player in the chemicals industry with global operations. This is a longer description to test word wrap and potential overlaps in the snippet box below the header.",
                "customers": ["Tata Motors", "Amazon India", "Infosys", "Wipro", "HDFC Bank", "Cipla Limited"],
                "assets": [
                    {"label": "Manufacturing\\nUnits", "value": "15"},
                    {"label": "R&D\\nCenters", "value": "4"},
                    {"label": "Employees", "value": "20,000+"},
                    {"label": "Countries", "value": "50+"}
                ],
                "certifications": ["ISO 9001", "WHO-GMP", "FDA", "ISO 14001", "REACH"],
                "product_portfolio": [
                    {"category": "Specialty Chemicals", "details": "High purity solvents and reagents for pharma"},
                    {"category": "Polymers", "details": "Advanced polymer solutions for industrial apps"},
                    {"category": "Agro Solutions", "details": "Sustainable crop protection products"},
                    {"category": "Research Services", "details": "Custom synthesis and formulation services"}
                ],
                "applications": [
                    {"industry": "Pharmaceuticals", "share": "45%"},
                    {"industry": "Automotive", "share": "25%"},
                    {"industry": "Agriculture", "share": "20%"},
                    {"industry": "Others", "share": "10%"}
                ],
                "revenue_split": {"Domestic": 60, "Export": 40}
            },
            "slide_3": {
                "investment_highlights": [
                    {"title": "Global Market Leader", "desc": "Dominant market share in specialty segments with high entry barriers and sticky customer base."},
                    {"title": "Vertical Integration", "desc": "Fully integrated supply chain from raw material to finished products ensuring quality and margin."},
                    {"title": "Innovation Driven", "desc": "Strong R&D pipeline with 50+ patents and continuous focus on new product development."},
                    {"title": "Strong Financials", "desc": "Consistent 20% CAGR with healthy EBITDA margins and strong cash-flow generation."},
                    {"title": "Strategic Locations", "desc": "Manufacturing facilities located near major ports and industrial clusters for logistics efficiency."},
                    {"title": "Experienced Management", "desc": "Led by industry veterans with deep domain expertise and proven execution track record."}
                ],
                "why_invest": "Reliance Industries represents a unique investment opportunity combining scale, innovation, and strong financial performance. Its diversified portfolio and global reach provide a solid foundation for continued growth and value creation in the specialty chemicals space."
            }
        },
        "generated_images": {},
        "kpis": {"Growth": "25%", "Margin": "18%"}
    }
    
    print(f"Starting test generation to: {output_path}")
    try:
        generator = PPTGenerator(output_path, data)
        generator.generate()
        print(f"SUCCESS: PPT generated at {output_path}")
        print("Please manually check the file for font sizes and logo fetching results.")
    except Exception as e:
        print(f"FAILURE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_generation()
