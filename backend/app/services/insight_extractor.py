from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import os
import re

from app.services.intelligence import IntelligenceService
from app.services.citations import CitationStore


def _split_bullets(text: str, max_items: int = 6) -> List[str]:
    if not text:
        return []
    # Split on newlines or sentence-ish boundaries
    parts = re.split(r"(?:\n+|•\s+|\-\s+)", text)
    cleaned = []
    for p in parts:
        p = p.strip(" \t\r\n-•")
        if len(p) >= 8:
            cleaned.append(p)
    return cleaned[:max_items]


def _pick_nonempty(*vals: Optional[str]) -> Optional[str]:
    for v in vals:
        if v and str(v).strip():
            return str(v).strip()
    return None


class InsightExtractor:
    """
    Turns private parsed packets + public scrape into a structured 'profile'
    ready for PPT templates (sector aware) and captures citations.
    """

    @staticmethod
    def build_profile(
        company_name: str,
        website: Optional[str],
        private_packets: List[Dict[str, Any]],
        public_context: Dict[str, Any],
        citations: CitationStore,
    ) -> Dict[str, Any]:
        aggregated_text = ""
        financials: Dict[str, Any] = {}
        kpis: Dict[str, Any] = {}

        # Private layer: merge
        for pkt in private_packets:
            if not pkt or pkt.get("error"):
                continue
            if "financials" in pkt:
                financials = InsightExtractor._merge_financials(financials, pkt.get("financials") or {})
                citations.add(
                    claim="Financial time-series extracted",
                    source_type="private_file",
                    ref=pkt.get("source_file", ""),
                    details="Excel parse: revenue/EBITDA/PAT series (best-effort).",
                )
            if "text_content" in pkt:
                aggregated_text += "\n" + (pkt.get("text_content") or "")
                # KPI hints from PDFs
                for k, v in (pkt.get("kpis") or {}).items():
                    if v and k not in kpis:
                        kpis[k] = v
                        citations.add(
                            claim=f"KPI extracted: {k} = {v}",
                            source_type="private_file",
                            ref=pkt.get("source_file", ""),
                            details="PDF regex extraction (best-effort).",
                        )

        # Public layer
        public_text = (public_context or {}).get("combined_text") or ""
        if public_text:
            aggregated_text += "\n" + public_text
            for page in (public_context.get("pages") or []):
                url = page.get("url") or ""
                if url:
                    citations.add(
                        claim="Public qualitative context used (business model/products/market)",
                        source_type="public_url",
                        ref=url,
                        details=_pick_nonempty(page.get("description"), page.get("title"), "") or "",
                    )

        # Sector detection
        sector = IntelligenceService.detect_sector(aggregated_text or company_name)

        # Narrative (blind-friendly)
        narrative = IntelligenceService.generate_narrative(sector, financials or {})
        narrative = IntelligenceService.anonymize_content({"company_name": company_name, "website": website, "narrative": narrative}).get("narrative", narrative)
        citations.add(
            claim="Narrative bullets generated (blind teaser)",
            source_type="generated",
            ref="internal",
            details=f"Sector={sector}; financials_used={bool(financials)}; public_used={bool(public_text)}",
        )

        # Sector-aware structure defaults (these will be overridden if private/public yields better signals)
        structure = InsightExtractor._default_structure(sector)

        # KPI cards: compute where possible
        cards = InsightExtractor._kpi_cards(financials, kpis)
        for c in cards:
            citations.add(
                claim=f"Slide KPI card: {c['label']} = {c['value']}",
                source_type="generated" if c.get("source") == "derived" else "private_file",
                ref=c.get("ref", "internal"),
                details=c.get("details", ""),
            )

        # Highlights: sector-aware hooks
        investment_highlights = InsightExtractor._investment_highlights(sector, narrative, financials)
        investment_highlights = [
            IntelligenceService.anonymize_content({"company_name": company_name, "website": website, "t": h}).get("t", h)
            for h in investment_highlights
        ]

        return {
            "company_name": company_name,
            "website": website,
            "sector": sector,
            "financials": financials,
            "kpi_cards": cards,
            "structure": structure,
            "narrative": narrative,
            "investment_highlights": investment_highlights,
        }

    @staticmethod
    def _merge_financials(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
        if not a:
            return b
        out = dict(a)
        # Prefer longer series
        for k in ["years", "revenue", "ebitda", "pat"]:
            av = out.get(k) or []
            bv = b.get(k) or []
            if isinstance(bv, list) and len(bv) > len(av):
                out[k] = bv
        return out

    @staticmethod
    def _default_structure(sector: str) -> Dict[str, Any]:
        s = (sector or "").lower()
        if "chemical" in s or "manufact" in s:
            return {
                "slide_1_bottom_header": "Growth led through its growing product portfolio and offering solutions to diverse sectors",
                "portfolio_items": ["Food Grade", "Industrial Grade", "Derivatives", "Blended Solutions"],
                "applications": ["Bakery", "Cosmetics", "Mining", "Textile", "Oil & Gas", "Pet Food"],
            }
        if "consumer" in s or "d2c" in s:
            return {
                "slide_1_bottom_header": "Growth led through expanding portfolio and omnichannel distribution",
                "portfolio_items": ["Category A", "Category B", "Category C", "Category D"],
                "applications": ["Amazon", "Flipkart", "Own Website", "Retail"],
            }
        if "pharma" in s or "health" in s:
            return {
                "slide_1_bottom_header": "Growth led through differentiated product portfolio and compliance-led positioning",
                "portfolio_items": ["APIs", "Formulations", "CDMO", "Devices"],
                "applications": ["Domestic", "Export", "Hospitals", "Institutions"],
            }
        if "logistics" in s:
            return {
                "slide_1_bottom_header": "Growth led through network density and service breadth",
                "portfolio_items": ["3PL", "Warehousing", "Cold Chain", "Last-Mile"],
                "applications": ["FMCG", "E-commerce", "Pharma", "Industrial"],
            }
        if "saas" in s or "tech" in s:
            return {
                "slide_1_bottom_header": "Growth led through product depth and enterprise expansion",
                "portfolio_items": ["Core Platform", "Add-ons", "Integrations", "Analytics"],
                "applications": ["SMB", "Mid-market", "Enterprise", "Partners"],
            }
        return {
            "slide_1_bottom_header": "Growth led through strong positioning and scalable operations",
            "portfolio_items": ["Product A", "Product B", "Product C", "Product D"],
            "applications": ["Segment 1", "Segment 2", "Segment 3", "Segment 4"],
        }

    @staticmethod
    def _kpi_cards(financials: Dict[str, Any], kpis: Dict[str, Any]) -> List[Dict[str, Any]]:
        cards: List[Dict[str, Any]] = []
        rev = financials.get("revenue") or []
        ebitda = financials.get("ebitda") or []

        # EBITDA margin derived
        if rev and ebitda and len(rev) == len(ebitda) and rev[-1]:
            m = round((ebitda[-1] / rev[-1]) * 100, 1)
            cards.append({"value": f"~{m}%", "label": "EBITDA Margin", "source": "derived", "ref": "internal", "details": "Derived from EBITDA/Revenue latest year"})
        elif kpis.get("ebitda_margin_pct"):
            cards.append({"value": str(kpis["ebitda_margin_pct"]), "label": "EBITDA Margin", "source": "private", "ref": "private"})
        else:
            cards.append({"value": "~--%", "label": "EBITDA Margin", "source": "generated", "ref": "internal"})

        # RoCE
        if kpis.get("roce_pct"):
            cards.append({"value": str(kpis["roce_pct"]), "label": "RoCE", "source": "private", "ref": "private"})
        else:
            cards.append({"value": "--%", "label": "RoCE", "source": "generated", "ref": "internal"})

        # RoE
        if kpis.get("roe_pct"):
            cards.append({"value": str(kpis["roe_pct"]), "label": "RoE", "source": "private", "ref": "private"})
        else:
            cards.append({"value": "--%", "label": "RoE", "source": "generated", "ref": "internal"})

        # Debt note
        if kpis.get("debt_note"):
            cards.append({"value": str(kpis["debt_note"]), "label": "(Last 3 Years)", "source": "private", "ref": "private"})
        else:
            cards.append({"value": "Net Cash/Low Debt", "label": "(Illustrative)", "source": "generated", "ref": "internal"})

        return cards[:4]

    @staticmethod
    def _investment_highlights(sector: str, narrative: Dict[str, str], financials: Dict[str, Any]) -> List[str]:
        s = (sector or "").lower()
        cagr = IntelligenceService._calc_cagr(financials.get("revenue") or [])
        if "chemical" in s or "manufact" in s:
            return [
                "Leading position in a niche portfolio with differentiated processing know-how and high entry barriers.",
                "Exposure to recession-resistant end-markets with strong customer stickiness and repeat business characteristics.",
                "Strategically located manufacturing footprint enabling efficient raw material procurement and logistics.",
                "Established presence in high-compliance export markets supported by certifications and quality systems.",
                f"Superior financial profile with consistent growth (Revenue CAGR ~{cagr}% where applicable) and healthy margins.",
            ]
        if "consumer" in s or "d2c" in s:
            return [
                "Strong brand traction across key online marketplaces supported by high customer repeat behavior.",
                "Attractive unit economics with improving contribution margins and operating leverage potential.",
                "Scaled product portfolio addressing multiple adjacencies with whitespace for category expansion.",
                "Efficient go-to-market supported by data-driven marketing and retention-led growth levers.",
                f"High growth trajectory (CAGR ~{cagr}% where applicable) with clear path to profitability.",
            ]
        if "pharma" in s or "health" in s:
            return [
                "Compliance-led operating model with strong quality systems and process controls.",
                "Diversified product/therapy exposure with potential for complex, higher-margin offerings.",
                "Export-ready footprint supported by certifications and regulatory readiness.",
                "Sticky customer relationships supported by long qualification cycles and switching costs.",
                f"Consistent scale-up with improving margins (Revenue CAGR ~{cagr}% where applicable).",
            ]
        if "logistics" in s:
            return [
                "Network density and service breadth enabling high utilization and strong customer retention.",
                "Strategically located hubs supporting efficient throughput and reduced transit times.",
                "Growing exposure to structurally growing end-markets (e-commerce, pharma, industrial).",
                "Operational levers to expand margins via automation, routing optimization, and scale benefits.",
                f"Visible growth runway with expanding capacity (Revenue CAGR ~{cagr}% where applicable).",
            ]
        if "saas" in s or "tech" in s:
            return [
                "Mission-critical product positioning with high switching costs and sticky customer workflows.",
                "Scalable software economics with strong gross margins and operating leverage potential.",
                "Multiple expansion levers via add-ons, integrations, and enterprise upsell.",
                "Large addressable market with whitespace across verticals and geographies.",
                f"Healthy growth profile (Revenue CAGR ~{cagr}% where applicable) supported by retention-led expansion.",
            ]
        return [
            "Defensible positioning with clear differentiation and durable customer demand drivers.",
            "Operational scale-up with identifiable levers for margin improvement.",
            "Diversified customer/end-market exposure to reduce cyclicality.",
            "Opportunity to accelerate growth via capacity, distribution, or product expansion initiatives.",
            f"Consistent financial trajectory (Revenue CAGR ~{cagr}% where applicable).",
        ]

