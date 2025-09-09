from pydantic import BaseModel, Field
from openai import OpenAI
from typing import Optional
import json
import whisper
import os
from dotenv import load_dotenv
import logging
from pathlib import Path

from src.prompts.prompts import messages
from src.models.lecture_models import SubTopic, Assignment, DocNotes, EnhancedResult, EnhancedDocNotes
from src.integrations.google_docs import GoogleDocsClient
from src.integrations.google_sheets import GoogleSheetsClient
from src.prompts.prompts import messages_for_enhanced_notes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NoteProcessor:
    def __init__(self, model_name: str = 'gpt-4.1'):
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model_name = model_name
        # create directory for detailed notes
        self.final_notes_dir = Path(__file__).resolve().parents[2] / "data" / "detailed_notes"
        self.final_notes_dir.mkdir(parents=True, exist_ok=True)
    
    def process_notes(self, first_pass_notes: DocNotes) -> Optional[EnhancedResult]:
        try:
            # Convert first pass notes to text for prompt
            notes_text = f"\nMain Topic: {first_pass_notes.main_topic}"
            if first_pass_notes.sub_topics:
                notes_text += f"\nSubtopics ({len(first_pass_notes.sub_topics)}):"
                for i, subtopic in enumerate(first_pass_notes.sub_topics, 1):
                    notes_text += f"\n  {i}. {subtopic.title}"
                    notes_text += f"     {subtopic.description}"
                    if subtopic.examples:
                        notes_text += f"     Examples: {', '.join(subtopic.examples)}"
            logger.info("Processing notes for enhanced details...")
            system_msg = messages_for_enhanced_notes[0]['content'] if messages_for_enhanced_notes and 'content' in messages_for_enhanced_notes[0] else \
                    "You are a meticulous note-enhancing assistant."
            prompt_messages = [
                    {'role': 'system', 'content': system_msg},
                    {'role': 'user',
                    'content': f"Please analyze this lecture transcription and extract structured notes:\n\n{notes_text}"}
                ]
            response = self.client.responses.parse(
                input=prompt_messages,
                model=self.model_name,
                text_format=EnhancedResult
            )
            enhanced_result: EnhancedResult = response.output_parsed
            enhanced_notes = EnhancedDocNotes(main_topic=first_pass_notes.main_topic, assignments=first_pass_notes.assignments, sub_topics=enhanced_result.sub_topics, key_takeaways=enhanced_result.key_takeaways)
            logger.info("Enhanced notes processing complete.")

            return enhanced_notes
    
        except Exception as e:
            logger.error(f"Error preparing notes for enhancement: {e}")
            return None

        
    def save_notes(self, notes: EnhancedDocNotes, filename: str) -> str:
        #Save structured notes to JSON file
        try:
            notes_file = self.final_notes_dir / f"{filename}_notes.json"
            
            with open(notes_file, 'w', encoding='utf-8') as f:
                json.dump(notes.model_dump(), f, ensure_ascii=False, indent=2)
            
            logger.info(f"Notes saved to: {notes_file}")
            return str(notes_file)
        except Exception as e:
            logger.error(f"Error saving notes: {e}")
            return None

        


    