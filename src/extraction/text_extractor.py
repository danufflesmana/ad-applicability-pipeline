"""PDF text extraction using pdfplumber."""

import pdfplumber
from pathlib import Path
from typing import Tuple

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF."""
    print(f"\n{'='*60}")
    print(f"TEXT EXTRACTION: {Path(pdf_path).name}")
    print(f"{'='*60}")
    
    with pdfplumber.open(pdf_path) as pdf:
        text_parts = []
        for i, page in enumerate(pdf.pages, 1):
            page_text = page.extract_text()
            if page_text:
                text_parts.append(f"--- PAGE {i} ---\n{page_text}")
                print(f"  Page {i}: {len(page_text):,} chars")
            else:
                print(f"  Page {i}: No text found")
        
        full_text = "\n\n".join(text_parts)
        print(f"✓ Total: {len(full_text):,} chars from {len(pdf.pages)} pages")
        return full_text

def extract_applicability_section(text: str) -> Tuple[str, int]:
    """Find and extract Applicability section."""
    print("\nSearching for Applicability section...")
    
    lines = text.split('\n')
    keywords = ['applicability', 'affected products', 'this ad applies to']
    
    applicability_start = None
    start_page = 1
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        
        if line.startswith('--- PAGE'):
            try:
                start_page = int(line.split()[2])
            except:
                pass
        
        for keyword in keywords:
            if keyword in line_lower:
                applicability_start = i
                print(f" Found '{keyword}' at line {i} (page ~{start_page})")
                break
        
        if applicability_start is not None:
            break
    
    if applicability_start is None:
        print(" Could not find Applicability section")
        return "", 1
    
    context_lines = lines[applicability_start:applicability_start + 30]
    applicability_text = '\n'.join(context_lines)
    
    print(f"✓ Extracted {len(applicability_text)} chars")
    print(f"Preview: {applicability_text[:200]}...")
    
    return applicability_text, start_page

def is_text_extraction_good(text: str, min_chars: int = 500) -> Tuple[bool, str]:
    """Check text extraction quality."""
    if len(text) < min_chars:
        return False, f"Text too short ({len(text)} chars)"
    
    words = text.split()
    if len(words) < 100:
        return False, "Too few words"
    
    lines = text.count('\n')
    if lines < 10:
        return False, "Too few lines"
    
    letters = sum(c.isalpha() for c in text)
    if letters < 400:
        return False, "Too few letters"
    
    return True, "Text extraction quality is good"
