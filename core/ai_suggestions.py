import json
import re
import numpy as np
import librosa
from typing import Dict, List, Tuple
from config.settings import DEFAULT_AI_SUGGESTIONS, DEFAULT_VOLUME, DEFAULT_PITCH, DEFAULT_CROSSFADE, DEFAULT_EQ
from utils.openai_client import create_openai_client
from utils.logging import setup_logging
from utils.json_parser import robust_json_parser

logger = setup_logging()

class AISuggestions:
    def get_ai_suggestions(self, song1_features: Dict, song2_features: Dict, has_openai: bool = False) -> Dict:
        """Get AI suggestions for mashup parameters."""
        default_suggestions = {
            **DEFAULT_AI_SUGGESTIONS,
            'tempo': (song1_features['tempo'] + song2_features['tempo']) / 2,
            'key': song1_features['key']
        }

        if not has_openai:
            return default_suggestions

        try:
            client = create_openai_client()
            prompt = self._build_suggestions_prompt(song1_features, song2_features)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a music analysis AI that provides mashup parameters in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            ai_suggestions = json.loads(response.choices[0].message.content)
            valid_suggestions = default_suggestions.copy()
            for key in default_suggestions.keys():
                if key in ai_suggestions:
                    valid_suggestions[key] = ai_suggestions[key]
            if 'reasoning' in ai_suggestions:
                valid_suggestions['reasoning'] = ai_suggestions['reasoning']
            logger.info(f"AI suggestions generated: {valid_suggestions}")
            return valid_suggestions
        except Exception as e:
            logger.warning(f"Error getting AI suggestions: {str(e)}")
            return default_suggestions

    def _build_suggestions_prompt(self, song1_features: Dict, song2_features: Dict) -> str:
        """Build prompt for AI suggestions."""
        # Ensure all values are Python native types to avoid numpy formatting issues
        tempo1 = float(song1_features['tempo'])
        key1 = song1_features['key']
        duration1 = float(song1_features['duration'])
        rms1 = float(song1_features['avg_rms'])
        centroid1 = float(song1_features['spectral_centroid'])
        
        tempo2 = float(song2_features['tempo'])
        key2 = song2_features['key']
        duration2 = float(song2_features['duration'])
        rms2 = float(song2_features['avg_rms'])
        centroid2 = float(song2_features['spectral_centroid'])
        
        return f"""Given two songs with the following features:

        Song 1:
        - Tempo: {tempo1:.1f} BPM
        - Key: {key1}
        - Duration: {duration1:.1f} seconds
        - Energy (RMS): {rms1:.3f}
        - Brightness (Spectral Centroid): {centroid1:.3f}

        Song 2:
        - Tempo: {tempo2:.1f} BPM
        - Key: {key2}
        - Duration: {duration2:.1f} seconds
        - Energy (RMS): {rms2:.3f}
        - Brightness (Spectral Centroid): {centroid2:.3f}

        Analyze these audio features and suggest optimal parameters for creating a high-quality mashup.

        Consider the following factors:
        1. Tempo compatibility and the best target tempo
        2. Musical key compatibility and the best target key
        3. Energy level balance between songs
        4. Spectral characteristics and how they might blend
        5. Appropriate transition types and durations based on the songs' features
        6. Overall complexity level suitable for these particular songs
        7. Recommended mashup style that would work best

        Respond in JSON format with the following fields:
        - tempo: (number) The optimal tempo for the mashup in BPM
        - key: (string) The optimal key for the mashup
        - transition_type: (string) The recommended transition type (e.g., "Crossfade", "Cut", "Filter")
        - transition_duration: (number) Recommended transition duration in seconds
        - mood_match: (number) Compatibility score for mood (0-100)
        - energy_match: (number) Compatibility score for energy (0-100)
        - recommended_style: (string) Recommended mashup style
        - complexity: (string) Recommended complexity level ("Simple", "Medium", "Complex")
        - reasoning: (string) Brief explanation of your recommendations
        """

    def get_ai_mashup_segments(self, y1: np.ndarray, sr1: int, y2: np.ndarray, sr2: int,
                               features1: Dict, features2: Dict, prompt: str = None,
                               has_openai: bool = False, style: str = "Auto-Detect",
                               segment_length: str = "Auto-Detect") -> Tuple[List[Dict], bool]:
        """Create AI-generated mashup segments."""
        segments = []
        is_ai_generated = False
        logger.info(f"Starting AI mashup segment generation - OpenAI enabled: {has_openai}")
        try:
            # Convert all numpy values to Python native types
            tempo1, beats1 = librosa.beat.beat_track(y=y1, sr=sr1)
            tempo1 = float(tempo1)
            beats1 = [float(b) for b in beats1]
            
            tempo2, beats2 = librosa.beat.beat_track(y=y2, sr=sr2)
            tempo2 = float(tempo2)
            beats2 = [float(b) for b in beats2]
            
            rms1 = librosa.feature.rms(y=y1)[0]
            rms2 = librosa.feature.rms(y=y2)[0]
            
            # Convert rms arrays to native Python lists if needed
            if isinstance(rms1, np.ndarray):
                rms1 = rms1.tolist()
            if isinstance(rms2, np.ndarray):
                rms2 = rms2.tolist()
                
            high_energy_regions1, high_energy_regions2 = self._find_high_energy_regions(
                y1, sr1, y2, sr2, rms1, rms2
            )
            logger.info(f"Found high energy regions: {len(high_energy_regions1)} for song1, {len(high_energy_regions2)} for song2")

            # If not custom prompt, generate one based on style
            use_ai = has_openai
            if not prompt and style != "Custom":
                prompt = self._build_segment_prompt(style, segment_length, features1, features2)
                logger.info(f"Built segment prompt for style '{style}'")

            # Check if we can and should use OpenAI
            if use_ai and prompt:
                try:
                    client = create_openai_client()
                    if client is None:
                        logger.warning("OpenAI client is None, falling back to default segments")
                        return self.get_fallback_segments(y1, sr1, y2, sr2, features1, features2, segment_length), False
                        
                    system_prompt = self._build_system_prompt()
                    user_prompt = self._build_user_prompt(
                        tempo1, tempo2, features1, features2, high_energy_regions1,
                        high_energy_regions2, prompt, y1, sr1, y2, sr2
                    )
                    logger.info(f"Sending request to OpenAI")
                    
                    response = client.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.5
                    )
                    logger.info(f"Received response from OpenAI")

                    response_content = response.choices[0].message.content
                    
                    try:
                        logger.info("Attempting to parse OpenAI response as JSON")
                        ai_segments = json.loads(response_content)
                    except json.JSONDecodeError as e:
                        logger.warning(f"OpenAI response is not valid JSON ({str(e)}), trying robust parsing")
                        ai_segments = robust_json_parser(response_content)

                    if ai_segments is None:
                        logger.warning("Robust JSON parsing failed, falling back to default segments")
                        segments = self.get_fallback_segments(y1, sr1, y2, sr2, features1, features2, segment_length)
                    elif isinstance(ai_segments, dict) and "segments" in ai_segments:
                        logger.info(f"Found segments key in response with {len(ai_segments['segments'])} segments")
                        raw_segments = ai_segments["segments"]
                        is_ai_generated = True
                    elif isinstance(ai_segments, list):
                        logger.info(f"Response is a list with {len(ai_segments)} segments")
                        raw_segments = ai_segments
                        is_ai_generated = True
                    else:
                        logger.warning(f"Invalid AI response format: {type(ai_segments)}, falling back to default segments")
                        segments = self.get_fallback_segments(y1, sr1, y2, sr2, features1, features2, segment_length)

                    if is_ai_generated:
                        logger.info(f"Processing {len(raw_segments)} AI-generated segments")
                        segments = [{'info': segment_data} for segment_data in raw_segments]
                        segments = self._validate_segments(segments, y1, sr1, y2, sr2, high_energy_regions1, high_energy_regions2, segment_length)
                except Exception as e:
                    logger.error(f"Error parsing AI segments: {str(e)}", exc_info=True)
                    segments = self.get_fallback_segments(y1, sr1, y2, sr2, features1, features2, segment_length)
            else:
                if not has_openai:
                    logger.info("OpenAI not available, using fallback segments")
                elif not prompt:
                    logger.info("Could not generate a valid prompt for the selected style, using fallback segments")
                else:
                    logger.info("OpenAI request not attempted, using fallback segments")
                segments = self.get_fallback_segments(y1, sr1, y2, sr2, features1, features2, segment_length)

            logger.info(f"Created {len(segments)} segments (AI-generated: {is_ai_generated})")
            return segments, is_ai_generated
        except Exception as e:
            logger.error(f"Error creating AI mashup segments: {str(e)}", exc_info=True)
            return self.get_fallback_segments(y1, sr1, y2, sr2, features1, features2, segment_length), False

    def _find_high_energy_regions(self, y1: np.ndarray, sr1: int, y2: np.ndarray, sr2: int,
                                 rms1, rms2) -> Tuple[List[Tuple[float, float]], List[Tuple[float, float]]]:
        """Find high-energy regions in both songs."""
        high_energy_regions1 = []
        high_energy_regions2 = []

        # Convert to Python native types to avoid numpy formatting issues
        rms1_values = rms1 if isinstance(rms1, list) else rms1.tolist()
        rms2_values = rms2 if isinstance(rms2, list) else rms2.tolist()
        
        # Convert numpy mean/std to Python float
        try:
            # Use simpler method to convert to Python native types
            rms1_mean = float(np.mean(rms1_values))
            rms1_std = float(np.std(rms1_values))
            rms2_mean = float(np.mean(rms2_values))
            rms2_std = float(np.std(rms2_values))
        except (TypeError, ValueError) as e:
            # Fallback method
            rms1_mean = sum(rms1_values) / len(rms1_values) if rms1_values else 0.0
            rms1_std = 0.05  # Default value if calculation fails
            rms2_mean = sum(rms2_values) / len(rms2_values) if rms2_values else 0.0
            rms2_std = 0.05  # Default value if calculation fails
        
        # Calculate threshold
        threshold1 = float(rms1_mean + 0.5 * rms1_std)
        threshold2 = float(rms2_mean + 0.5 * rms2_std)
        
        # Find high energy frames using simple comparison
        try:
            # Convert to standard Python list of integers
            high_energy_frames1 = np.where(np.array(rms1_values) > threshold1)[0]
            high_energy_frames1 = [int(x) for x in high_energy_frames1.tolist()]
            
            high_energy_frames2 = np.where(np.array(rms2_values) > threshold2)[0]
            high_energy_frames2 = [int(x) for x in high_energy_frames2.tolist()]
        except Exception as e:
            # Fallback to manual comparison
            high_energy_frames1 = [i for i, val in enumerate(rms1_values) if val > threshold1]
            high_energy_frames2 = [i for i, val in enumerate(rms2_values) if val > threshold2]

        # Process song 1
        if len(high_energy_frames1) > 0:
            region_start = int(high_energy_frames1[0])
            for i in range(1, len(high_energy_frames1)):
                if high_energy_frames1[i] - high_energy_frames1[i-1] > 10:
                    region_end = int(high_energy_frames1[i-1])
                    if region_end - region_start > 100:
                        # Convert to seconds and ensure they're Python floats
                        start_time = float(librosa.frames_to_time(region_start, sr=sr1))
                        end_time = float(librosa.frames_to_time(region_end, sr=sr1))
                        if end_time - start_time > 5.0:
                            high_energy_regions1.append((float(start_time), float(end_time)))
                    region_start = int(high_energy_frames1[i])
            if len(high_energy_frames1) > 0:
                # Convert to seconds and ensure they're Python floats
                start_time = float(librosa.frames_to_time(region_start, sr=sr1))
                end_time = float(librosa.frames_to_time(int(high_energy_frames1[-1]), sr=sr1))
                if end_time - start_time > 1.0:
                    high_energy_regions1.append((float(start_time), float(end_time)))

        # Process song 2
        if len(high_energy_frames2) > 0:
            region_start = int(high_energy_frames2[0])
            for i in range(1, len(high_energy_frames2)):
                if high_energy_frames2[i] - high_energy_frames2[i-1] > 10:
                    region_end = int(high_energy_frames2[i-1])
                    if region_end - region_start > 100:
                        # Convert to seconds and ensure they're Python floats
                        start_time = float(librosa.frames_to_time(region_start, sr=sr2))
                        end_time = float(librosa.frames_to_time(region_end, sr=sr2))
                        if end_time - start_time > 5.0:
                            high_energy_regions2.append((float(start_time), float(end_time)))
                    region_start = int(high_energy_frames2[i])
            if len(high_energy_frames2) > 0:
                # Convert to seconds and ensure they're Python floats
                start_time = float(librosa.frames_to_time(region_start, sr=sr2))
                end_time = float(librosa.frames_to_time(int(high_energy_frames2[-1]), sr=sr2))
                if end_time - start_time > 1.0:
                    high_energy_regions2.append((float(start_time), float(end_time)))

        # Create default regions if none were found
        if not high_energy_regions1:
            duration1 = float(len(y1)/sr1)
            high_energy_regions1 = [(0.0, 30.0), (30.0, min(60.0, duration1)), (60.0, min(90.0, duration1))]
        if not high_energy_regions2:
            duration2 = float(len(y2)/sr2)
            high_energy_regions2 = [(0.0, 30.0), (30.0, min(60.0, duration2)), (60.0, min(90.0, duration2))]

        return high_energy_regions1, high_energy_regions2

    def _build_segment_prompt(self, style: str, segment_length: str, features1: Dict, features2: Dict) -> str:
        """Build prompt for segment generation based on style and segment length."""
        base_prompt = ""
        if style == "Auto-Detect":
            base_prompt = """Analyze these two songs and create a mashup based on their audio characteristics. 
            Create well-balanced segments that showcase the best parts of both songs.
            Focus on compatibility between segments and smooth transitions.
            Use high-energy sections for impactful transitions.
            Create a professional-sounding mashup with 4-6 segments total."""
        elif style == "Energetic":
            base_prompt = """Create an energetic, high-impact mashup with fast-paced transitions.
            Focus on the high-energy sections of both songs.
            Use shorter segments (30-40s each) with energetic transitions.
            Create dramatic transitions between songs at peak moments.
            Aim for a dance/club feel with built-up energy throughout.
            Total of 4-6 segments with emphasis on energy and tempo."""
        elif style == "Smooth":
            base_prompt = """Create a smooth, flowing mashup with gradual, seamless transitions.
            Focus on melodic sections and vocal parts that complement each other.
            Use medium length segments (30-40s each) with gentle crossfades.
            Match similar energy levels between segments for consistent flow.
            Create a relaxing, cohesive listening experience.
            Total of 4-5 segments with emphasis on continuity and harmony."""
        elif style == "Dramatic":
            base_prompt = """Create a dramatic, dynamic mashup with contrasting sections.
            Create tension and release with dramatic shifts between songs.
            Use varied segment lengths (30-45s) to build narrative suspense.
            Focus on creating moments of surprise and contrast.
            Balance loud/quiet and fast/slow sections for dynamic range.
            Total of 4-6 segments with emphasis on contrast and surprise."""
        elif style == "Playful":
            base_prompt = """Create a playful, creative mashup with unexpected combinations.
            Use creative transitions and unexpected juxtapositions.
            Mix contrasting elements in surprising ways.
            Include some shorter segments (30-40s) for quick changes.
            Focus on fun, experimental transitions between songs.
            Total of 5-7 segments with emphasis on creativity and surprise."""
        else:
            # Generic prompt for any other style
            base_prompt = f"""Create a {style} style mashup with specific transition characteristics:
            
            1. When transitioning FROM song 1 TO song 2:
               - End song 1 segments at LOW intensity/energy points
               - Begin song 2 segments at HIGH intensity/energy points
               - Use minimal crossfade (0.5 seconds or less) for sharp transitions
            
            2. When transitioning FROM song 2 TO song 1:
               - Follow a similar pattern but adjust as needed for musicality
               - Keep transitions brief and impactful
            
            3. General guidelines:
               - Create 4-6 segments total with a balanced mix from both songs
               - Segment length should be appropriate for the musical phrases
               - Focus on creating contrast between segments
               - Ensure the overall flow feels intentional and dynamic
            """

        if segment_length != "Auto-Detect":
            if segment_length == "Short (20-30s)":
                base_prompt += " Use mostly shorter segments of 20-30 seconds each."
            elif segment_length == "Medium (30-40s)":
                base_prompt += " Use mostly medium-length segments of 30-40 seconds each."
            elif segment_length == "Long (40-50s)":
                base_prompt += " Use mostly longer segments of 40-50 seconds each."
            elif segment_length == "Variable":
                base_prompt += " Use variable segment lengths for more dynamic interest."

        return base_prompt

    def _build_system_prompt(self) -> str:
        """Build system prompt for segment generation."""
        return """You are an expert music producer specializing in creating mashups. 
        Analyze the user's instructions and provide specific parameters for creating mashup segments
        and make sure the segments are compatible with each other and the songs can start or end at any point with the duration of the song.

        SPECIAL TRANSITION RULES:
        - When transitioning FROM song 1 TO song 2:
          * End song 1 segments at LOW intensity/energy points
          * Begin song 2 segments at HIGH intensity/energy points
          * Use minimal crossfade (0.3 seconds or less) for sharp transitions
        
        - Keep ALL crossfade durations short (under 0.5 seconds) for crisp transitions

        You MUST respond with VALID JSON FORMAT ONLY. Use a JSON object with a "segments" array containing segment objects with these parameters:
        - song: (number, 1 or 2) Which song this segment is from
        - start: (number) Start time in seconds
        - end: (number) End time in seconds
        - volume: (number, 0-1) Volume factor
        - pitch: (number, -12 to 12) Pitch shift in semitones
        - eq: (object) EQ settings with bass, mid, and treble values (-12 to 12)
        - crossfade: (number, 0-2) Crossfade duration in seconds

        CRITICAL: Use proper JSON syntax with double quotes for property names, not single quotes.
        Ensure all numbers are valid (no trailing commas, no undefined values).

        Example of VALID format:
        {
          "segments": [
            {
              "song": 1,
              "start": 30.5,
              "end": 60.2,
              "volume": 0.8,
              "pitch": 0,
              "eq": {"bass": 0, "mid": 0, "treble": 0},
              "crossfade": 0.3
            },
            {
              "song": 2,
              "start": 45.0,
              "end": 75.0,
              "volume": 0.8,
              "pitch": 0,
              "eq": {"bass": 0, "mid": 0, "treble": 0},
              "crossfade": 0.3
            }
          ]
        }

        Create 4-6 segment objects total, alternating between songs to create a cohesive mashup.
        """

    def _build_user_prompt(self, tempo1: float, tempo2: float, features1: Dict, features2: Dict,
                          high_energy_regions1: List[Tuple[float, float]], high_energy_regions2: List[Tuple[float, float]],
                          prompt: str, y1: np.ndarray, sr1: int, y2: np.ndarray, sr2: int) -> str:
        """Build user prompt for segment generation."""
        try:
            # Convert numpy values to Python native types
            tempo1 = float(tempo1)
            tempo2 = float(tempo2)
            duration1 = float(len(y1)/sr1)
            duration2 = float(len(y2)/sr2)
            
            # Convert RMS values to native Python types - safely
            try:
                rms_values1 = librosa.feature.rms(y=y1)[0]
                if isinstance(rms_values1, np.ndarray):
                    rms_values1 = rms_values1.tolist()
                
                rms_values2 = librosa.feature.rms(y=y2)[0]
                if isinstance(rms_values2, np.ndarray):
                    rms_values2 = rms_values2.tolist()
                
                # Calculate means using simple Python method if numpy conversion fails
                try:
                    rms1 = float(np.mean(rms_values1))
                    rms2 = float(np.mean(rms_values2))
                except (TypeError, ValueError):
                    # Fallback to manual calculation
                    rms1 = sum(rms_values1) / len(rms_values1) if rms_values1 else 0.05
                    rms2 = sum(rms_values2) / len(rms_values2) if rms_values2 else 0.05
            except Exception as e:
                logger.warning(f"Error calculating RMS values: {e}, using default values")
                rms1 = 0.05  # Default fallback value
                rms2 = 0.05  # Default fallback value
            
            # Explicitly convert all high energy region values to Python floats
            python_regions1 = [(float(start), float(end)) for start, end in high_energy_regions1]
            python_regions2 = [(float(start), float(end)) for start, end in high_energy_regions2]
            
            # Format high energy regions with explicit float conversion
            try:
                regions1_str = ', '.join([f'{float(start):.1f}s-{float(end):.1f}s' for start, end in python_regions1[:3]])
                regions2_str = ', '.join([f'{float(start):.1f}s-{float(end):.1f}s' for start, end in python_regions2[:3]])
            except Exception as e:
                logger.warning(f"Error formatting region strings: {e}, using generic format")
                regions1_str = "multiple regions" if python_regions1 else "no high-energy regions found"
                regions2_str = "multiple regions" if python_regions2 else "no high-energy regions found"
            
            # Make sure the key values are strings
            key1 = str(features1.get('key', 'Unknown'))
            key2 = str(features2.get('key', 'Unknown'))
            
            # Ensure all values are standard Python types before f-string formatting
            tempo1_str = f"{float(tempo1):.1f}"
            tempo2_str = f"{float(tempo2):.1f}"
            duration1_str = f"{float(duration1):.1f}"
            duration2_str = f"{float(duration2):.1f}"
            rms1_str = f"{float(rms1):.3f}"
            rms2_str = f"{float(rms2):.3f}"
            
            return f"""Song 1 features:
            - Tempo: {tempo1_str} BPM
            - Key: {key1}
            - Duration: {duration1_str} seconds
            - Average RMS energy: {rms1_str}
    
            Song 2 features:
            - Tempo: {tempo2_str} BPM
            - Key: {key2}
            - Duration: {duration2_str} seconds
            - Average RMS energy: {rms2_str}
    
            I've identified high-energy regions in both songs:
            Song 1: {regions1_str}
            Song 2: {regions2_str}
    
            User instructions: {prompt}
    
            Please provide segment parameters that best match these instructions in JSON format.
            """
        except Exception as e:
            logger.error(f"Error building user prompt: {e}, using simplified prompt")
            # Fallback to a minimal prompt if all else fails
            return f"""Create a mashup with two songs.
            Song 1 duration: around {len(y1)/sr1:.0f} seconds
            Song 2 duration: around {len(y2)/sr2:.0f} seconds
            
            User instructions: {prompt}
            
            Please provide segment parameters for a balanced mashup in JSON format.
            """

    def _validate_segments(self, segments: List[Dict], y1: np.ndarray, sr1: int, y2: np.ndarray, sr2: int,
                           high_energy_regions1: List[Tuple[float, float]], high_energy_regions2: List[Tuple[float, float]],
                           segment_length: str) -> List[Dict]:
        """Validate and correct segment parameters."""
        validated_segments = []
        
        # Convert durations to native Python floats
        duration1 = float(len(y1)/sr1)
        duration2 = float(len(y2)/sr2)
        
        for i, segment in enumerate(segments):
            info = segment.get('info', {})
            if 'song' not in info or info['song'] not in [1, 2]:
                info['song'] = (i % 2) + 1

            # Get the correct duration based on song number
            duration = duration1 if info['song'] == 1 else duration2
            high_energy_regions = high_energy_regions1 if info['song'] == 1 else high_energy_regions2

            # Handle start time
            if 'start' not in info or not isinstance(info['start'], (int, float)) or info['start'] < 0 or info['start'] >= duration:
                if high_energy_regions and len(high_energy_regions) > 0:
                    region_idx = i % len(high_energy_regions)
                    info['start'] = float(high_energy_regions[region_idx][0])
                else:
                    info['start'] = float(min(30 * (i % 3), duration - 30))

            # Handle end time
            if 'end' not in info or not isinstance(info['end'], (int, float)) or info['end'] <= info['start'] or info['end'] > duration:
                segment_len = {
                    "Short (20-30s)": 30.0,
                    "Medium (30-40s)": 40.0,
                    "Long (40-50s)": 50.0
                }.get(segment_length, 35.0)
                info['end'] = float(min(info['start'] + segment_len, duration))

            # Ensure all other parameters are valid and convert to native Python types
            if 'volume' not in info or not isinstance(info['volume'], (int, float)) or not (0 <= info['volume'] <= 1):
                info['volume'] = float(DEFAULT_VOLUME)
            else:
                info['volume'] = float(info['volume'])

            if 'pitch' not in info or not isinstance(info['pitch'], (int, float)) or not (-12 <= info['pitch'] <= 12):
                info['pitch'] = float(DEFAULT_PITCH)
            else:
                info['pitch'] = float(info['pitch'])

            # Handle EQ settings
            if 'eq' not in info or not isinstance(info['eq'], dict):
                info['eq'] = DEFAULT_EQ.copy()
            else:
                eq_copy = {}
                for eq_param in ['bass', 'mid', 'treble']:
                    if eq_param not in info['eq'] or not isinstance(info['eq'][eq_param], (int, float)) or not (-12 <= info['eq'][eq_param] <= 12):
                        eq_copy[eq_param] = 0.0
                    else:
                        eq_copy[eq_param] = float(info['eq'][eq_param])
                info['eq'] = eq_copy

            if 'crossfade' not in info or not isinstance(info['crossfade'], (int, float)) or not (0 <= info['crossfade'] <= 2):
                info['crossfade'] = float(DEFAULT_CROSSFADE)
            else:
                info['crossfade'] = float(info['crossfade'])

            validated_segments.append({'info': info})

        return validated_segments

    def get_fallback_segments(self, y1: np.ndarray, sr1: int, y2: np.ndarray, sr2: int,
                             features1: Dict, features2: Dict, segment_length: str = "Medium (30-40s)") -> List[Dict]:
        """Create fallback segments if AI generation fails."""
        try:
            duration1 = float(len(y1)/sr1)
            duration2 = float(len(y2)/sr2)
            
            # Safely handle RMS values as Python native types
            rms_values1 = librosa.feature.rms(y=y1)[0]
            rms_values2 = librosa.feature.rms(y=y2)[0]
            
            # Convert to Python lists if they're numpy arrays
            rms1 = rms_values1.tolist() if isinstance(rms_values1, np.ndarray) else rms_values1
            rms2 = rms_values2.tolist() if isinstance(rms_values2, np.ndarray) else rms_values2
            
            high_energy_regions1, high_energy_regions2 = self._find_high_energy_regions(y1, sr1, y2, sr2, rms1, rms2)

            segment_duration = {
                "Short (20-30s)": 30.0,
                "Medium (30-40s)": 40.0,
                "Long (40-50s)": 45.0
            }.get(segment_length, 35.0)

            segments = []
            for regions, song_id, duration, sr, rms_values in [
                (high_energy_regions1, 1, duration1, sr1, rms1),
                (high_energy_regions2, 2, duration2, sr2, rms2)
            ]:
                sorted_regions = []
                for start, end in regions:
                    # Convert times to frames safely - ensure all values are Python native types
                    # Convert times to Python floats first
                    start_float = float(start)
                    end_float = float(end)
                    
                    # Then convert to frames
                    start_frame = int(librosa.time_to_frames(start_float, sr=sr))
                    end_frame = int(librosa.time_to_frames(end_float, sr=sr))
                    
                    # Ensure frames are within bounds
                    start_frame = max(0, min(start_frame, len(rms_values)-1))
                    end_frame = max(start_frame+1, min(end_frame, len(rms_values)))
                    
                    # Calculate average energy safely with Python native types
                    if start_frame < end_frame:
                        slice_to_use = rms_values[start_frame:end_frame]
                        if len(slice_to_use) > 0:
                            # Convert to Python float explicitly
                            avg_energy = float(np.mean(slice_to_use).item() if hasattr(np.mean(slice_to_use), 'item') else np.mean(slice_to_use))
                        else:
                            avg_energy = 0.0
                    else:
                        avg_energy = 0.0
                        
                    sorted_regions.append((float(start), float(end), float(avg_energy)))
                
                # Sort by energy level (descending)
                sorted_regions.sort(key=lambda x: x[2], reverse=True)

                for i, (start, end, _) in enumerate(sorted_regions[:3]):
                    # Calculate segment times ensuring they're Python float values
                    start = float(start)
                    end = float(end)
                    
                    if end - start < segment_duration:
                        extension_needed = segment_duration - (end - start)
                        start = max(0.0, start - extension_needed/2)
                        end = min(float(duration), end + extension_needed/2)
                    if end - start < 20.0:
                        continue
                    if end - start > segment_duration:
                        middle = (start + end) / 2
                        start = middle - segment_duration/2
                        end = middle + segment_duration/2
                    start = max(0.0, start)
                    end = min(float(duration), end)
                    
                    segments.append({
                        'info': {
                            'song': song_id,
                            'start': start,
                            'end': end,
                            'volume': DEFAULT_VOLUME,
                            'pitch': DEFAULT_PITCH,
                            'eq': DEFAULT_EQ.copy(),  # Use copy to avoid reference issues
                            'crossfade': DEFAULT_CROSSFADE
                        }
                    })

            # Add more segments if needed
            if len(segments) < 4:
                for song_id, duration in [(1, duration1), (2, duration2)]:
                    num_to_add = 2 - len([s for s in segments if s['info']['song'] == song_id])
                    for i in range(num_to_add):
                        start = float(i * (duration / (num_to_add + 1)))
                        end = min(start + segment_duration, float(duration))
                        if end - start >= 20.0:
                            segments.append({
                                'info': {
                                    'song': song_id,
                                    'start': start,
                                    'end': end,
                                    'volume': DEFAULT_VOLUME,
                                    'pitch': DEFAULT_PITCH,
                                    'eq': DEFAULT_EQ.copy(),
                                    'crossfade': DEFAULT_CROSSFADE
                                }
                            })

            # Interleave segments from both songs
            song1_segments = [s for s in segments if s['info']['song'] == 1]
            song2_segments = [s for s in segments if s['info']['song'] == 2]
            interleaved_segments = []
            for i in range(max(len(song1_segments), len(song2_segments))):
                if i < len(song1_segments):
                    interleaved_segments.append(song1_segments[i])
                if i < len(song2_segments):
                    interleaved_segments.append(song2_segments[i])

            return interleaved_segments[:6]  # Limit to 6 segments max
            
        except Exception as e:
            logger.error(f"Error creating fallback segments: {str(e)}")
            # Create very basic segments if everything else fails
            duration1 = float(len(y1)/sr1)
            duration2 = float(len(y2)/sr2)
            segment_len = 30.0
            return [
                {
                    'info': {
                        'song': 1,
                        'start': 0.0,
                        'end': min(segment_len, duration1),
                        'volume': DEFAULT_VOLUME,
                        'pitch': DEFAULT_PITCH,
                        'eq': DEFAULT_EQ.copy(),
                        'crossfade': DEFAULT_CROSSFADE
                    }
                },
                {
                    'info': {
                        'song': 2,
                        'start': 0.0,
                        'end': min(segment_len, duration2),
                        'volume': DEFAULT_VOLUME,
                        'pitch': DEFAULT_PITCH,
                        'eq': DEFAULT_EQ.copy(),
                        'crossfade': DEFAULT_CROSSFADE
                    }
                }
            ]