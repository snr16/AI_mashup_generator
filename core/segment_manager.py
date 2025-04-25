import streamlit as st
import os
from typing import Dict, List
from config.settings import SEGMENTS_DIR, PREVIEW_DIR, DEFAULT_VOLUME, DEFAULT_PITCH, DEFAULT_CROSSFADE, DEFAULT_EQ
from datetime import datetime
from .audio_processor import AudioProcessor
from utils.logging import setup_logging

logger = setup_logging()

class SegmentManager:
    def __init__(self, audio_processor: AudioProcessor):
        self.audio_processor = audio_processor

    def save_segments(self, song_path: str, segment_info: Dict, preview: bool = False) -> str:
        """Save a segment with its info to the session state."""
        try:
            os.makedirs(SEGMENTS_DIR, exist_ok=True)
            if 'saved_segments' not in st.session_state:
                st.session_state.saved_segments = []

            index = len(st.session_state.saved_segments)
            output_path = f"{PREVIEW_DIR}/preview_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.wav" if preview else f"{SEGMENTS_DIR}/segment_{index}.wav"

            processed_path = self.audio_processor.process_segment(
                song_path,
                start_time=segment_info['start'],
                end_time=segment_info['end'],
                volume=segment_info['volume'],
                pitch=segment_info['pitch'],
                eq=segment_info['eq'],
                crossfade=segment_info['crossfade'],
                output_path=output_path,
                preview=preview
            )

            if not preview:
                st.session_state.saved_segments.append({
                    'path': processed_path,
                    'info': segment_info.copy()
                })

            return processed_path
        except Exception as e:
            logger.error(f"Error saving segment: {str(e)}")
            raise

    def update_segment(self, index: int, new_info: Dict, song_path: str) -> bool:
        """Update a segment with new parameters and recreate preview."""
        try:
            if 'saved_segments' in st.session_state and index < len(st.session_state.saved_segments):
                saved_segment = st.session_state.saved_segments[index]
                original_info = saved_segment['info'].copy()

                for key, value in new_info.items():
                    if key in original_info:
                        if isinstance(value, dict) and isinstance(original_info[key], dict):
                            for inner_key, inner_value in value.items():
                                original_info[key][inner_key] = inner_value
                        else:
                            original_info[key] = value

                current_path = str(saved_segment['path'])
                if os.path.exists(current_path):
                    os.remove(current_path)

                processed_path = self.audio_processor.process_segment(
                    song_path,
                    start_time=original_info['start'],
                    end_time=original_info['end'],
                    volume=original_info['volume'],
                    pitch=original_info['pitch'],
                    eq=original_info['eq'],
                    crossfade=original_info['crossfade'],
                    output_path=current_path,
                    preview=False
                )

                saved_segment['path'] = processed_path
                saved_segment['info'] = original_info
                st.session_state.saved_segments[index] = saved_segment
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating segment: {str(e)}")
            return False

    def add_segment(self, song_choice: int, start_time: float, end_time: float,
                    volume: float, pitch: float, eq: Dict, crossfade: float):
        """Add a segment without causing a rerun."""
        if end_time > start_time:
            new_segment = {
                'song': song_choice,
                'start': start_time,
                'end': end_time,
                'volume': volume,
                'pitch': pitch,
                'eq': eq.copy(),
                'crossfade': crossfade
            }
            st.session_state.segments.append(new_segment)

    def remove_segment(self, index: int):
        """Remove a segment without causing a rerun."""
        if index < len(st.session_state.segments):
            st.session_state.segments.pop(index)

    def get_segment_order(self, segments: List[Dict]) -> List[int]:
        """Allow reordering of segments via user input."""
        try:
            num_segments = len(segments)
            if "segment_order" not in st.session_state:
                st.session_state.segment_order = list(range(num_segments))

            def clear_order_input():
                try:
                    raw_input = st.session_state.order_input
                    if raw_input:
                        new_order = [int(x.strip()) - 1 for x in raw_input.split(",")]
                        if len(new_order) != num_segments:
                            st.error(f"Please provide exactly {num_segments} numbers.")
                            return
                        if any(i < 0 or i >= num_segments for i in new_order):
                            st.error(f"Invalid segment numbers. Use values between 1 and {num_segments}.")
                            return
                        if len(set(new_order)) != num_segments:
                            st.error("Duplicate segment numbers detected.")
                            return
                        st.session_state.segment_order = new_order
                        if 'saved_segments' in st.session_state and st.session_state.saved_segments:
                            reordered = [st.session_state.saved_segments[i] for i in new_order]
                            st.session_state.saved_segments = reordered
                        st.success("Segment order updated!")
                        st.session_state.order_input = ""
                except ValueError:
                    st.error("Please enter valid integers separated by commas.")
                except Exception as e:
                    logger.error(f"clear_order_input error: {str(e)}")
                    st.error("An unexpected error occurred while updating order.")
            
            st.text_input(
                "Rearrange Segments (Enter new order as comma-separated numbers, e.g., '2,1,3')",
                key="order_input",
                on_change=clear_order_input
            )

            segment_display = ""
            for i, segment in enumerate(st.session_state.saved_segments):
                if i < num_segments:
                    segment_display += (
                        f"{i + 1}: Song {segment['info']['song']} "
                        f"({segment['info']['start']:.1f}s - {segment['info']['end']:.1f}s)\n"
                    )
            st.text_area("Current Segment Order", segment_display, height=120, disabled=True)

            return st.session_state.segment_order
        except Exception as e:
            logger.error(f"Error in get_segment_order: {str(e)}")
            st.error("An error occurred while processing segment order.")
            return list(range(len(segments)))