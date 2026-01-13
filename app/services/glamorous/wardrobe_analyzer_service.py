
import os
import time
import cv2
import json
from fastapi import types
import torch
import re
import google.genai as genai
import numpy as np
from supabase import create_client, Client
from sam2.build_sam import build_sam2
from sam2.automatic_mask_generator import SAM2AutomaticMaskGenerator
from app.config import supabaseUrl, supabaseAnonKey, genAiKey, model, supabaseUserId, genAiClient, image_content_config

# --- CONFIGURATION ---
BUCKET_NAME = "glamorous"


supabase: Client = create_client(supabaseUrl, supabaseAnonKey)

# Initialize SAM 2
sam2_checkpoint = "sam2_hiera_large.pt"
model_cfg = "sam2_hiera_l.yaml"
sam2 = build_sam2(model_cfg, sam2_checkpoint, device="cuda" if torch.cuda.is_available() else "cpu")
mask_generator = SAM2AutomaticMaskGenerator(sam2)

def clean_json_response(text):
    """Cleans Gemini's markdown code blocks to return raw JSON."""
    clean = re.search(r'\{.*\}', text, re.DOTALL)
    return json.loads(clean.group()) if clean else None

def analyze_closet(image_bytes: bytes, mime_type: str):
    start = time.time()
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image is None:
        raise ValueError("Could not decode image bytes")
    
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    print("✂️ Segmenting Closet Items...")
    masks = mask_generator.generate(image_rgb)
    
    for i, mask in enumerate(masks):
        # Filter out background or tiny specs
        if mask['area'] < 12000: 
            continue
            
        # 1. CREATE TRANSPARENT FRAGMENT
        m = mask['segmentation']
        rgba_image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
        rgba_image[~m] = [0, 0, 0, 0] # Set background pixels to transparent
        
        x, y, w, h = [int(v) for v in mask['bbox']]
        crop = rgba_image[y:y+h, x:x+w]
        
        # Local save for processing
        filename = f"item_{supabaseUserId.uuid4().hex[:8]}.png"
        cv2.imwrite(filename, crop)

        # 2. UPLOAD TO 'glamorous' BUCKET
        # Organize storage by user ID
        storage_path = f"{supabaseUserId}/{filename}"
        
        with open(filename, "rb") as f:
            supabase.storage.from_(BUCKET_NAME).upload(
                path=storage_path, 
                file=f, 
                file_options={"content-type": "image/png"}
            )
        
        # Get the Public URL
        public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(storage_path)
        print(f"✅ Uploaded to Storage: {public_url}")

        # 3. RECOGNITION WITH GEMINI
        print(f"🤖 Identifying Item {i}...")
        prompt = """
        Analyze this clothing item and return a JSON object exactly matching these keys:
        {
          "name": "string",
          "category": "string",
          "sub_category": "string",
          "primary_color": "string",
          "secondary_colors": ["string"],
          "pattern": "string",
          "material_look": "string",
          "seasonality": ["string"],
          "formality": "string",
          "warmth_level": "string",
          "fits_with_colors": ["string"],
          "occasion_suitability": ["string"],
          "tags": ["string"],
          "description": "string"
        }
        Return ONLY valid JSON.
        """
        
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt),
                    # types.Part.from_bytes(
                    #     mime_type="image/jpeg",
                    #     data=open(image_path, "rb").read(),
                    # )
                    types.Part.from_bytes(
                        mime_type=mime_type,
                        data=image_bytes,
                    )
                ],
            ),
        ]
        
        response = genAiClient.models.generate_content(
            model=model,
            contents=contents,
            config=image_content_config,
        )
        
        # Parse the JSON response string into a Python dictionary
        item_data = clean_json_response(response.text)

        if item_data:
            # 4. INSERT INTO DATABASE (Mapping to your WardrobeItem model)
            db_payload = {
                "user_id": supabaseUserId,
                "name": item_data.get("name"),
                "category": item_data.get("category"),
                "sub_category": item_data.get("sub_category"),
                "primary_color": item_data.get("primary_color"),
                "secondary_colors": item_data.get("secondary_colors"),
                "pattern": item_data.get("pattern"),
                "material_look": item_data.get("material_look"),
                "seasonality": item_data.get("seasonality"),
                "formality": item_data.get("formality"),
                "warmth_level": item_data.get("warmth_level"),
                "fits_with_colors": item_data.get("fits_with_colors"),
                "occasion_suitability": item_data.get("occasion_suitability"),
                "tags": item_data.get("tags"),
                "image_url": public_url, # <--- The URL from your 'glamorous' bucket
                "description": item_data.get("description"),
                "is_favorite": False
            }
            
            supabase.table("wardrobe_items").insert(db_payload).execute()

            print(f"✨ Database record created for: {item_data.get('name')}")
            
            end = time.time()
            elapsed = end - start

            print(f"Elapsed time: {elapsed} seconds")

        # Clean up local temp file
        os.remove(filename)