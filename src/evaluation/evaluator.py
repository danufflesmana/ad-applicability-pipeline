from typing import List, Tuple
from src.models.schemas import Aircraft, ApplicabilityRule, EvaluationResult

def normalize_model(m: str) -> str:
    return m.upper().replace("-", "").replace(" ", "")

def normalize_mod(m: str) -> str:
    # Extract just the number/ID
    normalized = m.lower().strip()
    normalized = normalized.replace("modification", "").replace("mod", "")
    normalized = normalized.replace("service bulletin", "").replace("sb", "")
    normalized = normalized.replace("airbus", "").strip()
    # Remove extra spaces and dashes
    normalized = normalized.replace(" ", "").replace("-", "")
    return normalized

def evaluate_aircraft(aircraft: Aircraft, rule: ApplicabilityRule) -> EvaluationResult:
    reasons = []
    
    # Check model
    aircraft_norm = normalize_model(aircraft.model)
    model_match = any(aircraft_norm == normalize_model(rm) or 
                      aircraft_norm in normalize_model(rm) or
                      normalize_model(rm) in aircraft_norm
                      for rm in rule.aircraft_models)
    reasons.append(f"Model: {'match' if model_match else 'no match'}")
    
    if not model_match:
        return EvaluationResult(aircraft=aircraft, ad_id=rule.ad_id, is_affected=False,
                                reason="; ".join(reasons), confidence=0.95)
    
    # Check MSN
    if rule.msn_range:
        min_msn, max_msn = rule.msn_range
        if not (min_msn <= aircraft.msn <= max_msn):
            reasons.append(f"MSN out of range")
            return EvaluationResult(aircraft=aircraft, ad_id=rule.ad_id, is_affected=False,
                                    reason="; ".join(reasons), confidence=0.95)
    
    # Check excluded mods - IMPROVED
    if rule.excluded_modifications:
        aircraft_mods_norm = {normalize_mod(m) for m in aircraft.modifications}
        excluded_mods_norm = {normalize_mod(m) for m in rule.excluded_modifications}
        
        # Check if any excluded mod number appears in aircraft mods
        for excluded in excluded_mods_norm:
            for aircraft_mod in aircraft_mods_norm:
                if excluded in aircraft_mod or aircraft_mod in excluded:
                    reasons.append(f"Has excluded mod: {excluded}")
                    return EvaluationResult(aircraft=aircraft, ad_id=rule.ad_id, is_affected=False,
                                            reason="; ".join(reasons), confidence=0.90)
    
    return EvaluationResult(aircraft=aircraft, ad_id=rule.ad_id, is_affected=True,
                            reason="; ".join(reasons) + " → AFFECTED", confidence=rule.confidence)

def evaluate_test_cases(rules: dict) -> List[EvaluationResult]:
    test_aircraft = [
        Aircraft(model="MD-11", msn=48123, modifications=[]),
        Aircraft(model="DC-10-30F", msn=47890, modifications=[]),
        Aircraft(model="Boeing 737-800", msn=30123, modifications=[]),
        Aircraft(model="A320-214", msn=5234, modifications=[]),
        Aircraft(model="A320-232", msn=6789, modifications=["mod 24591"]),
        Aircraft(model="A320-214", msn=7456, modifications=["SB A320-57-1089"]),
        Aircraft(model="A321-111", msn=8123, modifications=[]),
        Aircraft(model="A321-112", msn=364, modifications=["mod 24977"]),
        Aircraft(model="A319-100", msn=9234, modifications=[]),
        Aircraft(model="MD-10-10F", msn=46234, modifications=[]),
        Aircraft(model="MD-11F", msn=48400, modifications=[]),
        Aircraft(model="A320-214", msn=4500, modifications=["mod 24591"]),
        Aircraft(model="A320-214", msn=4500, modifications=[]),
    ]
    
    results = []
    for aircraft in test_aircraft:
        for ad_id, rule in rules.items():
            results.append(evaluate_aircraft(aircraft, rule))
    return results
