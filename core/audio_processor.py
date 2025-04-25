import librosa
import numpy as np
from typing import Dict, List
from config.settings import OUTPUT_DIR, TEMP_DIR, DEFAULT_EQ
from datetime import datetime
import os
import shutil
import soundfile as sf
from pydub import AudioSegment
import tempfile
from utils.logging import setup_logging

logger = setup_logging()

class AudioProcessor:
    def __init__(self):
        # Initialize basic components directly in this class
        # instead of using external mashup_engine modules
        self.separator = SeparatorStub()
        self.analyzer = AnalyzerStub()
        self.aligner = AlignerStub()
        self.mixer = self  # Use self as mixer since we'll implement those methods here
        self.namer = NamerStub()

    def analyze_song(self, file_path: str) -> Dict:
        """Analyze a song's features."""
        try:
            y, sr = librosa.load(file_path)
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
            key_idx = np.argmax(np.mean(chroma, axis=1))
            keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            key = keys[int(key_idx)]
            rms = librosa.feature.rms(y=y)
            avg_rms = float(np.mean(rms))
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
            avg_spectral_centroid = float(np.mean(spectral_centroid))
            
            # Return a dictionary with native Python types
            return {
                'y': y,
                'sr': int(sr),
                'tempo': float(tempo),
                'key': key,
                'duration': float(librosa.get_duration(y=y, sr=sr)),
                'avg_rms': float(avg_rms),
                'spectral_centroid': float(avg_spectral_centroid)
            }
        except Exception as e:
            logger.error(f"Error analyzing song: {str(e)}")
            raise

    def process_segment(self, source_path: str, start_time: float, end_time: float,
                       target_tempo: float = None, target_key: str = None,
                       volume: float = 0.8, pitch: float = 0.0,
                       eq: Dict = None, crossfade: float = 0.5,
                       output_path: str = None, preview: bool = False) -> str:
        """Process an audio segment with various effects."""
        try:
            # Default EQ settings if not provided
            if eq is None:
                eq = DEFAULT_EQ
                
            # Load the audio file
            logger.info(f"Processing segment from {source_path}, {start_time:.1f}s to {end_time:.1f}s")
            audio = AudioSegment.from_file(source_path)
            
            # Convert time to milliseconds
            start_ms = int(start_time * 1000)
            end_ms = int(end_time * 1000)
            
            # Extract segment
            segment = audio[start_ms:end_ms]
            
            # Apply volume adjustment
            segment = segment.apply_gain(10 * np.log10(volume))  # Convert to dB
            
            # Apply pitch shifting
            if pitch != 0:
                # Export to temporary file
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                    temp_path = temp_file.name
                
                segment.export(temp_path, format="wav")
                
                # Load with librosa
                y, sr = librosa.load(temp_path)
                
                # Apply pitch shifting
                y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=pitch)
                
                # Save back to temporary file
                sf.write(temp_path, y_shifted, sr)
                
                # Load back as AudioSegment
                segment = AudioSegment.from_file(temp_path)
                
                # Clean up
                os.remove(temp_path)
            
            # Apply EQ adjustments
            if any(eq.values()):
                segment = self.apply_eq(segment, eq)
            
            # Apply crossfade
            segment = self._apply_fade(segment, crossfade_ms=crossfade * 1000)
            
            # If no output path specified, create a temporary one
            if output_path is None:
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                    output_path = temp_file.name
            
            # Export the processed segment
            export_format = "wav"
            if preview:
                # Use lower quality for previews
                segment.export(output_path, format=export_format, parameters=["-ac", "2", "-ar", "44100"])
            else:
                # Use higher quality for final output
                segment.export(output_path, format=export_format)
            
            logger.info(f"Processed segment saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error processing segment: {str(e)}")
            raise

    def combine_segments(self, segment_paths: List[str], output_path: str) -> str:
        """Combine multiple audio segments with crossfades."""
        try:
            if not segment_paths:
                raise ValueError("No segment paths provided")
                
            # Load all segments
            segments = [AudioSegment.from_file(path) for path in segment_paths]
            
            # Combine segments
            combined = segments[0]
            for segment in segments[1:]:
                # Apply crossfade between segments
                crossfade_duration = min(1000, len(combined) // 2, len(segment) // 2)  # 1 second or less
                combined = combined.append(segment, crossfade=crossfade_duration)
            
            # Export the combined audio
            export_format = "mp3" if output_path.endswith(".mp3") else "wav"
            combined.export(output_path, format=export_format)
            
            logger.info(f"Combined {len(segments)} segments into {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error combining segments: {str(e)}")
            raise

    def create_final_mashup(self, song1_path: str, song2_path: str, target_tempo: float,
                           target_key: str, segments: List[Dict], song1_volume: float = 0.5,
                           song2_volume: float = 0.5, song1_pitch: float = 0.0,
                           song2_pitch: float = 0.0, song1_eq: Dict = None,
                           song2_eq: Dict = None) -> Dict:
        """Create the final mashup."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            mashup_path = OUTPUT_DIR / f"final_mashup_{timestamp}.wav"
            temp_dir = TEMP_DIR / f"final_mashup_{timestamp}"
            temp_dir.mkdir(parents=True, exist_ok=True)

            processed_segments = []
            for i, segment in enumerate(segments):
                song_number = int(segment.get('song', 1))
                source_path = song1_path if song_number == 1 else song2_path
                base_volume = song1_volume if song_number == 1 else song2_volume
                base_pitch = song1_pitch if song_number == 1 else song2_pitch
                base_eq = song1_eq if song_number == 1 else song2_eq

                volume = segment.get('volume', base_volume)
                pitch = base_pitch + segment.get('pitch', 0.0)
                eq = self._combine_eq(base_eq, segment.get('eq'))
                segment_output = str(temp_dir / f"segment_{i}.wav")

                processed_segment = self.process_segment(
                    source_path, segment['start'], segment['end'],
                    target_tempo, target_key, volume, pitch, eq,
                    segment.get('crossfade', 0.5), segment_output
                )
                if processed_segment and os.path.exists(processed_segment):
                    processed_segments.append(processed_segment)
                else:
                    logger.warning(f"Failed to process segment {i} - skipping it")

            if not processed_segments:
                raise ValueError("No segments were successfully processed")

            final_mashup_path = str(mashup_path)
            self.combine_segments(processed_segments, final_mashup_path)

            song1_name = os.path.splitext(os.path.basename(song1_path))[0]
            song2_name = os.path.splitext(os.path.basename(song2_path))[0]
            mashup_name = f"{song1_name}_x_{song2_name}_mashup"

            for segment_path in processed_segments:
                if os.path.exists(segment_path):
                    os.remove(segment_path)
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

            return {'mashup_path': final_mashup_path, 'mashup_name': mashup_name}
        except Exception as e:
            logger.error(f"Error creating final mashup: {str(e)}")
            raise

    def _combine_eq(self, base_eq: Dict, segment_eq: Dict) -> Dict:
        """Combine base and segment EQ settings."""
        if base_eq and segment_eq:
            return {
                'bass': base_eq.get('bass', 0) + segment_eq.get('bass', 0),
                'mid': base_eq.get('mid', 0) + segment_eq.get('mid', 0),
                'treble': base_eq.get('treble', 0) + segment_eq.get('treble', 0)
            }
        return segment_eq or base_eq or DEFAULT_EQ
        
    def apply_eq(self, audio_data: AudioSegment, eq_settings: Dict) -> AudioSegment:
        """Apply EQ adjustments to audio."""
        try:
            # Check if any EQ adjustment is needed
            if all(eq_settings.get(band, 0) == 0 for band in ['bass', 'mid', 'treble']):
                return audio_data  # No adjustments needed
                
            # Define frequency bands
            bass_band = (60, 250)
            mid_band = (500, 2000)
            treble_band = (4000, 16000)
            
            # Create a copy of the original audio
            result = audio_data
            
            # Apply bass adjustment (low frequencies)
            if eq_settings.get('bass', 0) != 0:
                bass_adjustment = float(eq_settings.get('bass', 0))
                # Only adjust the low frequencies using low_pass_filter
                bass_audio = audio_data.low_pass_filter(bass_band[1])
                # Apply the gain adjustment
                if bass_adjustment != 0:
                    result = result.apply_gain(bass_adjustment * 0.5)
            
            # Apply treble adjustment (high frequencies)
            if eq_settings.get('treble', 0) != 0:
                treble_adjustment = float(eq_settings.get('treble', 0))
                # Only adjust the high frequencies using high_pass_filter
                treble_audio = audio_data.high_pass_filter(treble_band[0])
                # Apply the gain adjustment
                if treble_adjustment != 0:
                    result = result.apply_gain(treble_adjustment * 0.5)
            
            # Apply mid adjustment (we can't directly target mid frequencies without band_pass_filter)
            # Instead we'll just apply a general gain adjustment to the overall audio
            if eq_settings.get('mid', 0) != 0:
                mid_adjustment = float(eq_settings.get('mid', 0))
                # Apply a gentle gain adjustment to the overall audio
                if mid_adjustment != 0:
                    result = result.apply_gain(mid_adjustment * 0.3)
                
            return result
            
        except Exception as e:
            logger.error(f"Error applying EQ: {str(e)}")
            return audio_data  # Return original if error
            
    def _apply_fade(self, segment: AudioSegment, crossfade_ms: float = 500) -> AudioSegment:
        """Apply fade in/out to a segment."""
        # Ensure crossfade_ms is not too long
        max_fade = min(crossfade_ms, len(segment) // 2)
        return segment.fade_in(int(max_fade)).fade_out(int(max_fade))


# Stub classes to replace the external dependencies
class SeparatorStub:
    def __init__(self, output_dir=None):
        self.output_dir = output_dir

class AnalyzerStub:
    def __init__(self):
        pass
        
    def analyze_audio_features(self, audio_path, has_openai=False):
        # Delegate to the audio processor's analyze_song
        y, sr = librosa.load(audio_path)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        key_idx = np.argmax(np.mean(chroma, axis=1))
        keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        key = keys[key_idx]
        rms = librosa.feature.rms(y=y)
        avg_rms = float(np.mean(rms))
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
        avg_spectral_centroid = float(np.mean(spectral_centroid))
        return {
            'tempo': tempo,
            'key': key,
            'duration': librosa.get_duration(y=y, sr=sr),
            'avg_rms': avg_rms,
            'spectral_centroid': avg_spectral_centroid
        }

class AlignerStub:
    def __init__(self):
        pass

class NamerStub:
    def __init__(self):
        pass