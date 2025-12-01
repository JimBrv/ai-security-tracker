from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import uuid

class Website(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    url: str
    description: Optional[str] = None
    last_scraped_at: Optional[datetime] = None

class Analysis(BaseModel):
    summary: str
    attack_vectors: List[str]
    vulnerabilities: List[str]
    affected_components: List[str]
    impact_level: str  # e.g., "Critical", "High", "Medium", "Low"
    technical_details: str
    published_date: Optional[str] = None

class Event(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    url: str
    source_website_id: str
    published_at: datetime = Field(default_factory=datetime.now)
    analysis: Analysis
    raw_content_snippet: Optional[str] = None

class EventArray(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event: List[Event]=None
