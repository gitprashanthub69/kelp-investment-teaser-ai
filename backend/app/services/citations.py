from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import os
import textwrap

import fitz  # PyMuPDF


@dataclass
class Citation:
    claim: str
    source_type: str  # "private_file" | "public_url" | "generated"
    ref: str  # filepath or URL
    details: str = ""  # page/snippet/etc


class CitationStore:
    def __init__(self) -> None:
        self._items: List[Citation] = []

    def add(self, claim: str, source_type: str, ref: str, details: str = "") -> None:
        self._items.append(Citation(claim=claim, source_type=source_type, ref=ref, details=details))

    def extend(self, items: List[Citation]) -> None:
        self._items.extend(items)

    def to_list(self) -> List[Dict[str, Any]]:
        return [
            {"claim": c.claim, "source_type": c.source_type, "ref": c.ref, "details": c.details}
            for c in self._items
        ]

    def write_pdf(self, output_path: str, title: str = "Citation Document") -> str:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        doc = fitz.open()
        page = doc.new_page()

        def write_line(y: float, txt: str, size: int = 10, bold: bool = False) -> float:
            nonlocal page
            # Wrap to page width
            max_width = page.rect.width - 72  # 1 inch margins
            lines = []
            for raw in txt.split("\n"):
                lines.extend(textwrap.wrap(raw, width=110) or [""])

            for line in lines:
                if y > page.rect.height - 60:
                    page = doc.new_page()
                    y = 50
                # Use default font to avoid platform font issues
                page.insert_text((36, y), line, fontsize=size)
                y += size + 4
            return y

        y = 50
        y = write_line(y, title, size=14, bold=True)
        y += 6
        y = write_line(y, "Each claim/number/image in the PPT is linked to its source.", size=10)
        y += 10

        if not self._items:
            y = write_line(y, "No citations captured.", size=10)
        else:
            for i, c in enumerate(self._items, start=1):
                y = write_line(y, f"{i}. Claim: {c.claim}", size=10, bold=True)
                y = write_line(y, f"   Source: [{c.source_type}] {c.ref}", size=9)
                if c.details:
                    y = write_line(y, f"   Details: {c.details}", size=9)
                y += 6

        doc.save(output_path)
        doc.close()
        return output_path

