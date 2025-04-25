import json
import re
from utils.logging import setup_logging

logger = setup_logging()

def robust_json_parser(json_text):
    """
    A robust JSON parser that attempts to fix common JSON formatting issues
    that might occur in AI responses.
    
    Args:
        json_text (str): The potentially malformed JSON string
        
    Returns:
        dict or list: The parsed JSON object, or None if parsing fails completely
    """
    # First try direct parsing
    try:
        return json.loads(json_text)
    except json.JSONDecodeError as e:
        logger.warning(f"Initial JSON parsing failed: {str(e)}")
    
    # If that fails, try to clean up common issues
    try:
        # Replace single quotes with double quotes (common AI mistake)
        cleaned_text = json_text.replace("'", '"')
        
        # Fix missing/extra commas in lists and objects
        # 1. Remove trailing commas before closing brackets
        cleaned_text = re.sub(r',\s*}', '}', cleaned_text)
        cleaned_text = re.sub(r',\s*\]', ']', cleaned_text)
        
        # 2. Add missing commas between elements
        cleaned_text = re.sub(r'}\s*{', '},{', cleaned_text)
        cleaned_text = re.sub(r'"\s*{', '",{', cleaned_text)
        cleaned_text = re.sub(r'}\s*"', '},"', cleaned_text)
        cleaned_text = re.sub(r']\s*{', '],{', cleaned_text)
        cleaned_text = re.sub(r'}\s*\[', '},[', cleaned_text)
        
        # Fix property names that aren't in quotes
        pattern = r'([{,])\s*([a-zA-Z0-9_]+)\s*:'
        cleaned_text = re.sub(pattern, r'\1"\2":', cleaned_text)
        
        # Try parsing the cleaned text
        return json.loads(cleaned_text)
    except (json.JSONDecodeError, Exception) as e:
        logger.warning(f"Cleaned JSON parsing failed: {str(e)}")
    
    # If cleaning failed, try a more aggressive approach: extracting just the array portion
    try:
        # Look for array pattern [...]
        array_match = re.search(r'\[(.*)\]', json_text, re.DOTALL)
        if array_match:
            array_text = "[" + array_match.group(1) + "]"
            # Apply the same cleaning to the extracted array
            array_text = array_text.replace("'", '"')
            array_text = re.sub(r',\s*}', '}', array_text)
            array_text = re.sub(r',\s*\]', ']', array_text)
            array_text = re.sub(r'}\s*{', '},{', array_text)
            pattern = r'([{,])\s*([a-zA-Z0-9_]+)\s*:'
            array_text = re.sub(pattern, r'\1"\2":', array_text)
            
            return json.loads(array_text)
    except (json.JSONDecodeError, Exception) as e:
        logger.warning(f"Array extraction parsing failed: {str(e)}")
    
    # As a last resort, try to construct a new array by parsing individual objects
    try:
        # Find all JSON-like objects using regex
        object_pattern = r'{[^{}]*}'
        objects = re.findall(object_pattern, json_text)
        
        if objects:
            # Try to clean and parse each object
            valid_objects = []
            for obj_text in objects:
                try:
                    # Clean the object text
                    obj_text = obj_text.replace("'", '"')
                    pattern = r'([{,])\s*([a-zA-Z0-9_]+)\s*:'
                    obj_text = re.sub(pattern, r'\1"\2":', obj_text)
                    obj = json.loads(obj_text)
                    valid_objects.append(obj)
                except:
                    continue
            
            if valid_objects:
                return valid_objects
    except Exception as e:
        logger.warning(f"Object extraction parsing failed: {str(e)}")
    
    # If all else fails, return None
    logger.error("All JSON parsing attempts failed")
    return None