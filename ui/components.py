import streamlit as st
from typing import Tuple, Dict, Optional, Any
from config.settings import STYLE_DESCRIPTIONS

def file_uploader() -> Tuple[Optional[Any], Optional[Any]]:
    """Render file uploaders for two songs."""
    st.header("Upload Songs")
    song1 = st.file_uploader("Upload first song", type=['mp3', 'wav'], key='song1')
    song2 = st.file_uploader("Upload second song", type=['mp3', 'wav'], key='song2')
    return song1, song2

def segment_selector(song_choices: list, default_song: int = 1) -> Dict:
    """Render segment selection controls."""
    st.header("Segment Selection")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        song_choice = st.selectbox("Select Song", song_choices, index=default_song-1, key="create_song_select")
    with col2:
        start_time = st.number_input("Start Time (seconds)", min_value=0.0, value=0.0, key="create_start_time")
    with col3:
        end_time = st.number_input("End Time (seconds)", min_value=0.0, value=start_time+20.0, key="create_end_time")
    with col4:
        crossfade = st.number_input("Crossfade (seconds)", min_value=0.0, max_value=2.0, value=0.5, step=0.1, key="create_crossfade")

    st.subheader("Segment Settings")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        volume = st.slider("Volume", 0.0, 1.0, value=0.8, step=0.1, key="create_volume")
    with col2:
        pitch = st.slider("Pitch Shift (semitones)", -12.0, 12.0, value=0.0, step=0.1, key="create_pitch")
    with col3:
        st.write("EQ Settings")
        eq = {
            'bass': st.slider("Bass", -12.0, 12.0, value=0.0, step=0.1, key="create_bass"),
            'mid': st.slider("Mid", -12.0, 12.0, value=0.0, step=0.1, key="create_mid"),
            'treble': st.slider("Treble", -12.0, 12.0, value=0.0, step=0.1, key="create_treble")
        }
    with col4:
        st.write("Transition Type")
        transition_type = st.selectbox("Transition Type", ["Fade", "Crossfade", "Smooth", "Hard"], key="create_transition_type")

    return {
        'song': song_choice,
        'start': start_time,
        'end': end_time,
        'volume': volume,
        'pitch': pitch,
        'eq': eq,
        'crossfade': crossfade,
        'transition_type': transition_type
    }

def ai_mashup_controls(recommended_style: str = "Auto-Detect") -> Tuple[str, str, str]:
    """Render AI mashup controls."""
    st.header("🤖 AI Mashup Assistant")
    st.subheader("Mashup Style")
    
    # Determine the index for the recommended style
    style_list = list(STYLE_DESCRIPTIONS.keys())
    style_list.append(recommended_style)
    try:
        recommended_index = style_list.index(recommended_style)
    except ValueError:
        recommended_index = 0  # Default to Auto-Detect if recommended style not found
    
    col1, col2 = st.columns(2)
    with col1:
        style = st.selectbox(
            "Select Mashup Style",
            style_list,
            index=recommended_index,
            key="ai_style_select"
        )
        st.info(STYLE_DESCRIPTIONS.get(style, "AI recommended style"))
        
        if recommended_style != "Auto-Detect" and recommended_style in STYLE_DESCRIPTIONS:
            st.success(f"✨ AI recommends the '{recommended_style}' style based on song analysis")
    with col2:
        segment_length = st.selectbox(
            "Segment Length",
            ["Auto-Detect", "Short (20-30s)", "Medium (30-40s)", "Long (40-50s)", "Variable"],
            index=0,
            key="ai_length_select"
        )

    custom_prompt = ""
    if style == "Custom":
        st.subheader("Custom Instructions")
        st.write("""
        💡 Tips for writing custom instructions:
        - Focus on 3-4 high-quality transitions between songs
        - Use 3-4 segments per song
        - Segment lengths can vary - choose what sounds best
        - Look for natural transition points (chorus to chorus, verse to verse)
        - Consider energy levels and mood for smooth transitions
        - Use smooth transitions between segments that match the style of the mashup
        """)
        custom_prompt = st.text_area(
            "Provide specific instructions for segment generation",
            placeholder="Example: Create 3-4 transitions focusing on the choruses...",
            key="ai_custom_prompt"
        )

    return style, segment_length, custom_prompt