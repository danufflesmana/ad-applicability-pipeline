"""Vision-Language Model parser for scanned PDFs."""

import base64
import json
from io import BytesIO
from pathlib import Path
from typing import List, Dict

from pdf2image import convert_from_path
from src.config import get_completion
from src.parsing.llm_parser import create_extraction_prompt

def convert_pdf_to_images(pdf_path: str, max_pages: int = 10, dpi: int = 200) -> List[str]:
    """Convert PDF to base64 images."""
    print(f"\nConverting PDF to images (DPI: {dpi}, Max pages: {max_pages})...")
    
    try:
        images = convert_from_path(pdf_path, dpi=dpi, first_page=1, last_page=max_pages)
        
        base64_images = []
        for i, img in enumerate(images, 1):
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            base64_images.append(img_base64)
            print(f" Page {i} converted")
        
        print(f" Converted {len(base64_images)} pages")
        return base64_images
    except Exception as e:
        print(f" Conversion failed: {e}")
        raise

def parse_with_vlm(pdf_path: str, ad_id: str) -> Dict:
    """Parse with Vision-Language Model."""
    print(f"\n{'='*60}")
    print(f"VLM PARSING: {ad_id}")
    print(f"{'='*60}")
    
    images = convert_pdf_to_images(pdf_path, max_pages=10)
    
    prompt = create_extraction_prompt()
    message_content = [{"type": "text", "text": prompt}]
    
    for img_b64 in images:
        message_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{img_b64}"}
        })
    
    try:
        print(f"Calling Gemini Vision...")
        response = get_completion(
            messages=[{"role": "user", "content": message_content}],
            use_vision=True
        )
        
        result_text = response.choices[0].message.content
        result_dict = json.loads(result_text)
        
        # Set defaults
        result_dict.setdefault('aircraft_models', [])
        result_dict.setdefault('msn_range', None)
        result_dict.setdefault('excluded_modifications', [])
        result_dict.setdefault('required_modifications', [])
        result_dict.setdefault('source_page', 1)
        result_dict.setdefault('confidence', 0.8)
        
        print(f" VLM parsing successful")
        return result_dict
    except Exception as e:
        print(f" VLM failed: {e}")
        raise
