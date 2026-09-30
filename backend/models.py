from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Dict, Optional, Any
from datetime import datetime

class CategoryEnum(str, Enum):
    ROADS = "ROADS"
    WATER = "WATER"
    ELECTRICITY = "ELECTRICITY"
    HEALTHCARE = "HEALTHCARE"
    EDUCATION = "EDUCATION"
    SANITATION = "SANITATION"
    DIGITAL = "DIGITAL"

class SentimentEnum(str, Enum):
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"
    POSITIVE = "POSITIVE"

class SourceEnum(str, Enum):
    TELEGRAM = "TELEGRAM"
    WEB = "WEB"

class DataTypeEnum(str, Enum):
    REAL = "REAL"
    SYNTHETIC = "SYNTHETIC"

class CitizenRequest(BaseModel):
    id: Optional[int] = None
    raw_text: str
    translated_text: str
    language_detected: str
    category: CategoryEnum
    location_district: str
    location_state: str
    urgency: int
    sentiment: SentimentEnum
    latitude: Optional[float]
    longitude: Optional[float]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: SourceEnum
    data_type: DataTypeEnum = DataTypeEnum.REAL

class DistrictPriority(BaseModel):
    district_name: str
    state: str
    priority_score: float
    demand_density: float
    infra_gap: float
    population_weight: float
    urgency_factor: float
    category_breakdown: Dict[str, int]
    total_requests: int
    top_issues: List[str]

class PolicyBrief(BaseModel):
    title: str
    summary: str
    top_districts: List[str]
    recommendations: List[str]
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    data_coverage: str

class GeminiClassification(BaseModel):
    translated_text: str
    language: str
    category: CategoryEnum
    district: str
    state: str
    urgency: int
    sentiment: SentimentEnum
    latitude: Optional[float] = None
    longitude: Optional[float] = None
