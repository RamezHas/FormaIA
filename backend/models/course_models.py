from pydantic import BaseModel
from typing import Optional

class CourseRequest(BaseModel):
    topic: str
    level: Optional[str] = "débutant"  # débutant, intermédiaire, avancé

class CourseResponse(BaseModel):
    title: str
    outline: str
    summary: str
    raw_content: str
