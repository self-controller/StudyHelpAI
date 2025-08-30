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
from src.models.lecture_models import SubTopic, Assignment, DocNotes
from src.integrations.google_docs import GoogleDocsClient
from src.integrations.google_sheets import GoogleSheetsClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LectureProcessor:
    def __init__(self, model_name: str = "gpt-4.1-nano", whisper_model: str = "base"):
        load_dotenv()
        self.transcriber = whisper.load_model(whisper_model)
        self.base_dir = Path(__file__).resolve().parents[2]
        self.model_name = model_name
        self.transcriptions_dir = self.base_dir/ "data" / "transcriptions"
        self.notes_dir = self.base_dir/ "data" / "notes"
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        self.transcriptions_dir.mkdir(parents=True, exist_ok=True)
        self.notes_dir.mkdir(parents=True, exist_ok=True)

    #Transcribes audio file to text and save as JSON
    def transcribe(self, recording_path: str) -> str:
        try:
            rp = Path(recording_path)
            if not rp.exists():
                logger.error(f"Recording {recording_path} does not exist.")
                return None
            recording_name = rp.stem
            trans_path = self.transcriptions_dir / f"{recording_name}.json"
            if trans_path.exists():
                return str(trans_path)
            
            result = self.transcriber.transcribe(recording_path, language='en', verbose=True)

            # Save transcription to JSON file
            with open(trans_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            logger.info(f"Transcription saved to: {trans_path}")
            return str(trans_path)
        except Exception as e:
            logger.error(f"Error transcribing {recording_path}: {e}")
            return None

    #Extracts structured notes from transcription text using OpenAI API
    def extract_structured_notes(self, transcription_text: str) -> Optional[DocNotes]:
        system_msg = messages[0]['content'] if messages and 'content' in messages[0] else \
                "You are a careful note-taking assistant."
        prompt_messages = [
                {'role': 'system', 'content': system_msg},
                {'role': 'user',
                 'content': f"Please analyze this lecture transcription and extract structured notes:\n\n{transcription_text}"}
            ]
        
        logger.info("Extracting structured notes from transcription...")

        response = self.client.responses.parse(
                input=prompt_messages,
                model=self.model_name,
                text_format=DocNotes,
            )
        
        notes: DocNotes = response.output_parsed
        logger.info("Structured notes extracted successfully.")
        return notes
    
    def save_notes(self, notes: DocNotes, filename: str) -> str:
        """Save structured notes to JSON file"""
        try:
            notes_file = self.notes_dir / f"{filename}_notes.json"
            
            with open(notes_file, 'w', encoding='utf-8') as f:
                json.dump(notes.model_dump(), f, ensure_ascii=False, indent=2)
            
            logger.info(f"Notes saved to: {notes_file}")
            return str(notes_file)
        except Exception as e:
            logger.error(f"Error saving notes: {e}")
            return None

    def process_lecture(self, recording_path: str) -> Optional[DocNotes]:
        try:
            # Transcribe audio
            logger.info(f"Starting processing of: {recording_path}")
            transcription_path = self.transcribe(recording_path)
            if not transcription_path:
                return None
            
            # Load transcription text
            try:
                with open(transcription_path, 'r', encoding='utf-8') as f:
                    transcription_data = json.load(f)
                transcription_text = transcription_data['text']
                logger.info("Transcription loaded successfully")
            except Exception as e:
                logger.error(f"Error loading transcription: {e}")
                return None
            
            # Extract structured notes
            notes = self.extract_structured_notes(transcription_text)
            if not notes:
                return None
            
            # Save notes
            recording_name = Path(recording_path).stem
            saved_path = self.save_notes(notes, recording_name)
            if saved_path:
                logger.info(f"Processing complete! Notes saved to: {saved_path}")
            doc_client = GoogleDocsClient()
            sheet_client = GoogleSheetsClient()
            doc_id = doc_client.create_doc(f"{notes.main_topic} - Lecture Notes")
            doc_client.write_text( doc_id, transcription_text)
            sheet_id = sheet_client.get_or_create_spreadsheet("Assignments_Tracker")["id"]
            sheet_client.write_data(
                sheet_id,
                "Sheet1!A:C",
                [[assignment.title, assignment.description or "", assignment.due_date] for assignment in notes.assignments]
            )
            return notes
            
        except Exception as e:
            logger.error(f"Error in process_lecture: {e}")
            return None
        


    