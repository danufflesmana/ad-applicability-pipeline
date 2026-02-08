import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from src.extraction.text_extractor import extract_text_from_pdf, extract_applicability_section, is_text_extraction_good
from src.parsing.llm_parser import parse_with_llm
from src.models.schemas import ApplicabilityRule

def extract_ad_rules(pdf_path: str, ad_id: str) -> ApplicabilityRule:
    print(f"\n{'#'*60}\n# PROCESSING: {ad_id}\n{'#'*60}")
    
    full_text = extract_text_from_pdf(pdf_path)
    is_good, reason = is_text_extraction_good(full_text)
    print(f"\nQuality: {reason}")
    
    if not is_good:
        raise Exception("Text extraction failed")
    
    applicability_text, page_num = extract_applicability_section(full_text)
    if not applicability_text:
        raise Exception("Applicability section not found")
    
    raw_result = parse_with_llm(applicability_text, ad_id, page_num)
    
    rule = ApplicabilityRule(
        ad_id=ad_id,
        aircraft_models=raw_result["aircraft_models"],
        msn_range=tuple(raw_result["msn_range"]) if raw_result.get("msn_range") else None,
        excluded_modifications=raw_result.get("excluded_modifications", []),
        required_modifications=[],
        extraction_method="text+llm",
        source_page=raw_result.get("source_page", 1),
        confidence=raw_result.get("confidence", 0.8),
        raw_applicability_text=raw_result.get("raw_applicability_text", "")
    )
    
    print(f"\n{'='*60}\nModels: {', '.join(rule.aircraft_models)}\nExcluded: {rule.excluded_modifications}\n{'='*60}\n")
    return rule

def process_all_ads(pdf_dir: str = "data/raw", output_dir: str = "data/extracted"):
    pdf_dir = Path(pdf_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    ad_files = {
        "FAA_AD_2025_23_53.pdf": "FAA-2025-23-53",
        "EASA_AD_2025_0254.pdf": "EASA-2025-0254"
    }
    
    results = {}
    for pdf_file, ad_id in ad_files.items():
        pdf_path = pdf_dir / pdf_file
        if not pdf_path.exists():
            print(f"⚠️  {pdf_file} not found")
            continue
        
        try:
            rule = extract_ad_rules(str(pdf_path), ad_id)
            results[ad_id] = rule
            
            output_file = output_dir / f"{ad_id}.json"
            with open(output_file, 'w') as f:
                json.dump(rule.to_dict(), f, indent=2)
            print(f"✓ Saved to {output_file}\n")
        except Exception as e:
            print(f"✗ Failed: {e}\n")
    
    return results

if __name__ == "__main__":
    print("="*60 + "\nAD EXTRACTION PIPELINE\n" + "="*60)
    results = process_all_ads()
    print(f"\n{'='*60}\nCOMPLETE: {len(results)}/2 ADs\n{'='*60}")
