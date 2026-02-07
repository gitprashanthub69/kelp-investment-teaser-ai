"""
Image Service - Free image sourcing for presentations
Uses Pexels (free, no key required for basic) and Unsplash fallbacks
"""

import os
import re
import requests
from typing import Optional, List, Dict
from bs4 import BeautifulSoup
import urllib.parse


class ImageService:
    """Service for sourcing high-quality images for presentations"""
    
    # Sector-specific image search terms
    SECTOR_IMAGES = {
        "Pharma / Healthcare": ["pharmaceutical laboratory", "medical research", "healthcare technology"],
        "Technology / SaaS": ["technology office", "software development", "cloud computing"],
        "B2B Manufacturing": ["industrial manufacturing", "factory production", "precision engineering"],
        "Chemicals / Specialty": ["chemical laboratory", "industrial chemicals", "research lab"],
        "Logistics / Supply Chain": ["warehouse logistics", "supply chain", "distribution center"],
        "Consumer / D2C": ["modern retail", "ecommerce shopping", "consumer products"],
        "Fintech": ["financial technology", "digital banking", "mobile payments"],
        "Edtech": ["digital education", "online learning", "classroom technology"],
        "Aerospace / Defense": ["aerospace engineering", "aviation technology", "defense systems"],
        "Clean Energy / EV": ["solar panels", "electric vehicle", "renewable energy"],
        "Real Estate / Infrastructure": ["modern architecture", "urban development", "commercial building"],
        "General Business": ["professional business", "corporate office", "business meeting"]
    }

    @staticmethod
    def get_sector_image(sector: str, variation: int = 0) -> Optional[str]:
        """Get a relevant image URL for the sector"""
        search_terms = ImageService.SECTOR_IMAGES.get(
            sector, 
            ImageService.SECTOR_IMAGES["General Business"]
        )
        
        # Cycle through variations
        term = search_terms[variation % len(search_terms)]
        
        # Try multiple sources
        url = ImageService._get_pexels_image(term)
        if url:
            return url
        
        url = ImageService._get_unsplash_direct(term)
        if url:
            return url
        
        url = ImageService._get_picsum_image()
        if url:
            return url
        
        return None

    @staticmethod
    def _get_pexels_image(query: str) -> Optional[str]:
        """Get image from Pexels (free API with generous limits)"""
        api_key = os.getenv("PEXELS_API_KEY")
        if not api_key:
            return None
        
        try:
            headers = {"Authorization": api_key}
            params = {"query": query, "per_page": 1, "orientation": "landscape"}
            response = requests.get(
                "https://api.pexels.com/v1/search",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                photos = data.get("photos", [])
                if photos:
                    return photos[0]["src"]["large"]
        except Exception as e:
            print(f"[ImageService] Pexels error: {e}")
        
        return None

    @staticmethod
    def _get_unsplash_direct(query: str) -> Optional[str]:
        """Get image directly from Unsplash (no API key needed)"""
        try:
            # Use Unsplash source URL (redirects to random matching image)
            encoded_query = urllib.parse.quote(query)
            source_url = f"https://source.unsplash.com/1280x720/?{encoded_query}"
            
            response = requests.get(source_url, timeout=10, allow_redirects=True)
            if response.status_code == 200:
                return response.url  # Returns the redirected image URL
        except Exception as e:
            print(f"[ImageService] Unsplash direct error: {e}")
        
        return None

    @staticmethod
    def _get_picsum_image() -> Optional[str]:
        """Get a random professional image from Lorem Picsum (always works)"""
        try:
            return "https://picsum.photos/1280/720"
        except:
            return None

    @staticmethod
    def download_image(url: str, save_path: str) -> bool:
        """Download image to local path"""
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                return True
        except Exception as e:
            print(f"[ImageService] Download error: {e}")
        return False

    @staticmethod
    def get_placeholder_color(sector: str) -> tuple:
        """Get sector-appropriate placeholder color (R, G, B)"""
        colors = {
            "Pharma / Healthcare": (0, 102, 153),      # Teal
            "Technology / SaaS": (0, 123, 255),        # Blue
            "B2B Manufacturing": (51, 51, 51),         # Dark Gray
            "Chemicals / Specialty": (102, 51, 153),   # Purple
            "Logistics / Supply Chain": (255, 152, 0), # Orange
            "Consumer / D2C": (233, 30, 99),           # Pink
            "Fintech": (0, 150, 136),                  # Teal-Green
            "Edtech": (156, 39, 176),                  # Purple
            "Aerospace / Defense": (33, 33, 33),       # Near Black
            "Clean Energy / EV": (76, 175, 80),        # Green
            "Real Estate / Infrastructure": (121, 85, 72),  # Brown
            "General Business": (0, 51, 102),          # Navy
        }
        return colors.get(sector, (0, 51, 102))
