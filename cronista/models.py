"""Modelos de datos para el agente de periodismo económico 'El Cronista'."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional

@dataclass
class EditorialMetadata:
    title: str
    slug: str
    subtitle: str
    author: str = "El Cronista Económico (Agente IA Ofertis)"
    publication_date: str = ""
    reading_time_minutes: int = 4
    tags: List[str] = field(default_factory=list)
    lead_paragraph: str = ""
    bulletin_source_id: str = ""

@dataclass
class ArticleSection:
    heading: str
    content: str
    mermaid_chart: Optional[str] = None
    svg_chart_path: Optional[str] = None

@dataclass
class Article:
    metadata: EditorialMetadata
    sections: List[ArticleSection]
    markdown_content: str = ""
    generated_at: str = ""
