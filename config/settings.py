from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
DATA_DIR = PROJECT_ROOT / "data"
SONGS_DIR = DATA_DIR / "songs"
OUTPUT_DIR = DATA_DIR / "output"
TEMP_DIR = DATA_DIR / "temp"
SEPARATED_DIR = TEMP_DIR / "separated"
SEGMENTS_DIR = DATA_DIR / "segments"
PREVIEW_DIR = TEMP_DIR / "previews"

# Default AI suggestions
DEFAULT_AI_SUGGESTIONS = {
    'transition_type': 'Crossfade',
    'transition_duration': 4.0,
    'mood_match': 75,
    'energy_match': 80,
    'recommended_style': 'Auto-Detect',
    'complexity': 'Medium'
}

# Audio settings
DEFAULT_VOLUME = 0.8
DEFAULT_PITCH = 0.0
DEFAULT_CROSSFADE = 0.5
DEFAULT_EQ = {'bass': 0.0, 'mid': 0.0, 'treble': 0.0}

# Style descriptions for UI
STYLE_DESCRIPTIONS = {
    "Auto-Detect": "AI will analyze both songs and choose the best style",
    "Energetic": "Fast-paced transitions, high energy sections, perfect for dance/pop",
    "Smooth": "Gradual transitions, flowing melodies, ideal for R&B/soul",
    "Dramatic": "Contrasting sections, dynamic changes, great for rock/classical",
    "Playful": "Creative transitions, unexpected combinations, fun for experimental mixes",
    "Custom": "Define your own style with specific parameters"
}