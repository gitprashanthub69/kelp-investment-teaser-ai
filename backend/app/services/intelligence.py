"""
Intelligence Service - Enhanced Narrative Generation for Sample Output Style
Generates comprehensive data for PPT including customers, assets, certifications, investment highlights
"""

import os
import re
import json
from typing import Dict, Any, Optional, List

try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class IntelligenceService:
    """Generates rich narrative data for investment teasers"""
    
    SECTORS = {
        "Pharma / Healthcare": {
            "keywords": ["pharma", "pharmaceutical", "drug", "api", "hospital", "clinical", 
                        "healthcare", "medtech", "diagnostic", "therapy", "biotech", "medicine",
                        "formulation", "generic", "crams", "cmo", "cdmo"],
            "certifications": ["WHO-GMP", "FDA", "EU-GMP", "ISO 9001", "ISO 14001"],
            "customers": ["Sun Pharma", "Cipla", "Lupin", "Dr. Reddy's", "Zydus", "Torrent"]
        },
        "Technology / SaaS": {
            "keywords": ["software", "saas", "tech", "platform", "cloud", "api", 
                        "subscription", "data", "ai", "machine learning", "analytics"],
            "certifications": ["ISO 27001", "SOC 2", "GDPR", "HIPAA", "ISO 9001"],
            "customers": ["TCS", "Infosys", "Wipro", "HCL", "Tech Mahindra", "Accenture"]
        },
        "B2B Manufacturing": {
            "keywords": ["manufacturing", "factory", "plant", "production", "machining",
                        "forge", "industrial", "engineering", "oem", "component",
                        "precision", "tooling", "stamping", "casting", "die"],
            "certifications": ["ISO 9001", "IATF 16949", "ISO 14001", "OHSAS 18001", "AS9100"],
            "customers": ["Tata Motors", "M&M", "Maruti", "Bosch", "L&T", "BHEL"]
        },
        "Chemicals / Specialty": {
            "keywords": ["chemical", "specialty", "polymer", "solvent", "surfactant",
                        "compound", "formulation", "ingredients", "petrochemical"],
            "certifications": ["ISO 9001", "ISO 14001", "REACH", "Responsible Care", "GMP"],
            "customers": ["Asian Paints", "Pidilite", "BASF", "UPL", "Reliance", "Tata Chemicals"]
        },
        "Consumer / D2C": {
            "keywords": ["consumer", "d2c", "brand", "retail", "ecommerce", "amazon",
                        "flipkart", "lifestyle", "fashion", "fmcg", "personal care"],
            "certifications": ["FSSAI", "ISO 22000", "HACCP", "BRC", "Organic Certified"],
            "customers": ["Amazon", "Flipkart", "BigBasket", "Reliance Retail", "DMart", "Nykaa"]
        },
        "Food & Beverage": {
            "keywords": ["food", "beverage", "snack", "dairy", "bakery", "confectionery"],
            "certifications": ["FSSAI", "ISO 22000", "FSSC 22000", "HACCP", "BRC"],
            "customers": ["ITC", "Nestle", "Britannia", "Parle", "HUL", "PepsiCo"]
        },
        "Fintech": {
            "keywords": ["fintech", "payment", "banking", "lending", "insurance", "neobank"],
            "certifications": ["RBI License", "PCI DSS", "ISO 27001", "SOC 2", "IRDAI"],
            "customers": ["HDFC Bank", "ICICI", "SBI", "Bajaj Finance", "Axis Bank", "Kotak"]
        },
        "Logistics / Supply Chain": {
            "keywords": ["logistics", "warehouse", "fleet", "transport", "supply chain", "3pl"],
            "certifications": ["ISO 9001", "AEO", "GDP", "IATA", "C-TPAT"],
            "customers": ["Amazon", "Flipkart", "Reliance", "BigBasket", "Delhivery", "Blue Dart"]
        },
        "General Business": {
            "keywords": [],
            "certifications": ["ISO 9001", "ISO 14001", "SEDEX", "SA 8000", "GMP"],
            "customers": ["Customer A", "Customer B", "Customer C", "Customer D", "Customer E", "Customer F"]
        }
    }

    @staticmethod
    def detect_sector(text: str) -> str:
        if not text:
            return "General Business"
        t = text.lower()
        scores = {}
        for sector, config in IntelligenceService.SECTORS.items():
            if not config["keywords"]:
                continue
            score = sum(1 for k in config["keywords"] if k in t)
            if score > 0:
                scores[sector] = score
        return max(scores, key=scores.get) if scores else "General Business"

    @staticmethod
    def generate_narrative(sector: str, financial_data: Dict, kpis: Dict = None, scraped_text: str = None) -> Dict:
        """Generate comprehensive narrative for all slide elements"""
        kpis = kpis or {}
        scraped_text = scraped_text or ""
        
        # Strategy: Use the unified prompt for both providers
        # 1. Try Gemini
        narrative = IntelligenceService._try_gemini(sector, financial_data, kpis, scraped_text)
        if narrative:
            return narrative
            
        # 2. Try OpenAI
        narrative = IntelligenceService._try_openai(sector, financial_data, kpis, scraped_text)
        if narrative:
            return narrative
        
        # 3. Intelligent Fallback Template
        return IntelligenceService._get_sector_template(sector, financial_data, kpis, scraped_text)

    @staticmethod
    def _get_prompt(sector: str, financial_data: Dict, kpis: Dict, scraped_text: str) -> str:
        return f"""You are an M&A analyst preparing an investment teaser for a {sector} company.

CRITICAL: Use "The Company" instead of any real name in the descriptions.
OBJECTIVE: Generate a comprehensive, data-driven narrative based ONLY on the provided context.

DATA:
- Real Financials Provided: {json.dumps(financial_data) if financial_data else "None"}
- Extracted KPIs: {json.dumps(kpis) if kpis else "None"}
- Scraped Context (News, Web, LinkedIn): {scraped_text[:6000]}

INSTRUCTIONS:
1. STRICT DATA ENFORCEMENT: If specific customer names, locations, or numbers are NOT explicitly mentioned in the context, return "NA" or "Undisclosed". DO NOT ESTIMATE OR FABRICATE DATA.
2. FINANCIALS: Use provided financials if available. If NO financials are provided, return "NA" for all financial values. DO NOT ESTIMATE REVENUE.
3. OUTPUT FORMAT: Return ONLY valid JSON with this EXACT structure:

{{
    "slide_1": {{
        "biz_desc": "2-3 sentences describing business model based strictly on context.",
        "customers": ["Customer 1", "Customer 2"] (Return ["NA"] if none found),
        "assets": [
            {{"label": "Manufacturing\\nUnits", "value": "NA"}},
            {{"label": "R&D\\nCenters", "value": "NA"}},
            {{"label": "Employees", "value": "NA"}},
            {{"label": "Years in\\nBusiness", "value": "NA"}}
        ],
        "certifications": ["Cert 1", "Cert 2"] (Return ["NA"] if none found),
        "product_portfolio": [
            {{"category": "Category", "details": "Description"}},
            {{"category": "Category", "details": "Description"}}
        ],
        "applications": [
            {{"industry": "Industry 1", "share": "NA"}},
            {{"industry": "Industry 2", "share": "NA"}}
        ],
        "revenue_split": {{"Domestic": 0, "Export": 0}} (Use 0 if unknown)
    }},
    "slide_3": {{
        "global_reach": "Description of geographic footprint (or 'NA' if unknown).",
        "export_markets": ["Market 1"] (Return ["NA"] if none found),
        "upcoming_facilities": ["Facility 1"] (Return ["NA"] if none found),
        "assumptions": ["Data extracted from uploaded documents."],
        "investment_highlights": [
            {{"title": "Highlight 1", "desc": "Description based on context"}},
            {{"title": "Highlight 2", "desc": "Description based on context"}}
        ],
        "why_invest": "Summary paragraph based on context."
    }},
    "financials": {{
        "years": ["FY21", "FY22", "FY23", "FY24"],
        "revenue": ["NA", "NA", "NA", "NA"],
        "ebitda": ["NA", "NA", "NA", "NA"],
        "pat": ["NA", "NA", "NA", "NA"]
    }}
}}"""

    @staticmethod
    def _try_gemini(sector: str, financial_data: Dict, kpis: Dict, scraped_text: str) -> Optional[Dict]:
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key or not genai:
            return None
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = IntelligenceService._get_prompt(sector, financial_data, kpis, scraped_text)
            response = model.generate_content(prompt)
            txt = (response.text or "").strip()
            txt = re.sub(r'^```(?:json)?\s*', '', txt, flags=re.MULTILINE)
            txt = re.sub(r'\s*```$', '', txt, flags=re.MULTILINE)
            data = json.loads(txt)
            if isinstance(data, dict) and "slide_1" in data:
                return data
        except Exception as e:
            print(f"[IntelligenceService] Gemini error: {e}")
        return None

    @staticmethod
    def _try_openai(sector: str, financial_data: Dict, kpis: Dict, scraped_text: str) -> Optional[Dict]:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or not OpenAI:
            return None
        try:
            client = OpenAI(api_key=api_key)
            prompt = IntelligenceService._get_prompt(sector, financial_data, kpis, scraped_text)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert M&A analyst. Return ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)
            if isinstance(data, dict) and "slide_1" in data:
                return data
        except Exception as e:
            print(f"[IntelligenceService] OpenAI error: {e}")
        return None

    @staticmethod
    def _get_sector_template(sector: str, financial_data: Dict, kpis: Dict, scraped_text: str = "") -> Dict:
        """Smarter sector fallback when AI fails"""
        config = IntelligenceService.SECTORS.get(sector, IntelligenceService.SECTORS["General Business"])
        context_lower = scraped_text.lower() if scraped_text else ""
        
        # Use provided stats or NA
        revenue = financial_data.get("revenue", ["NA", "NA", "NA", "NA"])
        ebitda = financial_data.get("ebitda", ["NA", "NA", "NA", "NA"])
        
        # Dynamic Description
        desc = (scraped_text[:250] + "...") if len(scraped_text) > 100 else f"The Company is a player in {sector}."

        return {
            "slide_1": {
                "biz_desc": desc,
                "customers": ["NA"],
                "assets": [
                    {"label": "Manufacturing\nUnits", "value": "NA"},
                    {"label": "R&D\nCenters", "value": "NA"},
                    {"label": "Employees", "value": "NA"},
                    {"label": "Years in\nBusiness", "value": "NA"}
                ],
                "certifications": ["NA"],
                "product_portfolio": [
                    {"category": "Core Products", "details": "Information not available"},
                    {"category": "Other Services", "details": "Information not available"}
                ],
                "applications": [
                    {"industry": "NA", "share": "NA"},
                    {"industry": "NA", "share": "NA"}
                ],
                "revenue_split": {"Domestic": 0, "Export": 0}
            },
            "slide_3": {
                "global_reach": "Information not available.",
                "export_markets": ["NA"],
                "upcoming_facilities": ["NA"],
                "assumptions": ["Data extracted from uploaded documents."],
                "investment_highlights": [
                    {"title": "Potential Opportunity", "desc": f"Company operates in {sector} sector."},
                    {"title": "Data Unavailable", "desc": "Insufficient data to generate highlights."},
                    {"title": "Data Unavailable", "desc": "Insufficient data to generate highlights."},
                    {"title": "Data Unavailable", "desc": "Insufficient data to generate highlights."},
                    {"title": "Data Unavailable", "desc": "Insufficient data to generate highlights."},
                    {"title": "Data Unavailable", "desc": "Insufficient data to generate highlights."}
                ],
                "why_invest": "Investment summary not available due to lack of data."
            },
            "financials": {
                "years": ["FY21", "FY22", "FY23", "FY24"],
                "revenue": revenue,
                "ebitda": ebitda,
                "pat": ["NA", "NA", "NA", "NA"]
            }
        }

    @staticmethod
    def _calc_cagr(series: List) -> int:
        try:
            if not series or len(series) < 2: return 15
            start, end = float(series[0]), float(series[-1])
            if start <= 0 or end <= 0: return 15
            n = len(series) - 1
            return int(round(((end / start) ** (1 / n) - 1) * 100))
        except: return 15

    @staticmethod
    def generate_codename() -> str:
        import random
        codenames = ["Apex", "Stellar", "Horizon", "Summit", "Pinnacle", "Titan", "Orion", "Nova", "Zenith"]
        return f"Project {random.choice(codenames)}"
