import streamlit as st
import os
from pathlib import Path
from typing import Dict
from config.settings import DATA_DIR, SONGS_DIR, OUTPUT_DIR, TEMP_DIR, SEPARATED_DIR, SEGMENTS_DIR, PREVIEW_DIR
from utils.logging import setup_logging

logger = setup_logging()

class FileHandler:
    def __init__(self):
        self.has_openai = bool(os.getenv('OPENAI_API_KEY'))
        self._initialize_directories()

    def _initialize_directories(self):
        """Initialize application directories."""
        for directory in [DATA_DIR, SONGS_DIR, OUTPUT_DIR, TEMP_DIR, SEPARATED_DIR, SEGMENTS_DIR, PREVIEW_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")

    def save_uploaded_file(self, uploaded_file, directory: Path) -> Path:
        """Save uploaded file to the specified directory."""
        try:
            file_path = directory / uploaded_file.name
            logger.info(f"Saving file to: {file_path}")
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            logger.info(f"Successfully saved file: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            raise

    def cleanup_temp_files(self):
        """Clean up temporary files."""
        try:
            for preview_file in PREVIEW_DIR.glob("preview_*.wav"):
                try:
                    os.remove(preview_file)
                    logger.info(f"Cleaned up preview file: {preview_file}")
                except Exception as e:
                    logger.warning(f"Could not remove preview file {preview_file}: {str(e)}")
            for separated_file in SEPARATED_DIR.glob("*.wav"):
                try:
                    os.remove(separated_file)
                    logger.info(f"Cleaned up separated file: {separated_file}")
                except Exception as e:
                    logger.warning(f"Could not remove separated file {separated_file}: {str(e)}")
        except Exception as e:
            logger.error(f"Error cleaning up temporary files: {str(e)}")