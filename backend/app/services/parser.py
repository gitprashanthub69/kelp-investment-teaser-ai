"""
Data Parser - Enhanced Extraction
Robust extraction of financial data and KPIs from Excel and PDF files
"""

import pandas as pd
import fitz  # PyMuPDF
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

try:
    import camelot
except ImportError:
    camelot = None


@dataclass
class DataSource:
    file_path: str
    page: Optional[int] = None
    sheet: Optional[str] = None
    row: Optional[int] = None
    metric: Optional[str] = None


# Year pattern matching
_YEAR_RE = re.compile(r"(?:FY\s?)?((?:20|19)\d{2})|(?:FY\s?)(\d{2})", re.IGNORECASE)


def _to_number(val: Any) -> float | None:
    """Convert various formats to float"""
    if val is None:
        return None
    s = str(val).strip()
    if not s or s.lower() in {"nan", "none", "-", "null", "n/a", "na"}:
        return None
    
    # Remove currency and formatting
    s = re.sub(r"[₹$€£,]", "", s)
    s = re.sub(r"\s*(cr|crore|lakhs?|lacs?|mn|m|k|billion|bn)\s*$", "", s, flags=re.IGNORECASE)
    
    # Handle parentheses negatives
    neg = False
    if s.startswith("(") and s.endswith(")"):
        neg = True
        s = s[1:-1]
    
    # Remove percentage/multiplier suffixes
    s = re.sub(r"[%x]$", "", s).strip()
    
    try:
        num = float(s)
        return -num if neg else num
    except Exception:
        return None


def _looks_like_year(x: Any) -> bool:
    if x is None:
        return False
    s = str(x).strip()
    return bool(_YEAR_RE.search(s)) if s else False


def _extract_year_label(x: Any) -> str | None:
    if x is None:
        return None
    s = str(x).strip()
    m = _YEAR_RE.search(s)
    if not m:
        return None
    
    full_year = m.group(1)
    short_year = m.group(2)
    
    if full_year:
        year = int(full_year)
    elif short_year:
        year = 2000 + int(short_year)
    else:
        return None
    
    suffix = "E" if re.search(r"(?:E|e|est)\b", s) else ""
    return f"FY{str(year)[-2:]}{suffix}"


def _dedupe_keep_order(items: List[str]) -> List[str]:
    seen = set()
    out = []
    for it in items:
        if it and it not in seen:
            seen.add(it)
            out.append(it)
    return out


class DataParser:
    """Enhanced data extraction from Excel and PDF files"""
    
    # Metric keywords for recognition
    REVENUE_KEYWORDS = [
        "revenue", "sales", "turnover", "total income", "gross receipts", 
        "total revenue", "net sales", "operating revenue", "top line",
        "arr", "mrr", "tpv", "gmv", "premium income", "gross revenue"
    ]
    
    EBITDA_KEYWORDS = [
        "ebitda", "operating profit", "pbit", "operating income", "ebit",
        "operating surplus", "earnings before", "operating margin"
    ]
    
    PAT_KEYWORDS = [
        "pat", "net profit", "profit after tax", "earning after tax", 
        "net income", "profit / (loss)", "surplus after tax", "net earnings",
        "bottom line", "profit for the year"
    ]

    @staticmethod
    def parse_excel(file_path: str) -> Dict[str, Any]:
        """
        Parse financial data from Excel with horizontal and vertical layouts.
        """
        financials = {
            "years": [],
            "revenue": [],
            "ebitda": [],
            "pat": [],
            "units": None,
            "source_metadata": {}
        }
        
        try:
            xls = pd.ExcelFile(file_path)
            
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
                if df.empty:
                    continue
                
                # Strategy 1: Horizontal Parse (metrics in rows, years in columns)
                result = DataParser._parse_horizontal(df, file_path, sheet_name)
                if result:
                    return result
                
                # Strategy 2: Vertical Parse (years in rows, metrics in columns)
                result = DataParser._parse_vertical(df, file_path)
                if result:
                    return result
            
            return {"financials": financials, "source_file": file_path}
            
        except Exception as e:
            print(f"[DataParser] Excel Error: {e}")
            return {"error": str(e), "source_file": file_path}

    @staticmethod
    def _parse_horizontal(df: pd.DataFrame, file_path: str, sheet_name: str) -> Dict | None:
        """Parse horizontal layout (years across columns)"""
        financials = {
            "years": [],
            "revenue": [],
            "ebitda": [],
            "pat": [],
            "source_metadata": {}
        }
        
        # Find year columns in top rows
        year_positions = []  # (col_idx, year_label)
        for r in range(min(10, len(df))):
            for c in range(len(df.columns)):
                y = _extract_year_label(df.iat[r, c])
                if y and not any(y == yp[1] for yp in year_positions):
                    year_positions.append((c, y))
        
        if len(year_positions) < 2:
            return None
        
        # Sort by column position
        year_positions.sort(key=lambda x: x[0])
        year_cols = [yp[0] for yp in year_positions]
        year_labels = [yp[1] for yp in year_positions]
        
        financials["years"] = year_labels
        
        # Scan for metrics
        for r in range(len(df)):
            row_text = " ".join(str(df.iat[r, c]).lower() for c in range(min(3, len(df.columns))))
            
            metric = None
            if any(k in row_text for k in DataParser.REVENUE_KEYWORDS):
                metric = "revenue"
            elif any(k in row_text for k in DataParser.EBITDA_KEYWORDS):
                metric = "ebitda"
            elif any(k in row_text for k in DataParser.PAT_KEYWORDS):
                metric = "pat"
            
            if metric and metric not in financials["source_metadata"]:
                values = []
                for col in year_cols:
                    val = _to_number(df.iat[r, col])
                    values.append(val if val is not None else 0)
                
                if any(v != 0 for v in values):
                    financials[metric] = values
                    financials["source_metadata"][metric] = DataSource(
                        file_path=file_path, sheet=sheet_name, row=r, metric=metric
                    )
        
        if financials["revenue"] or financials["ebitda"]:
            return {"financials": financials, "source_file": file_path}
        
        return None

    @staticmethod
    def _parse_vertical(df: pd.DataFrame, file_path: str) -> Dict | None:
        """Parse vertical layout (years in rows)"""
        financials = {
            "years": [],
            "revenue": [],
            "ebitda": [],
            "pat": [],
            "source_metadata": {}
        }
        
        # Find year column
        year_col_idx = -1
        for c in range(len(df.columns)):
            col_values = df.iloc[:, c].tolist()
            matches = [v for v in col_values if _looks_like_year(v)]
            if len(matches) >= 2:
                year_col_idx = c
                break
        
        if year_col_idx == -1:
            return None
        
        # Extract year rows
        valid_rows = []
        for r in range(len(df)):
            y_label = _extract_year_label(df.iat[r, year_col_idx])
            if y_label:
                valid_rows.append((r, y_label))
        
        if len(valid_rows) < 2:
            return None
        
        valid_rows.sort(key=lambda x: x[0])
        financials["years"] = [x[1] for x in valid_rows]
        row_indices = [x[0] for x in valid_rows]
        
        # Find metric columns from header rows
        column_map = {}
        for r in range(min(5, len(df))):
            for c in range(len(df.columns)):
                if c == year_col_idx:
                    continue
                val = str(df.iat[r, c]).lower()
                
                if any(k in val for k in DataParser.REVENUE_KEYWORDS):
                    column_map["revenue"] = c
                elif any(k in val for k in DataParser.EBITDA_KEYWORDS):
                    column_map["ebitda"] = c
                elif any(k in val for k in DataParser.PAT_KEYWORDS):
                    column_map["pat"] = c
        
        if not column_map:
            return None
        
        # Extract values
        for metric, col_idx in column_map.items():
            values = []
            for r_idx in row_indices:
                val = _to_number(df.iat[r_idx, col_idx])
                values.append(val if val is not None else 0)
            financials[metric] = values
            financials["source_metadata"][metric] = DataSource(
                file_path=file_path, metric=metric
            )
        
        if financials["revenue"] or financials["ebitda"]:
            return {"financials": financials, "source_file": file_path}
        
        return None

    @staticmethod
    def parse_pdf(file_path: str) -> Dict[str, Any]:
        """
        Extract text, tables, and KPIs from PDF files.
        """
        results = {
            "text_content": "",
            "page_count": 0,
            "kpis": {},
            "source_file": file_path,
            "financials": None
        }
        
        try:
            doc = fitz.open(file_path)
            results["page_count"] = len(doc)
            
            # Extract text from all pages
            pages_text = []
            for page in doc:
                pages_text.append(page.get_text() or "")
            full_text = "\n".join(pages_text)
            results["text_content"] = full_text
            
            # Enhanced KPI extraction with regex patterns
            results["kpis"] = DataParser._extract_kpis(full_text)
            
            # Try table extraction with Camelot
            if camelot:
                try:
                    tables = camelot.read_pdf(file_path, pages='all', flavor='lattice')
                    for table in tables:
                        df = table.df
                        vertical = DataParser._parse_vertical(df, file_path)
                        if vertical and vertical.get("financials", {}).get("revenue"):
                            vertical["financials"]["source_type"] = "pdf_table"
                            vertical["financials"]["page"] = table.page
                            results["financials"] = vertical["financials"]
                            break
                except Exception as e:
                    print(f"[DataParser] Camelot error: {e}")
            
            return results
            
        except Exception as e:
            print(f"[DataParser] PDF Error: {e}")
            return {"error": str(e), "source_file": file_path}

    @staticmethod
    def _extract_kpis(text: str) -> Dict[str, Any]:
        """Extract key performance indicators from text"""
        kpis = {}
        
        # Financial metrics
        patterns = {
            "ebitda_margin": r"EBITDA\s*Margin\s*[:\-]?\s*([~]?\d{1,2}\.?\d{0,2}\s*%)",
            "pat_margin": r"(?:PAT|Net\s+Profit)\s*Margin\s*[:\-]?\s*([~]?\d{1,2}\.?\d{0,2}\s*%)",
            "roe": r"\bRo[EA]\b\s*[:\-]?\s*([~]?\d{1,2}\.?\d{0,2}\s*%)",
            "roce": r"\bRoCE\b\s*[:\-]?\s*([~]?\d{1,2}\.?\d{0,2}\s*%)",
            "revenue_cagr": r"Revenue\s*CAGR\s*[:\-]?\s*([~]?\d{1,2}\.?\d{0,2}\s*%)",
            "employees": r"(?:Employees?|Headcount|Team\s+Size)\s*[:\-]?\s*([\d,]+(?:\+)?)",
            "facilities": r"(?:Facilities?|Plants?|Units?)\s*[:\-]?\s*(\d+)",
            "countries": r"(?:Countries|Markets)\s*[:\-]?\s*(\d+\+?)",
            "customers": r"(?:Customers?|Clients?)\s*[:\-]?\s*([\d,]+\+?)",
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                kpis[key] = match.group(1).strip()
        
        # Boolean flags
        kpis["zero_debt"] = bool(re.search(r"\bzero\s+debt\b", text, re.IGNORECASE))
        kpis["profitable"] = bool(re.search(r"\bprofitable\b|\bprofit\s+making\b", text, re.IGNORECASE))
        kpis["iso_certified"] = bool(re.search(r"\bISO\s*\d{4}\b", text, re.IGNORECASE))
        kpis["who_gmp"] = bool(re.search(r"\bWHO[\-\s]?GMP\b", text, re.IGNORECASE))
        kpis["fda_approved"] = bool(re.search(r"\bFDA\s*(?:approved|approval)\b", text, re.IGNORECASE))
        
        return kpis

    @staticmethod
    def merge_financials(excel_data: Dict, pdf_data: Dict) -> Dict:
        """Merge financial data from multiple sources, preferring Excel"""
        result = {
            "years": [],
            "revenue": [],
            "ebitda": [],
            "pat": [],
            "kpis": {}
        }
        
        # Prefer Excel financials
        excel_fin = excel_data.get("financials", {})
        pdf_fin = pdf_data.get("financials", {}) or {}
        
        if excel_fin.get("revenue"):
            result["years"] = excel_fin.get("years", [])
            result["revenue"] = excel_fin.get("revenue", [])
            result["ebitda"] = excel_fin.get("ebitda", [])
            result["pat"] = excel_fin.get("pat", [])
        elif pdf_fin.get("revenue"):
            result["years"] = pdf_fin.get("years", [])
            result["revenue"] = pdf_fin.get("revenue", [])
            result["ebitda"] = pdf_fin.get("ebitda", [])
            result["pat"] = pdf_fin.get("pat", [])
        
        # Merge KPIs from PDF
        result["kpis"] = pdf_data.get("kpis", {})
        
        return result


class DocumentExtractor:
    """
    Extract structured narrative data from PDF text for PPT generation.
    Parses business description, products, applications, certifications, assets, etc.
    """
    
    # Section header patterns
    SECTION_PATTERNS = {
        "business_description": r"(?:Business\s+Description|Company\s+Overview|About\s+(?:the\s+)?Company)\s*\n",
        "products": r"(?:Product\s*[&\s]*Services?|Product\s+Portfolio|Our\s+Products)\s*\n",
        "applications": r"(?:Application\s+areas?\s*/?\s*Industries?\s*served|Key\s+Applications?|End\s+Markets?|Industries?\s+Served)\s*\n",
        "operational": r"(?:Key\s+Operational\s+Indicators?|Operational\s+Highlights?|Key\s+Metrics)\s*\n",
        "website": r"(?:Website|Web)\s*\n",
    }
    
    # Certification patterns
    CERT_PATTERNS = [
        r"\bISO\s*(?:TS\s*)?\d{4,5}(?::\d{4})?\b",
        r"\bWHO[\-\s]?GMP\b",
        r"\bFDA\b(?:\s+approved)?",
        r"\bEU[\-\s]?GMP\b",
        r"\bFSSAI\b",
        r"\bHACCP\b",
        r"\bBRC\b",
        r"\bIATF\s*\d+\b",
        r"\bOHSAS\s*\d+\b",
        r"\bSEDEX\b",
        r"\bSA\s*8000\b",
        r"\bGDP\b",
        r"\bREACH\b",
        r"\bGDPR\b",
        r"\bSOC\s*2\b",
        r"\bPCI[\-\s]?DSS\b",
    ]
    
    @staticmethod
    def extract_narrative(text: str) -> Dict[str, Any]:
        """
        Extract all narrative fields from PDF text content.
        Returns a structure compatible with ppt_generator narrative format.
        """
        if not text:
            return {}
        
        result = {
            "slide_1": {},
            "slide_3": {},
            "_extracted_fields": []  # Track what was successfully extracted
        }
        
        # 1. Extract business description
        biz_desc = DocumentExtractor._extract_business_description(text)
        if biz_desc:
            result["slide_1"]["biz_desc"] = biz_desc
            result["_extracted_fields"].append("biz_desc")
        
        # 2. Extract website
        website = DocumentExtractor._extract_website(text)
        if website:
            result["website"] = website
            result["_extracted_fields"].append("website")
        
        # 3. Extract products/services
        products = DocumentExtractor._extract_products(text)
        if products:
            result["slide_1"]["product_portfolio"] = products
            result["_extracted_fields"].append("product_portfolio")
        
        # 4. Extract applications/industries
        applications = DocumentExtractor._extract_applications(text)
        if applications:
            result["slide_1"]["applications"] = applications
            result["_extracted_fields"].append("applications")
        
        # 5. Extract certifications
        certifications = DocumentExtractor._extract_certifications(text)
        if certifications:
            result["slide_1"]["certifications"] = certifications
            result["_extracted_fields"].append("certifications")
        
        # 6. Extract assets (facilities, employees, etc.)
        assets = DocumentExtractor._extract_assets(text)
        if assets:
            result["slide_1"]["assets"] = assets
            result["_extracted_fields"].append("assets")
        
        # 7. Extract operational indicators / upcoming facilities
        operational = DocumentExtractor._extract_operational_indicators(text)
        if operational.get("upcoming_facilities"):
            result["slide_3"]["upcoming_facilities"] = operational["upcoming_facilities"]
            result["_extracted_fields"].append("upcoming_facilities")
        
        # 8. Extract export markets / global presence
        markets = DocumentExtractor._extract_export_markets(text)
        if markets:
            result["slide_3"]["export_markets"] = markets
            result["_extracted_fields"].append("export_markets")
        
        # 9. Extract customers if mentioned
        customers = DocumentExtractor._extract_customers(text)
        if customers:
            result["slide_1"]["customers"] = customers
            result["_extracted_fields"].append("customers")
        
        # 10. Extract financial metrics for slide 3 charts
        financial_data = DocumentExtractor._extract_financial_data(text)
        if financial_data:
            result["financials"] = financial_data
            result["_extracted_fields"].append("financials")
        
        # 11. Construct global_reach text from export markets
        if markets:
            market_count = len(markets)
            markets_str = ", ".join(markets[:4])
            result["slide_3"]["global_reach"] = f"Exports to {market_count}+ global markets including {markets_str}."
            result["_extracted_fields"].append("global_reach")
        
        print(f"[DocumentExtractor] Extracted fields: {result['_extracted_fields']}")
        return result
    
    @staticmethod
    def _extract_section(text: str, section_name: str, next_sections: List[str] = None) -> str:
        """Extract text between a section header and the next section."""
        pattern = DocumentExtractor.SECTION_PATTERNS.get(section_name)
        if not pattern:
            return ""
        
        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            return ""
        
        start = match.end()
        
        # Find the end - look for next section header
        end = len(text)
        next_patterns = next_sections or list(DocumentExtractor.SECTION_PATTERNS.values())
        for np in next_patterns:
            next_match = re.search(np, text[start:], re.IGNORECASE)
            if next_match:
                end = min(end, start + next_match.start())
        
        return text[start:end].strip()
    
    @staticmethod
    def _extract_business_description(text: str) -> str:
        """Extract business description paragraph."""
        # Try section-based extraction
        section = DocumentExtractor._extract_section(text, "business_description")
        if section:
            # Take first 2-3 sentences or ~350 chars
            sentences = re.split(r'(?<=[.!?])\s+', section)
            desc = " ".join(sentences[:3])
            return desc[:400] if len(desc) > 400 else desc
        
        # Fallback: look for company description in first paragraphs
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if len(line) > 100 and not line.startswith('•') and not line.startswith('*'):
                # Looks like a paragraph
                return line[:400]
        
        return ""
    
    @staticmethod
    def _extract_website(text: str) -> str:
        """Extract website URL."""
        # Look for URL pattern
        url_pattern = r'https?://[^\s\n]+'
        match = re.search(url_pattern, text)
        if match:
            return match.group(0).rstrip('.,;:')
        return ""
    
    @staticmethod
    def _extract_products(text: str) -> List[Dict[str, str]]:
        """Extract product portfolio items."""
        products = []
        
        # Extract products section
        section = DocumentExtractor._extract_section(text, "products")
        if not section:
            return []
        
        # Parse bullet points: • **Category** (details) or * **Category:** details
        bullet_pattern = r'[•*]\s*\*?\*?([^*\n(]+?)(?:\*\*)?(?:\s*\(([^)]+)\)|\s*[:\-]\s*([^\n]+))?'
        matches = re.findall(bullet_pattern, section)
        
        for match in matches[:6]:  # Limit to 6 products
            category = match[0].strip().strip('*').strip()
            details = (match[1] or match[2] or "").strip()
            
            if category and len(category) > 2:
                products.append({
                    "category": category[:50],
                    "details": details[:80] if details else f"Key {category.lower()} segment"
                })
        
        # If no bullet points, try line-by-line
        if not products:
            lines = section.split('\n')
            for line in lines[:6]:
                line = line.strip().strip('•*').strip()
                if line and len(line) > 3 and len(line) < 100:
                    products.append({
                        "category": line[:50],
                        "details": ""
                    })
        
        return products
    
    @staticmethod
    def _extract_applications(text: str) -> List[Dict[str, str]]:
        """Extract application areas / industries served."""
        applications = []
        
        section = DocumentExtractor._extract_section(text, "applications")
        if section:
            # Parse comma-separated or line-separated industries
            # Clean up the section
            clean_section = re.sub(r'[•*]', '', section)
            
            # Try comma-separated first
            if ',' in clean_section:
                items = [x.strip() for x in clean_section.split(',')]
            else:
                items = [x.strip() for x in clean_section.split('\n') if x.strip()]
            
            # Create application entries
            total_items = len([i for i in items if i and len(i) > 2])
            for i, item in enumerate(items[:6]):
                if item and len(item) > 2:
                    # Estimate share based on position (simple heuristic)
                    share = max(10, 60 - (i * 10)) if total_items > 0 else 25
                    applications.append({
                        "industry": item[:40],
                        "share": f"{share}%"
                    })
        
        return applications
    
    @staticmethod
    def _extract_certifications(text: str) -> List[str]:
        """Extract certifications from text."""
        certifications = []
        seen = set()
        
        for pattern in DocumentExtractor.CERT_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                cert = match.upper().strip()
                # Normalize
                cert = re.sub(r'\s+', ' ', cert)
                if cert not in seen:
                    seen.add(cert)
                    certifications.append(cert)
        
        return certifications[:5]  # Limit to 5
    
    @staticmethod
    def _extract_assets(text: str) -> List[Dict[str, str]]:
        """Extract company assets (facilities, employees, R&D, years)."""
        assets = []
        
        # Patterns for different asset types
        patterns = {
            "plants": r'(\d+)\s*(?:plants?|manufacturing\s+(?:units?|facilities?))',
            "facilities": r'(\d+)\s*(?:facilities?|factories?)',
            "employees": r'(\d+[\d,]*)\+?\s*(?:employees?|people|team\s*(?:members?)?|staff)',
            "rd_centers": r'(\d+)\s*(?:R&D|research|development)\s*(?:centers?|labs?|facilities?)',
            "countries": r'(\d+)\+?\s*countries',
            "years": r'(?:over\s+)?(\d+)\+?\s*(?:years?|decades?)\s*(?:of\s+)?(?:experience|expertise|in\s+business)?',
        }
        
        found = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                found[key] = match.group(1).replace(',', '')
        
        # Build assets list in preferred order
        if found.get("plants") or found.get("facilities"):
            assets.append({
                "label": "Manufacturing\nUnits",
                "value": found.get("plants") or found.get("facilities")
            })
        
        if found.get("rd_centers"):
            assets.append({
                "label": "R&D\nCenters",
                "value": found.get("rd_centers")
            })
        
        if found.get("employees"):
            emp = found["employees"]
            assets.append({
                "label": "Employees",
                "value": f"{emp}+"
            })
        
        if found.get("years"):
            assets.append({
                "label": "Years in\nBusiness",
                "value": f"{found['years']}+"
            })
        
        if found.get("countries"):
            assets.append({
                "label": "Countries\nPresence",
                "value": f"{found['countries']}+"
            })
        
        return assets[:4]  # Limit to 4 assets
    
    @staticmethod
    def _extract_operational_indicators(text: str) -> Dict[str, List[str]]:
        """Extract operational indicators and upcoming facilities."""
        result = {"upcoming_facilities": [], "highlights": []}
        
        section = DocumentExtractor._extract_section(text, "operational")
        if not section:
            return result
        
        # Parse bullet points
        bullets = re.findall(r'[*•]\s*\*?\*?([^*\n]+)\*?\*?(?::\s*([^\n]+))?', section)
        
        for bullet in bullets[:5]:
            title = (bullet[0] or "").strip().strip(':').strip()
            details = (bullet[1] or "").strip()
            
            full_text = f"{title}: {details}" if details else title
            
            # Check if it's a future/upcoming item
            if any(kw in full_text.lower() for kw in ['upcoming', 'planned', 'fy25', 'fy26', 'new', 'expansion', 'capex']):
                result["upcoming_facilities"].append(full_text[:100])
            else:
                result["highlights"].append(full_text[:100])
        
        return result
    
    @staticmethod
    def _extract_export_markets(text: str) -> List[str]:
        """Extract export markets / geographic presence."""
        markets = []
        
        # Look for export mentions
        export_pattern = r'export(?:ing|s)?\s+to\s+(\d+)\+?\s*countries'
        match = re.search(export_pattern, text, re.IGNORECASE)
        
        # Look for specific region/country mentions
        regions = [
            "USA", "Europe", "Middle East", "Asia", "Africa", "LATAM",
            "Germany", "UK", "France", "Japan", "China", "India", 
            "SEA", "GCC", "MENA", "Americas"
        ]
        
        text_upper = text.upper()
        for region in regions:
            if region.upper() in text_upper:
                markets.append(region)
        
        # Also check for "subsidiary in Germany" type patterns
        subsidiary_pattern = r'subsidiary\s+in\s+(\w+)'
        sub_match = re.search(subsidiary_pattern, text, re.IGNORECASE)
        if sub_match:
            country = sub_match.group(1).title()
            if country not in markets:
                markets.append(country)
        
        return markets[:5]
    
    @staticmethod
    def _extract_financial_data(text: str) -> Dict[str, Any]:
        """Extract financial metrics like revenue, EBITDA, years from PDF text."""
        financials = {}
        
        # Try to find year patterns (FY22, 2023, FY24, etc.)
        year_patterns = re.findall(r'\b(?:FY|CY)?[\'"]?(\d{2,4})\b', text)
        fiscal_years = []
        for y in year_patterns:
            try:
                if len(y) == 2:
                    year = int("20" + y)
                else:
                    year = int(y)
                if 2018 <= year <= 2030:
                    fiscal_years.append(f"FY{str(year)[-2:]}")
            except:
                pass
        
        # Deduplicate and sort years
        fiscal_years = sorted(list(set(fiscal_years)))[-5:]  # Last 5 years
        if fiscal_years:
            financials["years"] = fiscal_years
        
        # Try to extract revenue figures (look for Cr, Crore, million, INR patterns)
        revenue_matches = re.findall(
            r'(?:revenue|sales|turnover)[^\d]*?(\d{1,5}(?:[.,]\d{1,2})?)\s*(?:Cr|crore|M|million)?',
            text, re.IGNORECASE
        )
        if revenue_matches:
            try:
                revenues = [float(r.replace(',', '')) for r in revenue_matches[:5]]
                if revenues:
                    financials["revenue"] = revenues
            except:
                pass
        
        # Extract EBITDA
        ebitda_matches = re.findall(
            r'EBITDA[^\d]*?(\d{1,4}(?:[.,]\d{1,2})?)',
            text, re.IGNORECASE
        )
        if ebitda_matches:
            try:
                ebitda = [float(e.replace(',', '')) for e in ebitda_matches[:5]]
                if ebitda:
                    financials["ebitda"] = ebitda
            except:
                pass
        
        # Extract growth rates / CAGR
        cagr_match = re.search(r'(?:CAGR|growth)\s*[:\-]?\s*~?(\d{1,2}(?:\.\d)?)\s*%', text, re.IGNORECASE)
        if cagr_match:
            financials["revenue_cagr"] = cagr_match.group(1) + "%"
        
        # Extract margins
        ebitda_margin = re.search(r'EBITDA\s*(?:margin)?\s*[:\-]?\s*~?(\d{1,2}(?:\.\d)?)\s*%', text, re.IGNORECASE)
        if ebitda_margin:
            financials["ebitda_margin"] = ebitda_margin.group(1) + "%"
        
        pat_margin = re.search(r'(?:PAT|Net\s*Profit)\s*(?:margin)?\s*[:\-]?\s*~?(\d{1,2}(?:\.\d)?)\s*%', text, re.IGNORECASE)
        if pat_margin:
            financials["pat_margin"] = pat_margin.group(1) + "%"
        
        # If we found any data, return it
        if financials:
            print(f"[DocumentExtractor] Financial data extracted: {list(financials.keys())}")
        
        return financials if financials else None
    
    @staticmethod
    def _extract_customers(text: str) -> List[str]:
        """Extract customer names if explicitly mentioned."""
        customers = []
        
        # Look for patterns like "customers include" or "clients such as"
        customer_section = re.search(
            r'(?:customers?|clients?)\s+(?:include|such as|like)\s*:?\s*([^\n.]+)',
            text, re.IGNORECASE
        )
        
        if customer_section:
            names = customer_section.group(1).split(',')
            customers = [n.strip() for n in names if n.strip() and len(n.strip()) > 2]
        
        # Also check for "MNC customer" mentions
        mnc_match = re.search(r'(?:new\s+)?MNC\s+customer', text, re.IGNORECASE)
        if mnc_match and not customers:
            customers.append("Major MNC Customer")
        
        return customers[:6]
    
    @staticmethod
    def merge_with_ai_narrative(extracted: Dict, ai_generated: Dict) -> Dict:
        """
        Merge extracted data with AI-generated narrative.
        Prefers extracted data, falls back to AI for missing fields.
        """
        if not extracted:
            return ai_generated
        if not ai_generated:
            return extracted
        
        result = {
            "slide_1": {},
            "slide_3": {},
        }
        
        # Merge slide_1 fields
        slide_1_fields = ["biz_desc", "customers", "assets", "certifications", 
                         "product_portfolio", "applications", "revenue_split"]
        
        for field in slide_1_fields:
            extracted_val = extracted.get("slide_1", {}).get(field)
            ai_val = ai_generated.get("slide_1", {}).get(field)
            
            if extracted_val:
                result["slide_1"][field] = extracted_val
            elif ai_val:
                result["slide_1"][field] = ai_val
        
        # Merge slide_3 fields
        slide_3_fields = ["global_reach", "export_markets", "upcoming_facilities",
                         "assumptions", "investment_highlights", "why_invest"]
        
        for field in slide_3_fields:
            extracted_val = extracted.get("slide_3", {}).get(field)
            ai_val = ai_generated.get("slide_3", {}).get(field)
            
            if extracted_val:
                result["slide_3"][field] = extracted_val
            elif ai_val:
                result["slide_3"][field] = ai_val
        
        # Copy financials from AI if present (file extraction handles this separately)
        if ai_generated.get("financials"):
            result["financials"] = ai_generated["financials"]
        
        # Copy website if extracted
        if extracted.get("website"):
            result["website"] = extracted["website"]
        
        return result
