"""
OpenAI Service for Investment Teaser Generation

Features:
1. LLM-powered insights from uploaded data
2. Public company information research  
3. Image generation for PPT visuals
"""

import os
import json
import re
import requests
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from googlesearch import search as google_search
except ImportError:
    google_search = None


@dataclass
class CompanyInsights:
    """Structured company insights from LLM analysis"""
    business_overview: str
    key_strengths: List[str]
    investment_highlights: List[Dict[str, str]]
    financial_summary: str
    market_position: str
    growth_drivers: List[str]
    risk_factors: List[str]


class OpenAIService:
    """Service for OpenAI-powered intelligence and image generation"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        if self.api_key and OpenAI:
            self.client = OpenAI(api_key=self.api_key)
    
    def is_available(self) -> bool:
        """Check if OpenAI is configured and available"""
        return self.client is not None
    
    # ========== DATA ANALYSIS & INSIGHTS ==========
    
    def analyze_company_data(
        self, 
        company_name: str,
        sector: str,
        financial_data: Dict[str, Any],
        text_content: str,
        website_info: Dict[str, Any] = None
    ) -> Optional[CompanyInsights]:
        """
        Analyze all available company data and generate comprehensive insights.
        """
        if not self.is_available():
            return None
        
        try:
            # Build context from all available data
            context = self._build_analysis_context(
                company_name, sector, financial_data, text_content, website_info
            )
            
            prompt = f"""You are an M&A analyst creating a blind investment teaser for institutional investors.

CONTEXT:
{context}

Generate a comprehensive analysis for an investment presentation. Return STRICT JSON with these keys:

{{
    "business_overview": "2-3 paragraph professional business description for Slide 1. Do NOT mention the company name, use 'The Company'. Focus on business model, products/services, market position.",
    
    "key_strengths": ["List of 4-5 core competitive advantages"],
    
    "investment_highlights": [
        {{"title": "Highlight 1 Title", "description": "1-2 sentence explanation with data if available"}},
        {{"title": "Highlight 2 Title", "description": "explanation"}},
        {{"title": "Highlight 3 Title", "description": "explanation"}},
        {{"title": "Highlight 4 Title", "description": "explanation"}},
        {{"title": "Highlight 5 Title", "description": "explanation"}}
    ],
    
    "financial_summary": "2-3 sentences summarizing financial performance, growth trajectory, and profitability. Include specific metrics if available.",
    
    "market_position": "1-2 sentences on competitive positioning and market share.",
    
    "growth_drivers": ["List of 3-4 key growth catalysts"],
    
    "risk_factors": ["List of 2-3 key risks to monitor"]
}}

IMPORTANT:
- Do NOT mention the actual company name anywhere
- Use "The Company" as the reference
- Be specific with numbers and data when available
- Write in professional investment banking style
- Keep descriptions concise but impactful
"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert M&A analyst specializing in creating institutional-grade investment teasers."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            result_text = re.sub(r'^```(?:json)?\s*', '', result_text)
            result_text = re.sub(r'\s*```$', '', result_text)
            data = json.loads(result_text)
            
            return CompanyInsights(
                business_overview=data.get("business_overview", ""),
                key_strengths=data.get("key_strengths", []),
                investment_highlights=data.get("investment_highlights", []),
                financial_summary=data.get("financial_summary", ""),
                market_position=data.get("market_position", ""),
                growth_drivers=data.get("growth_drivers", []),
                risk_factors=data.get("risk_factors", [])
            )
            
        except Exception as e:
            print(f"OpenAI Analysis Error: {e}")
            return None
    
    def _build_analysis_context(
        self,
        company_name: str,
        sector: str,
        financial_data: Dict[str, Any],
        text_content: str,
        website_info: Dict[str, Any]
    ) -> str:
        """Build context string for LLM analysis"""
        parts = []
        
        parts.append(f"SECTOR: {sector}")
        
        # Financial data
        if financial_data:
            years = financial_data.get("years", [])
            revenue = financial_data.get("revenue", [])
            ebitda = financial_data.get("ebitda", [])
            pat = financial_data.get("pat", [])
            kpis = financial_data.get("kpis", {})
            
            if years and revenue:
                parts.append(f"REVENUE TREND: {list(zip(years, revenue))}")
            if years and ebitda:
                parts.append(f"EBITDA TREND: {list(zip(years, ebitda))}")
            if years and pat:
                parts.append(f"PAT TREND: {list(zip(years, pat))}")
            if kpis:
                parts.append(f"KEY METRICS: {json.dumps(kpis)}")
        
        # Website info
        if website_info:
            if website_info.get("title"):
                parts.append(f"WEBSITE TITLE: {website_info['title']}")
            if website_info.get("description"):
                parts.append(f"META DESCRIPTION: {website_info['description']}")
            if website_info.get("content_snippet"):
                parts.append(f"WEBSITE CONTENT: {website_info['content_snippet'][:1500]}")
        
        # Document content
        if text_content:
            parts.append(f"DOCUMENT CONTENT:\n{text_content[:3000]}")
        
        return "\n\n".join(parts)
    
    # ========== PUBLIC DATA RESEARCH ==========
    
    def research_company_public(self, company_name: str, website: str = None) -> Dict[str, Any]:
        """
        Research company using public sources and synthesize findings.
        """
        if not self.is_available():
            return {}
        
        try:
            # Gather public information
            search_results = self._web_search(company_name)
            
            # Synthesize with LLM
            prompt = f"""Research the following company and provide public information for an investment teaser.

COMPANY: {company_name}
WEBSITE: {website or 'Not provided'}

WEB SEARCH RESULTS:
{json.dumps(search_results[:5], indent=2) if search_results else 'No results available'}

Return STRICT JSON with:
{{
    "company_description": "2-3 sentence public description of the company",
    "industry": "Primary industry/sector",
    "key_products": ["List of main products/services"],
    "key_customers": ["List of known major customers if available"],
    "geographic_presence": "Markets/regions where company operates",
    "recent_news": ["1-2 recent news items or developments if available"],
    "competitive_landscape": "Brief note on competitors and positioning"
}}

If information is not available for any field, use reasonable inferences based on the sector or leave as empty string/list.
"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a business research analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1000
            )
            
            result_text = response.choices[0].message.content.strip()
            result_text = re.sub(r'^```(?:json)?\s*', '', result_text)
            result_text = re.sub(r'\s*```$', '', result_text)
            
            return json.loads(result_text)
            
        except Exception as e:
            print(f"OpenAI Research Error: {e}")
            return {}
    
    def _web_search(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """Perform web search for company information"""
        results = []
        
        if google_search:
            try:
                for url in google_search(query, num_results=num_results, lang="en"):
                    results.append({"url": url, "query": query})
            except Exception as e:
                print(f"Web search error: {e}")
        
        return results
    

    # ========== UNSPLASH IMAGE GENERATION ==========
    
    def search_unsplash(self, query: str, orientation: str = "landscape") -> Optional[str]:
        """
        Search Unsplash for a high-quality, professional image.
        Fallback: If API Key fails, use direct public search scraping.
        """
        access_key = os.getenv("UNSPLASH_ACCESS_KEY")
        
        # 1. Try Official API first
        if access_key:
            try:
                url = "https://api.unsplash.com/search/photos"
                params = {
                    "query": query,
                    "orientation": orientation,
                    "per_page": 1,
                    "client_id": access_key,
                    "content_filter": "high"
                }
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    if results:
                        return results[0]["urls"]["regular"]
                print(f"Unsplash API fallback triggered (Status {response.status_code})")
            except Exception as e:
                print(f"Unsplash API Error: {e}")

        # 2. Fallback: Direct Public Source Sourcing (User's 'Direct Access' request)
        # We use Unsplash's source redirect or a simple scrape of the public search
        try:
            # Unsplash Source (Legacy but often functional for single images)
            source_url = f"https://source.unsplash.com/featured/?{query.replace(' ', ',')}"
            r = requests.get(source_url, timeout=10, allow_redirects=True)
            if r.status_code == 200 and "unsplash.com/photos/" in r.url:
                # Extract photo ID from URL if redirected to a photo page
                photo_id = r.url.split("/")[-1]
                # Construct a direct download link (unregistered version)
                return f"https://images.unsplash.com/photo-{photo_id}?auto=format&fit=crop&q=80&w=1080"
            
            # 3. Final Fallback: Scrape Unsplash Search Result
            search_url = f"https://unsplash.com/s/photos/{query.replace(' ', '-')}"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            r = requests.get(search_url, headers=headers, timeout=10)
            if r.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(r.text, 'html.parser')
                # Find the first high-res image link (usually in a specific class or data-attribute)
                img = soup.find('img', {'srcset': True})
                if img and img['src']:
                    return img['src'].split('?')[0] + "?auto=format&fit=crop&q=80&w=1080"

        except Exception as e:
            print(f"Unsplash Direct Access Error: {e}")
            
        return None

    # ========== BRAND / LOGO SEARCH (NEW) ==========
    
    def find_company_logo(self, company_name: str) -> Optional[str]:
        """
        Attempt to find a company logo URL using a clearbit fallback or search logic.
        """
        # 1. Clearbit Fallback (Simplest for prominent brands)
        domain_guess = company_name.lower().replace(" ", "") + ".com"
        logo_url = f"https://logo.clearbit.com/{domain_guess}"
        try:
            r = requests.get(logo_url, timeout=5, stream=True)
            if r.status_code == 200:
                return logo_url
        except: pass
        
        # 2. Generic Industry Icon fallback if logo not found
        return None

    def validate_image_safety(self, image_url: str) -> bool:
        """
        Placeholder for image safety check. 
        Unsplash 'content_filter=high' provides baseline safety.
        """
        return True

    def download_image(self, url: str, path: str) -> bool:
        """
        Download an image from a URL and save it to the specified path.
        """
        try:
            response = requests.get(url, stream=True, timeout=20)
            if response.status_code == 200:
                with open(path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return True
            print(f"Failed to download image: {response.status_code}")
            return False
        except Exception as e:
            print(f"Error downloading image: {e}")
            return False

    def generate_image_queries(self, sector: str, slide_type: str, company_name: str = None) -> str:
        """
        Generate a safe, generic search query for Unsplash.
        Ensures no company names are leaked in the search query.
        """
        prompts = {
            "Manufacturing / Specialty Chemicals": {
                "overview": "clean industrial chemical plant interior",
                "operations": "automated manufacturing assembly line",
                "growth": "shipping containers logistics port dusk"
            },
            "Pharma / Healthcare": {
                "overview": "modern pharmaceutical laboratory research",
                "operations": "scientific microscope analysis biology",
                "growth": "medical technology abstract blue"
            },
            "D2C Consumer": {
                "overview": "modern ecommerce warehouse fulfillment",
                "operations": "branded delivery boxes logistics",
                "growth": "lifestyle retail shopping abstract"
            },
            "Tech / B2B SaaS": {
                "overview": "high tech data center server room",
                "operations": "software code programming screen",
                "growth": "global digital networking connectivity"
            },
            "Logistics": {
                "overview": "large logistics warehouse distribution",
                "operations": "delivery trucks fleet logistics",
                "growth": "global supply chain map abstract"
            }
        }
        
        sector_prompts = prompts.get(sector, {
            "overview": "modern business office building glass",
            "operations": "professional business meeting room",
            "growth": "city skyline conceptual growth"
        })
        
        query = sector_prompts.get(slide_type, "professional business abstract")
        
        # Security: Remove company name if it accidentally appears in the query
        if company_name:
            query = re.sub(re.escape(company_name), "", query, flags=re.IGNORECASE).strip()
            
        return query

    # ========== DENSE NARRATIVE GENERATION ==========
    
    def generate_dense_narrative(
        self,
        slide_type: str,
        sector: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any] | None:
        """
        Generate high-density, insight-rich content for Reference Style slides.
        """
        if not self.is_available():
            return None
            
        prompts = {
            "slide_1": f"""Analyze data for Slide 1 (Executive Summary).
Sector: {sector}
Data: {json.dumps(data)[:2500]}

REQUIREMENTS:
1. Extract specific numbers where possible (Employees, Facilities, Capacity).
2. Use "The Company" (Blind).

Return JSON:
{{
    "biz_desc": "2 dense paragraphs describing business model and market position.",
    "at_a_glance": [
        {{"label": "Revenue", "value": "e.g. $150M+"}},
        {{"label": "EBITDA Margin", "value": "e.g. ~18%"}},
        {{"label": "Employees", "value": "e.g. 500+"}},
        {{"label": "Facilities", "value": "e.g. 3 Mfg Units"}},
        {{"label": "CAGR", "value": "e.g. 15%"}},
        {{"label": "Key Markets", "value": "e.g. US, EU"}}
    ],
    "revenue_split": {{"Domestic": 60, "Export": 40}}, 
    "key_highlights": ["Highlight 1", "Highlight 2", "Highlight 3"]
}}""",

            "slide_2": f"""Analyze data for Slide 2 (Operational Scale).
Sector: {sector}
Data: {json.dumps(data)[:2500]}

Return JSON:
{{
    "product_portfolio": [
        {{"category": "Cat 1", "details": "Detail A, Detail B"}},
        {{"category": "Cat 2", "details": "Detail C, Detail D"}}
    ],
    "applications": [
        {{"industry": "Ind 1", "share": "e.g. 40%"}},
        {{"industry": "Ind 2", "share": "e.g. 25%"}}
    ],
    "global_reach": "Description of export markets and presence."
}}""",

            "slide_3": f"""Analyze data for Slide 3 (Growth & Financials).
Sector: {sector}
Data: {json.dumps(data)[:2500]}

Return JSON:
{{
    "financial_commentary": "One sentence on financial trajectory.",
    "growth_strategies": [
        {{"title": "Strategy 1", "desc": "Detail..."}},
        {{"title": "Strategy 2", "desc": "Detail..."}},
        {{"title": "Strategy 3", "desc": "Detail..."}}
    ]
}}"""
        }
        
        prompt = prompts.get(slide_type)
        if not prompt: return None
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a senior investment banker. You value density, precision, and specific numbers."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            content = response.choices[0].message.content.strip()
            content = re.sub(r'^```(?:json)?\s*', '', content)
            content = re.sub(r'\s*```$', '', content)
            parsed = json.loads(content)
            
            # Additional Safety: Ensure keys exist
            if slide_type == "slide_1" and "at_a_glance" not in parsed:
                parsed["at_a_glance"] = [
                    {"label": "Revenue", "value": "N/A"},
                    {"label": "Employees", "value": "N/A"}
                ]
            
            return parsed
            
        except Exception as e:
            print(f"OpenAI Narrative Error ({slide_type}): {e}")
            # Return Safe Defaults instead of None
            defaults = {
                "slide_1": {
                    "biz_desc": "Business description unavailable.",
                    "key_highlights": ["Highlight unavailable"],
                    "at_a_glance": [],
                    "revenue_split": {}
                },
                "slide_2": {
                    "product_portfolio": [],
                    "applications": [],
                    "global_reach": "Global Reach Unavailable"
                },
                "slide_3": {
                    "financial_commentary": "Financial data unavailable.",
                    "growth_strategies": []
                }
            }
            return defaults.get(slide_type, {})


# Singleton instance
_openai_service = None

def get_openai_service() -> OpenAIService:
    """Get singleton OpenAI service instance"""
    global _openai_service
    if _openai_service is None:
        _openai_service = OpenAIService()
    return _openai_service
