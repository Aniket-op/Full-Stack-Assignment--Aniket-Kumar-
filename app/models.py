from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class ScrapeRequest(BaseModel):
    url: str

class SectionContent(BaseModel):
    headings: List[str] = Field(default_factory=list)
    text: str = ""
    links: List[Dict[str, str]] = Field(default_factory=list)
    images: List[Dict[str, str]] = Field(default_factory=list)
    lists: List[List[str]] = Field(default_factory=list)
    tables: List[Any] = Field(default_factory=list)

class Section(BaseModel):
    id: str
    type: str
    label: str
    sourceUrl: str
    content: SectionContent
    rawHtml: str
    truncated: bool

class Interactions(BaseModel):
    clicks: List[str] = Field(default_factory=list)
    scrolls: int = 0
    pages: List[str] = Field(default_factory=list)

class ScrapeError(BaseModel):
    message: str
    phase: str

class ScrapeResult(BaseModel):
    url: str
    scrapedAt: str
    meta: Dict[str, Optional[str]]
    sections: List[Section]
    interactions: Interactions
    errors: List[ScrapeError] = Field(default_factory=list)

class ScrapeResponse(BaseModel):
    result: ScrapeResult

class HealthResponse(BaseModel):
    status: str
