import json
import re

from fastapi import HTTPException


def extract_json_list(text):
    try:
        # Extract the content inside the triple backticks using regex
        match = re.search(r"```json\s*(\[.*?\])\s*```", text, re.DOTALL)
        if not match:
            raise ValueError("No JSON block found in the text.")
        
        json_str = match.group(1).strip()
        json_list = json.loads(json_str)
        return json_list
    
    except (json.JSONDecodeError, ValueError) as e:
        raise HTTPException(status_code=500, detail=str(e))