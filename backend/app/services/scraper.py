import os
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional, Tuple

try:
    from googlesearch import search as google_search
except Exception:
    google_search = None

class ScraperService:
    @staticmethod
    def _get_serpapi_key():
        return os.getenv("SERPAPI_KEY")

    @staticmethod
    def find_official_site(company_name: str) -> Optional[str]:
        """
        Best-effort: find likely official website using search results.
        """
        if not company_name or not google_search:
            return None
        try:
            q = f"{company_name} official website"
            results = list(google_search(q, num_results=5, lang="en"))
            for url in results:
                if url.startswith("https://") and not any(bad in url for bad in ["linkedin.com", "facebook.com", "instagram.com", "twitter.com", "x.com", "wikipedia.org"]):
                    return url
            return results[0] if results else None
        except Exception:
            return None

    @staticmethod
    def scrape_news_serpapi(company_name: str) -> List[Dict[str, Any]]:
        """
        Fetch news using SerpAPI Google News.
        """
        api_key = ScraperService._get_serpapi_key()
        if not api_key:
            return []
            
        try:
            params = {
                "q": company_name,
                "tbm": "nws",
                "api_key": api_key,
                "num": 3
            }
            response = requests.get("https://serpapi.com/search", params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                news_results = data.get("news_results", [])
                return [{"title": n.get("title"), "link": n.get("link"), "snippet": n.get("snippet")} for n in news_results]
        except Exception as e:
            print(f"SerpAPI Error: {e}")
        return []

    @staticmethod
    def scrape_linkedin_public(company_name: str) -> Dict[str, Any]:
        """
        Improved best-effort LinkedIn discovery using Google Search.
        """
        if not google_search:
            return {"platform": "LinkedIn", "error": "Google search not available"}
            
        try:
            q = f"{company_name} linkedin company page"
            results = list(google_search(q, num_results=3, lang="en"))
            target_url = None
            for url in results:
                if "linkedin.com/company/" in url:
                    target_url = url
                    break
            
            if target_url:
                # In a real production environment, we would use a dedicated scrapers like Proxycurl
                # For now, we return the URL and metadata for IntelligenceService to reference
                return {
                    "platform": "LinkedIn",
                    "url": target_url,
                    "note": f"Discovered company profile for context."
                }
            return {"platform": "LinkedIn", "note": "No public company profile found."}
        except Exception as e:
            return {"platform": "LinkedIn", "error": str(e)}

    @staticmethod
    def gather_public_context(company_name: str, website: Optional[str] = None, max_urls: int = 5) -> Dict[str, Any]:
        """
        Collects comprehensive public context.
        """
        urls: List[str] = []
        if website:
            urls.append(website if website.startswith("http") else "https://" + website)
        else:
            found = ScraperService.find_official_site(company_name)
            if found:
                urls.append(found)

        # 1. Basic Web Search
        if google_search:
            try:
                q = f"{company_name} products business model"
                for u in google_search(q, num_results=max_urls, lang="en"):
                    if u not in urls and u.startswith("http"):
                        urls.append(u)
                    if len(urls) >= max_urls:
                        break
            except Exception:
                pass

        # 2. News from SerpAPI
        news = ScraperService.scrape_news_serpapi(company_name)
        
        # 3. LinkedIn Context
        linkedin = ScraperService.scrape_linkedin_public(company_name)

        scraped_pages: List[Dict[str, Any]] = []
        combined_text = ""
        for u in urls[:max_urls]:
            info = ScraperService.scrape_website(u)
            if info and not info.get("error"):
                scraped_pages.append({"url": u, **info})
                combined_text += f"\nURL: {u}\nTITLE: {info.get('title','')}\nTEXT: {info.get('content_snippet','')}\n"

        # Add news to combined text
        for n in news:
            combined_text += f"\nNEWS: {n['title']} - {n['snippet']} (Source: {n['link']})\n"

        # Add LinkedIn context
        if linkedin.get("url"):
            combined_text += f"\nLINKEDIN: {linkedin['url']} - {linkedin.get('note','')}\n"

        return {
            "urls": urls[:max_urls],
            "pages": scraped_pages,
            "news": news,
            "linkedin": linkedin,
            "combined_text": combined_text.strip()
        }

    @staticmethod
    def scrape_website(url: str) -> Dict[str, Any]:
        """
        Fetches public company info from the URL. 
        Uses requests/BS4 by default, with an optional Playwright fallback.
        """
        if not url:
            return {}
        if not url.startswith('http'):
            url = 'https://' + url
            
        try:
            # Try Requests first (faster)
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                title = soup.title.string.strip() if soup.title else ""
                desc = ""
                meta = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
                if meta:
                    desc = meta.get('content', '').strip()
                paragraphs = [p.get_text().strip() for p in soup.find_all('p') if len(p.get_text()) > 50]
                full_text = " ".join(paragraphs[:5])
                return {"title": title, "description": desc, "content_snippet": full_text}
            
            # If requests fails or returns 403, Playwright could be used here in Docker
            return {"error": f"Status {response.status_code}"}
            
        except Exception as e:
            return {"error": str(e)}
