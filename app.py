import streamlit as st
import sys
import os
from pathlib import Path

# Get the absolute path of the project root
PROJECT_ROOT = Path(__file__).parent.absolute()
# Add the project root to sys.path so that modules can be found
sys.path.append(str(PROJECT_ROOT))

from config.settings import DEFAULT_AI_SUGGESTIONS
from core.audio_processor import AudioProcessor
from core.ai_suggestions import AISuggestions
from core.segment_manager import SegmentManager
from core.file_handler import FileHandler
from ui.pages import render_main_page
from ui.styles import load_styles
from utils.logging import setup_logging

logger = setup_logging()

def initialize_session_state():
    """Initialize Streamlit session state with default values."""
    defaults = {
        'initialized': False,
        'segments': [],
        'current_time1': 0.0,
        'current_time2': 0.0,
        'target_tempo': 120.0,
        'target_key': 'C',
        'y1': None,
        'y2': None,
        'sr1': None,
        'sr2': None,
        'ai_style': 'Auto-Detect',
        'ai_segment_length': 'Auto-Detect',
        'ai_transition_type': 'Auto-Detect',
        'ai_volume': None,
        'ai_crossfade': None,
        'ai_eq': None,
        'preview_path': None,
        'processing': False,
        'show_saved_segments': True,
        'saved_segments': [],
        'features1': None,
        'features2': None,
        'song1_path': None,
        'song2_path': None,
        'segment_prompt': '',
        'suggestions': None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def set_page_config():
    """Set page configuration for the Streamlit app."""
    st.set_page_config(
        page_title="Mashup AI Generator",
        page_icon="🎵",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Load styles from the styles module
    load_styles()

def main():
    """Main function to run the Streamlit app."""
    # Set page configuration
    set_page_config()
    
    # Initialize session state
    initialize_session_state()

    # Initialize core components
    file_handler = FileHandler()
    audio_processor = AudioProcessor()
    ai_suggestions = AISuggestions()
    segment_manager = SegmentManager(audio_processor)

    # Store resources in session state for access across modules
    st.session_state.resources = {
        'separator': audio_processor.separator,
        'analyzer': audio_processor.analyzer,
        'aligner': audio_processor.aligner,
        'mixer': audio_processor.mixer,
        'namer': audio_processor.namer,
        'has_openai': file_handler.has_openai
    }

    # Render main page
    render_main_page(
        file_handler=file_handler,
        audio_processor=audio_processor,
        ai_suggestions=ai_suggestions,
        segment_manager=segment_manager
    )

if __name__ == "__main__":
    main()