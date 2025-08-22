from pydantic import BaseModel, Field
from typing import List, Optional

class SubTopic(BaseModel):
    title: str = Field(..., description="The title or heading of the subtopic")
    description: str = Field(..., description="Detailed explanation or summary of the subtopic")
    examples: Optional[List[str]] = Field(
        None, description="Optional examples or case studies or supporting points/details related to the subtopic"
    )

class Assignment(BaseModel):
    title: str = Field(..., description = "The name or title of the assignment")
    description: Optional[str] = Field(None, description="A detailed description of the expectations of the assignment")
    due_date: str = Field(..., description="The due date of the assignment in YYYY-MM-DD format")

class DocNotes(BaseModel):
    main_topic: str = Field(..., description="The overall topic of the entire lecture")
    sub_topics: List[SubTopic] = Field(..., description="List of structured subtopics with detailed information")
    assignments: List[Assignment] = Field(
        default=[],
        description="List of assignments or tasks mentioned in the lecture, if any")
    key_takeaways: Optional[List[str]] = Field(
        None, description="Optional key takeaways or important points from the lecture")

