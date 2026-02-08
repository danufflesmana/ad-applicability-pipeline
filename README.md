# AD Applicability Extraction Pipeline

Automated system for extracting applicability rules from Airworthiness Directive PDFs and evaluating aircraft compliance using LLMs.

## 🎯 Results

✅ **100% accuracy** on all verification test cases  
✅ Successfully extracted rules from 2 ADs (FAA & EASA)  
✅ Deterministic evaluation logic  
✅ Structured JSON output  

## 🚀 Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Install poppler (Ubuntu/Debian)
sudo apt-get install poppler-utils

# Download PDFs to data/raw/
# - FAA_AD_2025_23_53.pdf
# - EASA_AD_2025_0254.pdf

# Run extraction
python -m src.pipeline

# Run evaluation
python tests/run_evaluation.py
```

## 📁 Project Structure
```
ad-applicability-pipeline/
├── src/
│   ├── config.py              # API configuration
│   ├── pipeline.py            # Main orchestrator
│   ├── extraction/            # PDF text extraction
│   ├── parsing/               # LLM parsing
│   ├── models/                # Pydantic data models
│   └── evaluation/            # Evaluation logic
├── data/
│   ├── raw/                   # Input PDFs
│   └── extracted/             # Output JSON
├── tests/
│   └── run_evaluation.py      # Test suite
└── requirements.txt
```

## 🛠 Technology Stack

- **API:** LiteLLM Proxy (Gemini 2.5 Flash)
- **PDF Processing:** pdfplumber
- **Data Validation:** Pydantic
- **Language:** Python 3.12

## 📊 Architecture

**3-Stage Pipeline:**
1. **PDF Ingestion** - Text extraction with quality checks
2. **Structured Extraction** - LLM parsing (temp=0 for determinism)
3. **Deterministic Evaluation** - Pure Python boolean logic

**Key Design Decision:** AI for semantic understanding (extraction), deterministic logic for compliance decisions (evaluation).

## 🧪 Verification Results

| Aircraft | MSN | Modifications | FAA AD | EASA AD | Status |
|----------|-----|---------------|--------|---------|--------|
| MD-11F | 48400 | None | ✅ | ❌ | ✅ PASS |
| A320-214 | 4500 | mod 24591 | ❌ | ❌ | ✅ PASS |
| A320-214 | 4500 | None | ❌ | ✅ | ✅ PASS |

## 📝 Output Format
```json
{
  "ad_id": "FAA-2025-23-53",
  "aircraft_models": ["MD-11", "MD-11F"],
  "msn_range": null,
  "excluded_modifications": [],
  "confidence": 1.0,
  "extraction_method": "text+llm"
}
```

## 📄 Documentation

See [report.md](report.md) for detailed technical analysis including:
- Approach & architecture
- Trade-off analysis
- Challenges & solutions
- Limitations & future work

## 👤 Author

Danu Febriansyah - Data Science/AI Engineer Assignment
