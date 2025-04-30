import json
import re

from fastapi import HTTPException


def extract_json_list(text):
    """
    Extracts JSON data from text, handling both wrapped and unwrapped JSON.
    
    Args:
        text (str): Input text potentially containing JSON data
        
    Returns:
        list/dict: Parsed JSON data if found and valid
        None: If no valid JSON found
    """
    try:
        # First try to extract between ```json markers if they exist
        json_match = re.search(r'```json\n([\s\S]*?)\n```', text)
        if not json_match:
            # If no markers, try parsing the entire text as JSON
            text = text.strip()
            if (text.startswith('{') and text.endswith('}')) or (text.startswith('[') and text.endswith(']')):
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    pass
            
            # More aggressive search for JSON in text
            # Find potential JSON objects/arrays
            json_candidates = re.findall(r'\{[^{}]*\}|\[[^\[\]]*\]', text)
            
            for candidate in json_candidates:
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    continue
        
        json_str = json_match.group(1).strip()
        return json.loads(json_str)

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# def extract_json_list(text):
#     try:
#         # Extract the content inside the triple backticks using regex
#         match = re.search(r"```json\s*(\[.*?\])\s*```", text, re.DOTALL)
#         if not match:
#             raise ValueError("No JSON block found in the text.")
        
#         json_str = match.group(1).strip()
#         json_list = json.loads(json_str)
#         return json_list
    
#     except (json.JSONDecodeError, ValueError) as e:
#         return text