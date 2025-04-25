import streamlit as st
import os
import librosa
import numpy as np
from typing import Dict
from .components import file_uploader, segment_selector, ai_mashup_controls
from .visualizations import visualize_audio, cached_visualize_timeline
from core.audio_processor import AudioProcessor
from core.ai_suggestions import AISuggestions
from core.segment_manager import SegmentManager
from core.file_handler import FileHandler
from config.settings import SONGS_DIR
from utils.logging import setup_logging

logger = setup_logging()

def styled_header(title, icon=""):
    """Create a styled section header."""
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(44, 82, 130, 0.8) 100%); 
         padding: 1rem; border-radius: 8px; 
         margin-top: 2rem; margin-bottom: 1.5rem; border-left: 5px solid #4CAF50;
         box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        <h2 style="margin: 0; font-size: 1.5rem; color: white; display: flex; align-items: center;">
            <span style="margin-right: 0.5rem; font-size: 1.5rem;">{icon}</span>
            <span>{title}</span>
        </h2>
    </div>
    """, unsafe_allow_html=True)

def render_main_page(file_handler: FileHandler, audio_processor: AudioProcessor,
                    ai_suggestions: AISuggestions, segment_manager: SegmentManager):
    """Render the main page of the Streamlit app."""
    try:
        # Header with custom styling
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0; margin-bottom: 2rem; 
             background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(44, 82, 130, 0.8) 100%);
             border-radius: 10px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);">
            <h1 style="color: white; font-size: 3.5rem; margin-bottom: 0.5rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                🎵 Mashup AI Generator
            </h1>
            <p style="color: #e0e0e0; font-size: 1.4rem; max-width: 800px; margin: 0 auto;">
                Create professional-quality mashups powered by AI technology
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        song1, song2 = file_uploader()
        if song1 and song2:
            song1_path = str(file_handler.save_uploaded_file(song1, SONGS_DIR))
            song2_path = str(file_handler.save_uploaded_file(song2, SONGS_DIR))
            st.session_state.song1_path = song1_path
            st.session_state.song2_path = song2_path

            if not st.session_state.initialized:
                with st.spinner("Analyzing songs..."):
                    features1 = audio_processor.analyze_song(song1_path)
                    features2 = audio_processor.analyze_song(song2_path)
                    suggestions = ai_suggestions.get_ai_suggestions(features1, features2, st.session_state.resources['has_openai'])
                    st.session_state.features1 = features1
                    st.session_state.features2 = features2
                    st.session_state.y1 = features1['y'].copy()
                    st.session_state.y2 = features2['y'].copy()
                    st.session_state.sr1 = features1['sr']
                    st.session_state.sr2 = features2['sr']
                    st.session_state.suggestions = suggestions
                    st.session_state.initialized = True
                    st.success("Songs analyzed successfully!")

            render_uploaded_songs(song1_path, song2_path, song1.name, song2.name)
            render_song_analysis(st.session_state.features1, st.session_state.features2)
            render_ai_suggestions(st.session_state.suggestions)
            render_ai_mashup_assistant(song1_path, song2_path, ai_suggestions, segment_manager)
            render_segment_selection(song1_path, song2_path, segment_manager)
            render_final_mashup(song1_path, song2_path, audio_processor, segment_manager)

        file_handler.cleanup_temp_files()
    except Exception as e:
        logger.error(f"Error in main page: {str(e)}")
        st.error(f"An error occurred: {str(e)}")
        file_handler.cleanup_temp_files()

def render_uploaded_songs(song1_path: str, song2_path: str, song1_name: str, song2_name: str):
    """Render uploaded songs section."""
    st.subheader("Uploaded Songs")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Song 1:** {song1_name}")
        st.audio(song1_path)
    with col2:
        st.write(f"**Song 2:** {song2_name}")
        st.audio(song2_path)

def render_song_analysis(features1: Dict, features2: Dict):
    """Render song analysis section."""
    styled_header("Song Analysis", "📊")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Song 1 Features")
        st.write(f"**Tempo:** {features1['tempo']:.1f} BPM")
        st.write(f"**Key:** {features1['key']}")
        st.write(f"**Duration:** {features1['duration']:.1f}s")
        st.write(f"**Energy Level:** {features1['avg_rms']:.2f}")
        st.write(f"**Brightness:** {features1['spectral_centroid']:.2f}")
    with col2:
        st.subheader("Song 2 Features")
        st.write(f"**Tempo:** {features2['tempo']:.1f} BPM")
        st.write(f"**Key:** {features2['key']}")
        st.write(f"**Duration:** {features2['duration']:.1f}s")
        st.write(f"**Energy Level:** {features2['avg_rms']:.2f}")
        st.write(f"**Brightness:** {features2['spectral_centroid']:.2f}")

def render_ai_suggestions(suggestions: Dict):
    """Render AI suggestions section."""
    styled_header("AI Suggestions", "✨")
    st.write("Based on the analysis of both songs, here are the recommended settings:")
    
    # Ensure all numeric values are native Python types to avoid numpy formatting issues
    safe_suggestions = {}
    for key, value in suggestions.items():
        if isinstance(value, (np.number, np.ndarray)):
            safe_suggestions[key] = float(value)
        else:
            safe_suggestions[key] = value
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Technical Settings")
        st.write(f"**Suggested Tempo:** {safe_suggestions['tempo']:.1f} BPM")
        st.write(f"**Suggested Key:** {safe_suggestions['key']}")
        st.write(f"**Recommended Transition:** {safe_suggestions['transition_type']}")
        st.write(f"**Transition Duration:** {safe_suggestions['transition_duration']:.1f}s")
    with col2:
        st.subheader("Style Analysis")
        st.write(f"**Mood Match:** {safe_suggestions['mood_match']}%")
        st.write(f"**Energy Match:** {safe_suggestions['energy_match']}%")
        st.write(f"**Recommended Style:** {safe_suggestions['recommended_style']}")
        st.write(f"**Complexity Level:** {safe_suggestions['complexity']}")
    if 'reasoning' in safe_suggestions:
        st.subheader("AI Reasoning")
        st.info(safe_suggestions['reasoning'])

def render_ai_mashup_assistant(song1_path: str, song2_path: str, ai_suggestions: AISuggestions, segment_manager: SegmentManager):
    """Render AI mashup assistant section."""
    styled_header("AI Mashup Assistant", "🤖")
    
    recommended_style = "Auto-Detect"
    if 'suggestions' in st.session_state and st.session_state.suggestions:
        recommended_style = st.session_state.suggestions.get('recommended_style', "Auto-Detect")
    
    style, segment_length, custom_prompt = ai_mashup_controls(recommended_style)
    st.session_state.ai_style = style
    st.session_state.ai_segment_length = segment_length
    st.session_state.segment_prompt = custom_prompt

    if st.button("Let AI Create Mashup Segments") and not st.session_state.processing:
        st.session_state.processing = True
        if 'saved_segments' in st.session_state:
            for segment in st.session_state.saved_segments:
                try:
                    if os.path.exists(str(segment['path'])):
                        os.remove(str(segment['path']))
                except Exception as e:
                    logger.error(f"Error removing segment file: {str(e)}")
            st.session_state.saved_segments = []

        with st.spinner("AI is analyzing songs and creating optimal segments..."):
            try:
                ai_segments, is_ai_generated = ai_suggestions.get_ai_mashup_segments(
                    st.session_state.y1, st.session_state.sr1,
                    st.session_state.y2, st.session_state.sr2,
                    st.session_state.features1, st.session_state.features2,
                    prompt=st.session_state.segment_prompt,
                    has_openai=st.session_state.resources['has_openai'],
                    style=st.session_state.ai_style,
                    segment_length=st.session_state.ai_segment_length
                )

                for index, segment in enumerate(ai_segments):
                    try:
                        song_path = song1_path if segment['info']['song'] == 1 else song2_path
                        segment_manager.save_segments(song_path, segment['info'], preview=False)
                        logger.info(f"AI generated segment {index} using song {segment['info']['song']}")
                    except Exception as e:
                        st.error(f"Error saving segment: {str(e)}")

                if is_ai_generated:
                    st.success("✨ AI has created and saved mashup segments!")
                    st.subheader("AI's Reasoning")
                    st.write("The AI created these segments based on:")
                    st.write(f"- Selected style: {style}")
                    st.write(f"- Segment length preference: {segment_length}")
                    st.write(f"- Song compatibility: {st.session_state.suggestions['mood_match']}% mood match")
                    st.write(f"- Energy levels: {st.session_state.suggestions['energy_match']}% energy match")
                    st.write(f"- Complexity level: {st.session_state.suggestions['complexity']}")
                else:
                    st.info("AI couldn't create custom segments. Generated fallback segments.")
            except Exception as e:
                logger.error(f"Error generating AI segments: {str(e)}")
                st.error(f"Error generating AI segments: {str(e)}")
        st.session_state.processing = False

def render_segment_selection(song1_path: str, song2_path: str, segment_manager: SegmentManager):
    """Render segment selection section."""
    styled_header("Create & Manage Segments", "✂️")
    segment_info = segment_selector([1, 2])
    col1, col2 = st.columns(2)
    with col1:
        song_path = song1_path if segment_info['song'] == 1 else song2_path
        processed_path = segment_manager.save_segments(song_path, segment_info, preview=True)
        st.audio(processed_path)
    with col2:
        if st.button("Save Segment"):
            try:
                song_path = song1_path if segment_info['song'] == 1 else song2_path
                segment_manager.save_segments(song_path, segment_info, preview=False)
                st.success("Segment saved!")
            except Exception as e:
                st.error(f"Error saving segment: {str(e)}")

    if 'saved_segments' in st.session_state and st.session_state.saved_segments:
        st.subheader("Saved Segments")
        if len(st.session_state.saved_segments) > 1:
            st.subheader("Segment Order")
            segment_manager.get_segment_order(st.session_state.saved_segments)

        for i, saved_segment in enumerate(st.session_state.saved_segments):
            song_path = song1_path if saved_segment['info']['song'] == 1 else song2_path
            with st.expander(f"Saved Segment {i+1}", expanded=False):
                st.subheader("Modify Segment Settings")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    start_time = st.number_input(
                        "Start Time (seconds)", min_value=0.0, step=5.0,
                        value=float(saved_segment['info']['start']), key=f"modify_start_time_{i}"
                    )
                    end_time = st.number_input(
                        "End Time (seconds)", min_value=0.0, step=5.0,
                        value=float(saved_segment['info']['end']), key=f"modify_end_time_{i}"
                    )
                with col2:
                    new_volume = st.slider(
                        "Volume", 0.0, 1.0, value=float(saved_segment['info']['volume']),
                        step=0.1, key=f"volume_saved_{i}"
                    )
                with col3:
                    new_pitch = st.slider(
                        "Pitch Shift (semitones)", -12.0, 12.0, value=float(saved_segment['info']['pitch']),
                        step=0.1, key=f"pitch_saved_{i}"
                    )
                with col4:
                    st.write("EQ Settings")
                    eq = saved_segment['info']['eq']
                    new_eq = {
                        'bass': st.slider("Bass", -12.0, 12.0, value=float(eq['bass']), step=0.1, key=f"bass_saved_{i}"),
                        'mid': st.slider("Mid", -12.0, 12.0, value=float(eq['mid']), step=0.1, key=f"mid_saved_{i}"),
                        'treble': st.slider("Treble", -12.0, 12.0, value=float(eq['treble']), step=0.1, key=f"treble_saved_{i}")
                    }

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Update Settings", key=f"update_saved_{i}"):
                        new_info = {
                            'start': start_time,
                            'end': end_time,
                            'volume': new_volume,
                            'pitch': new_pitch,
                            'eq': new_eq.copy()
                        }
                        if segment_manager.update_segment(i, new_info, song_path):
                            st.success("Settings updated successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to update segment settings.")

                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Song:** {saved_segment['info']['song']}")
                    st.write(f"**Start:** {saved_segment['info']['start']:.1f}s")
                    st.write(f"**End:** {saved_segment['info']['end']:.1f}s")
                    st.write(f"**Volume:** {saved_segment['info']['volume']:.1f}")
                    st.write(f"**Pitch:** {saved_segment['info']['pitch']:.1f}")
                    st.write(f"**Crossfade:** {saved_segment['info']['crossfade']:.1f}s")
                with col2:
                    st.write("**EQ Settings:**")
                    st.write(f"Bass: {eq.get('bass', 0):.1f}")
                    st.write(f"Mid: {eq.get('mid', 0):.1f}")
                    st.write(f"Treble: {eq.get('treble', 0):.1f}")
                    try:
                        st.audio(str(saved_segment['path']))
                    except Exception as e:
                        st.error(f"Error playing preview: {str(e)}")
                    if st.button("Remove", key=f"remove_saved_{i}"):
                        try:
                            file_path = str(saved_segment['path'])
                            if os.path.exists(file_path):
                                os.remove(file_path)
                            st.session_state.saved_segments.pop(i)
                            st.success("Segment removed!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error removing segment: {str(e)}")

def render_final_mashup(song1_path: str, song2_path: str, audio_processor: AudioProcessor, segment_manager: SegmentManager):
    """Render final mashup section."""
    styled_header("Final Mashup", "🎵")
    if st.button("Create Mashup", key="create_mashup"):
        if not st.session_state.saved_segments:
            st.error("Please save at least one segment to create a mashup")
        else:
            try:
                with st.spinner("Creating final mashup..."):
                    segments = [saved['info'] for saved in st.session_state.saved_segments]
                    for i, segment in enumerate(segments):
                        logger.info(f"Final mashup input - Segment {i}: song={segment['song']}, start={segment['start']}, end={segment['end']}")
                    results = audio_processor.create_final_mashup(
                        song1_path, song2_path, st.session_state.target_tempo,
                        st.session_state.target_key, segments
                    )

                    st.success("🎵 Your mashup is ready!")
                    st.write(f"**Name:** {results['mashup_name']}")
                    st.audio(str(results['mashup_path']))

                    y, sr = librosa.load(str(results['mashup_path']))
                    visualize_audio(y, sr, "Final Mashup Waveform")

                    with open(str(results['mashup_path']), 'rb') as f:
                        st.download_button(
                            label="Download Mashup",
                            data=f,
                            file_name=f"{results['mashup_name']}.wav",
                            mime="audio/wav"
                        )
            except Exception as e:
                st.error(f"Error creating mashup: {str(e)}")
                logger.error(f"Mashup creation error: {str(e)}")