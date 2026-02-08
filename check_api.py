import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.config import test_api_connection, list_available_models

print("="*60)
print("API CONNECTION TEST")
print("="*60)

if test_api_connection():
    print("\n API connection successful\n")
    
    print("="*60)
    print("AVAILABLE MODELS")
    print("="*60)
    models = list_available_models()
    
    gemini_models = [m for m in models if 'gemini' in m.lower()]
    
    if gemini_models:
        print("\nGemini Models:")
        for m in gemini_models[:10]:
            print(f"  - {m}")
    
    print(f"\nTotal models: {len(models)}")
else:
    print("\n API connection failed")
