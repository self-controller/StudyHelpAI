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
class EnhancedSubTopic(SubTopic):
    practice_questions: Optional[List[str]] = Field(
        None, description="Practice questions related to subtopic for self-assessment if applicable")
    definitions: Optional[List[str]] = Field(
        None, description="Key Definitions related to the subtopic if applicable"
    )

class EnhancedResult(BaseModel):
    sub_topics: List[EnhancedSubTopic] = Field(..., description="List of structured subtopics with more polished details, more studying focused")
    key_takeaways: Optional[List[str]] = Field(
        None, description="Optional key takeaways or important points from the lecture, more studying focused")

class EnhancedDocNotes(BaseModel):
    main_topic: str = Field(..., description="The overall topic of the entire lecture")
    assignments: List[Assignment] = Field(
        default=[],
        description="List of assignments or tasks mentioned in the lecture, if any"
    )
    sub_topics: List[EnhancedSubTopic] = Field(
        ..., description="List of structured subtopics with more polished details, more studying focused"
    )
    key_takeaways: Optional[List[str]] = Field(
        None, description="Optional key takeaways or important points from the lecture, more studying focused"
    )

    @classmethod
    def from_results(
        cls,
        main_topic: str,
        assignments: List[Assignment],
        enhanced_result: EnhancedResult,
    ) -> "EnhancedDocNotes":
        return cls(
            main_topic=main_topic,
            assignments=assignments,
            sub_topics=enhanced_result.sub_topics,
            key_takeaways=enhanced_result.key_takeaways,
        )