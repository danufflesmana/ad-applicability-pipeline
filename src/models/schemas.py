"""Pydantic data models for AD applicability."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Tuple
from datetime import datetime

class ApplicabilityRule(BaseModel):
    """Structured representation of AD applicability rules."""
    ad_id: str
    aircraft_models: List[str] = Field(min_length=1)
    msn_range: Optional[Tuple[int, int]] = None
    excluded_modifications: List[str] = Field(default_factory=list)
    required_modifications: List[str] = Field(default_factory=list)
    
    extraction_method: str
    source_page: int = 1
    confidence: float = Field(ge=0.0, le=1.0)
    raw_applicability_text: str = ""
    ambiguity_flags: List[str] = Field(default_factory=list)
    extracted_at: datetime = Field(default_factory=datetime.now)
    
    @field_validator('msn_range')
    @classmethod
    def validate_msn_range(cls, v):
        if v is not None:
            min_msn, max_msn = v
            if min_msn > max_msn:
                raise ValueError(f"Invalid MSN range: {min_msn} > {max_msn}")
        return v
    
    @field_validator('aircraft_models')
    @classmethod
    def normalize_models(cls, v):
        return [model.strip().upper() for model in v]
    
    def to_dict(self):
        data = self.model_dump()
        data['extracted_at'] = data['extracted_at'].isoformat()
        return data

class Aircraft(BaseModel):
    """Aircraft configuration."""
    model: str
    msn: int = Field(gt=0)
    modifications: List[str] = Field(default_factory=list)
    
    @field_validator('model')
    @classmethod
    def normalize_model(cls, v):
        return v.strip().upper()
    
    @field_validator('modifications')
    @classmethod
    def normalize_modifications(cls, v):
        normalized = []
        for mod in v:
            mod_clean = mod.strip().lower()
            normalized.append(mod_clean)
        return normalized

class EvaluationResult(BaseModel):
    """Result of evaluating aircraft against AD."""
    aircraft: Aircraft
    ad_id: str
    is_affected: bool
    reason: str
    confidence: float = Field(ge=0.0, le=1.0)
    evaluated_at: datetime = Field(default_factory=datetime.now)
