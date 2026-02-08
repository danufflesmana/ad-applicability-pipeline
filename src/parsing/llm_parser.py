import json
from typing import Dict
from src.config import get_completion

def parse_with_llm(text: str, ad_id: str, page: int = 1) -> Dict:
    print(f"\n{'='*60}\nLLM PARSING: {ad_id}\n{'='*60}")
    
    prompt = f"""Extract applicability rules from this AD text.

Return ONLY valid JSON:
{{
  "aircraft_models": ["list of models"],
  "msn_range": [min, max] or null,
  "excluded_modifications": ["mods that exempt"],
  "confidence": 0.0-1.0,
  "raw_applicability_text": "original text"
}}

AD TEXT:
{text}"""
    
    try:
        response = get_completion(messages=[{"role": "user", "content": prompt}], use_vision=False)
        result_text = response.choices[0].message.content
        print(f"✓ Received {len(result_text)} chars")
        
        # Parse JSON
        result_dict = json.loads(result_text)
        
        # Handle if LLM returns list instead of dict
        if isinstance(result_dict, list):
            result_dict = result_dict[0] if result_dict else {}
        
        # Set defaults
        if not isinstance(result_dict, dict):
            raise ValueError("Invalid response format")
            
        result_dict.setdefault('aircraft_models', [])
        result_dict.setdefault('msn_range', None)
        result_dict.setdefault('excluded_modifications', [])
        result_dict.setdefault('confidence', 0.8)
        result_dict.setdefault('source_page', page)
        result_dict.setdefault('raw_applicability_text', text[:200])
        
        print(f"✓ Parsed successfully")
        print(f"  Models: {result_dict['aircraft_models']}")
        print(f"  Confidence: {result_dict['confidence']:.2f}")
        
        return result_dict
    except json.JSONDecodeError as e:
        print(f"✗ JSON error: {e}")
        print(f"Response: {result_text[:200]}")
        raise
    except Exception as e:
        print(f"✗ Failed: {e}")
        raise
