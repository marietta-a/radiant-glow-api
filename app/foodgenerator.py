import json
import re
from fastapi import HTTPException
import os
from dotenv import load_dotenv
import requests

class FoodGenerator:
    def __init__(self):
        load_dotenv()
        self.model = os.getenv("MODEL")
        self.apiKey = os.getenv("OPEN_ROUTER_API_KEY")
        self.url = os.getenv("OPEN_ROUTER_URL")
        self.model_id = "HuggingFaceH4/zephyr-7b-beta"
        self.headers = {
                    'Authorization': f'Bearer {self.apiKey}',
                    'Content-Type': 'application/json'
                }
        
    def extract_json_list(self, text):
        try:
            # Extract the content inside the triple backticks using regex
            match = re.search(r"```json\s*(\[.*?\])\s*```", text, re.DOTALL)
            if not match:
                raise ValueError("No JSON block found in the text.")
            
            json_str = match.group(1).strip()
            json_list = json.loads(json_str)
            return json_list
        
        except (json.JSONDecodeError, ValueError) as e:
            print(f"An error occurred: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def search_food(self, query):
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": f"""generate a json formatted list of dish/food/cuisine that start with {query} using the template below for output:
                    [
                        {{
                            "name": 'Fufu',
                            "description": 'A staple food in many African countries, made from boiled and pounded starchy vegetables like cassava, yams, or plantains.',
                            "region": 'West Africa, Central Africa',
                            "type": 'Staple food'
                        }}
                    ]"""
                }
            ]
        }
        try:
            # Send the POST request to the DeepSeek API
            response = requests.post(self.url, json=data, headers=self.headers).json()
            raw_content = response["choices"][0]["message"]["content"]
            return self.extract_json_list(raw_content)
        except Exception as e:
            print(f"An error occurred: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        
    