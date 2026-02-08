import json, sys
from pathlib import Path
from tabulate import tabulate
from colorama import Fore, Style, init

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.models.schemas import ApplicabilityRule
from src.evaluation.evaluator import evaluate_test_cases

init(autoreset=True)

def load_existing_rules():
    """Load rules from existing JSON files instead of re-extracting."""
    rules = {}
    
    json_files = {
        "FAA-2025-23-53.json": "FAA-2025-23-53",
        "EASA-2025-0254.json": "EASA-2025-0254"
    }
    
    for json_file, ad_id in json_files.items():
        json_path = Path("data/extracted") / json_file
        if json_path.exists():
            with open(json_path, 'r') as f:
                data = json.load(f)
                # Convert back to ApplicabilityRule
                if data.get('msn_range'):
                    data['msn_range'] = tuple(data['msn_range'])
                rule = ApplicabilityRule(**data)
                rules[ad_id] = rule
                print(f"✓ Loaded {ad_id} from existing JSON")
        else:
            print(f"⚠️  {json_file} not found")
    
    return rules

def print_table(results):
    data = {}
    for r in results:
        key = f"{r.aircraft.model}|{r.aircraft.msn}|{','.join(r.aircraft.modifications) or 'None'}"
        if key not in data:
            data[key] = {'model': r.aircraft.model, 'msn': r.aircraft.msn, 
                         'mods': ','.join(r.aircraft.modifications) or 'None'}
        status = f"{Fore.GREEN}✅ AFFECTED" if r.is_affected else f"{Fore.RED}❌ NOT AFFECTED"
        data[key][r.ad_id] = status
    
    headers = ["Aircraft", "MSN", "Mods", "FAA AD", "EASA AD"]
    rows = [[d['model'], d['msn'], d['mods'], d.get('FAA-2025-23-53','N/A'), d.get('EASA-2025-0254','N/A')] 
            for d in data.values()]
    
    print("\n" + "="*120 + "\nRESULTS\n" + "="*120)
    print(tabulate(rows, headers=headers, tablefmt="grid"))
    print("="*120 + "\n")

def verify(results):
    expected = {
        ("MD-11F", 48400, ""): {"FAA-2025-23-53": True, "EASA-2025-0254": False},
        ("A320-214", 4500, "mod 24591"): {"FAA-2025-23-53": False, "EASA-2025-0254": False},
        ("A320-214", 4500, ""): {"FAA-2025-23-53": False, "EASA-2025-0254": True}
    }
    
    print("="*80 + "\nVERIFICATION\n" + "="*80)
    passed = True
    for r in results:
        key = (r.aircraft.model, r.aircraft.msn, ','.join(r.aircraft.modifications))
        if key in expected and r.ad_id in expected[key]:
            exp = expected[key][r.ad_id]
            match = r.is_affected == exp
            status = f"{Fore.GREEN}✅ PASS" if match else f"{Fore.RED}❌ FAIL"
            print(f"{status} | {r.aircraft.model} MSN{r.aircraft.msn} | {r.ad_id} | Exp:{exp} Got:{r.is_affected}")
            if not match:
                passed = False
    
    print("="*80)
    print(f"{Fore.GREEN}✅ ALL PASSED" if passed else f"{Fore.RED}❌ FAILED")
    print("="*80 + "\n")
    return passed

def main():
    print("\n" + "#"*80 + "\nEVALUATION\n" + "#"*80 + "\n")
    
    # Load existing rules instead of re-extracting
    rules = load_existing_rules()
    
    if not rules:
        print("❌ No rules found. Run: python -m src.pipeline first")
        return
    
    print(f"✓ Loaded {len(rules)} ADs\n")
    
    results = evaluate_test_cases(rules)
    print_table(results)
    verify(results)
    
    with open("data/extracted/evaluation_results.json", 'w') as f:
        json.dump([r.model_dump() for r in results], f, indent=2, default=str)
    print("✓ Saved results\n")

if __name__ == "__main__":
    main()
