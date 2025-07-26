from pydantic import BaseModel
from typing import Optional

class CourseRequest(BaseModel):
    topic: str
    level: Optional[str] = "débutant"  # débutant, intermédiaire, avancé
    model: Optional[str] = None  # Add model selection
    design: Optional[str] = "Minimal"  # Add design template selection

class CourseResponse(BaseModel):
    title: str
    outline: str
    summary: str
    raw_content: str