import sys
import argparse
import logging
from pathlib import Path
from typing import Optional



from src.core.lecture_processor import LectureProcessor
from src.models.lecture_models import DocNotes
from config import Settings


settings = Settings()


def setup_logging():
    #Configure logging for the application
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('agentic_ai.log')
        ]
    )
    return logging.getLogger(__name__)

def display_notes(notes: DocNotes):
    #Display the processed notes in a formatted way
    print("\n" + "="*60)
    print("LECTURE ANALYSIS RESULTS")
    print("="*60)
    
    print(f"\nMain Topic: {notes.main_topic}")
    
    if notes.sub_topics:
        print(f"\n📋 Subtopics ({len(notes.sub_topics)}):")
        for i, subtopic in enumerate(notes.sub_topics, 1):
            print(f"\n  {i}. {subtopic.title}")
            print(f"     {subtopic.description}")
            if subtopic.examples:
                print(f"     Examples: {', '.join(subtopic.examples)}")
    
    if notes.assignments:
        print(f"\nAssignments ({len(notes.assignments)}):")
        for assignment in notes.assignments:
            print(f"  • {assignment.title}")
            print(f"    Due: {assignment.due_date}")
            if assignment.description:
                print(f"    📄 Details: {assignment.description}")
    
    if notes.key_takeaways:
        print(f"\nKey Takeaways:")
        for takeaway in notes.key_takeaways:
            print(f"  • {takeaway}")
    
    print("\n" + "="*60)

def process_single_file(file_path: str, logger) -> bool:
    #Process a single audio file
    try:
        # Initialize the processor
        processor = LectureProcessor()
        
        # Check if file exists
        if not Path(file_path).exists():
            logger.error(f"File not found: {file_path}")
            return False
        
        logger.info(f"Processing: {file_path}")
        
        # Process the lecture
        notes = processor.process_lecture(file_path)
        
        if notes:
            display_notes(notes)
            logger.info("Successfully processed lecture!")
            return True
        else:
            logger.error("Failed to process lecture")
            return False
            
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")
        return False

def process_directory(directory_path: str, logger) -> None:
    #Process all audio files in a directory
    directory = Path(directory_path)
    
    if not directory.exists():
        logger.error(f"Directory not found: {directory_path}")
        return
    
    # Common audio file extensions
    audio_extensions = {'.mp3', '.wav', '.m4a', '.flac', '.ogg', '.mp4'}
    
    audio_files = [
        f for f in directory.iterdir() 
        if f.is_file() and f.suffix.lower() in audio_extensions
    ]
    
    if not audio_files:
        logger.warning(f"No audio files found in: {directory_path}")
        return
    
    logger.info(f"Found {len(audio_files)} audio files to process")
    
    successful = 0
    for audio_file in audio_files:
        print(f"\n{'='*40}")
        print(f"Processing: {audio_file.name}")
        print(f"{'='*40}")
        
        if process_single_file(str(audio_file), logger):
            successful += 1
        
        print("\n" + "-"*40)
    
    print(f"\n✅ Successfully processed {successful}/{len(audio_files)} files")

def main():
    #Main entry point
    parser = argparse.ArgumentParser(
        description="Process lecture recordings into structured notes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py recording.mp3                    # Process single file
  python main.py recordings/                      # Process all files in directory
  python main.py recording.mp3 --verbose          # Enable verbose output
  python main.py recordings/ --model llama2       # Use different AI model
  """
    )
    
    parser.add_argument(
        'input_path',
        help='Path to audio file or directory containing audio files'
    )
    
    parser.add_argument(
        '--model',
        default=settings.model,
        help=f'OpenAI model to use (default: {settings.model})'
    )
    
    parser.add_argument(
        '--whisper-model',
        default=settings.whisper_model,
        help=f'Whisper model to use (default: {settings.whisper_model})'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--output-format',
        choices=['console', 'json', 'both'],
        default='console',
        help='Output format (default: console)'
    )
    
    args = parser.parse_args()
    
    # Set up logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger = setup_logging()
    
    # Create processor with specified models
    processor_kwargs = {}
    if args.model != settings.model:
        processor_kwargs['model_name'] = args.model
        logger.info(f"Using OpenAI model: {args.model}")
    
    if args.whisper_model != settings.whisper_model:
        processor_kwargs['whisper_model'] = args.whisper_model
        logger.info(f"Using Whisper model: {args.whisper_model}")
    
    # Determine if input is file or directory
    input_path = Path(args.input_path)
    
    if input_path.is_file():
        # Process single file
        success = process_single_file(args.input_path, logger)
        sys.exit(0 if success else 1)
        
    elif input_path.is_dir():
        # Process directory
        process_directory(args.input_path, logger)
        
    else:
        logger.error(f"Invalid path: {args.input_path}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)