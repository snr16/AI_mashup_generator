import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from utils.logging import setup_logging

logger = setup_logging()

def visualize_audio(y: np.ndarray, sr: int, title: str = "Audio Waveform") -> None:
    """Visualize audio with waveform."""
    try:
        fig, ax = plt.subplots(figsize=(12, 3))
        times = np.linspace(0, len(y)/sr, len(y))
        ax.plot(times, y)
        ax.set_title(title)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Amplitude')
        plt.tight_layout()
        st.pyplot(fig)
    except Exception as e:
        logger.error(f"Error visualizing audio: {str(e)}")
        raise

@st.cache_data
def cached_visualize_timeline(_y: np.ndarray, sr: int, title: str, current_time: float) -> plt.Figure:
    """Cached version of timeline visualization."""
    try:
        fig, ax = plt.subplots(figsize=(12, 3))
        times = np.linspace(0, len(_y)/sr, len(_y))
        ax.plot(times, _y, color='gray', alpha=0.5)
        ax.axvline(x=current_time, color='red', linestyle='--')
        ax.set_title(title)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Amplitude')
        ax.set_xlim(0, len(_y)/sr)
        plt.tight_layout()
        return fig
    except Exception as e:
        logger.error(f"Error visualizing timeline: {str(e)}")
        raise