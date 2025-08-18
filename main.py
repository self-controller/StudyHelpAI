from ollama import chat
from pydantic import BaseModel, Field
import requests
from typing import List, Optional
import json
import whisper
import os

transcriber = whisper.load_model("base")
recording_path = r"C:\Users\david\projects\agentic_ai1\recordings\ErnWZxJovaM.mp3"

def transcribe(recording_path: str) -> str:
    os.makedirs('transcriptions', exist_ok=True)
    recording_name = os.path.basename(recording_path).split('.')[0]
    if not os.path.exists(recording_path):
        return
    
    trans_path = os.path.join( 'transcriptions', f"{recording_name}.json")
    if (os.path.exists(trans_path)):
        return trans_path
    
    result = transcriber.transcribe(recording_path, language='en', verbose=True)
    
    with open(trans_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return trans_path

class SubTopic(BaseModel):
    title: str = Field(..., description="The title or heading of the subtopic")
    description: str = Field(..., description="Detailed explanation or summary of the subtopic")
    examples: Optional[List[str]] = Field(
        None, description="Optional examples or case studies or supporting points/details related to the subtopic"
    )

class DocNotes(BaseModel):
    main_topic: str = Field(..., description="The overall topic of the entire lecture or speech")
    sub_topics: List[SubTopic] = Field(..., description="List of structured subtopics with detailed information")
    assignments: dict[str, str] = Field(description="The key being name or title of the assignment and the value " 
                                        "being the due date of the assignment in YYYY-MM-DD format")
    
path = transcribe(recording_path)

content = json.load(open(path, 'r'))['text']

messages = [
    {'role': 'system', 'content': 'You are a helpful assistant that helps summarize lectures and speeches into structured notes.'},
    {'role': 'user', 'content': content}
]

response = chat(
    messages=messages,
    model='mistrallite:latest',
    stream=False,
    format=DocNotes.model_json_schema(),
)

response_content = response["message"]["content"]

notes = DocNotes.model_validate_json(response_content)

print(notes.model_dump_json, "\n\n\n")


