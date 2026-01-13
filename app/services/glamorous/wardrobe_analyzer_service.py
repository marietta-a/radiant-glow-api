
import os
import cv2
import json
import torch
import re
import google.genai as genai
from supabase import create_client, Client
from sam2.build_sam import build_sam2
from sam2.automatic_mask_generator import SAM2AutomaticMaskGenerator

# --- CONFIGURATION ---
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-service-role-key" # Use service role for backend inserts
GEMINI_KEY = "your-gemini-key"
USER_ID = "00000000-0000-0000-0000-000000000000" # Pass the actual user's UUID

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GEMINI_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize SAM 2
sam2_checkpoint = "sam2_hiera_large.pt"
model_cfg = "sam2_hiera_l.yaml"
sam2 = build_sam2(model_cfg, sam2_checkpoint, device="cuda" if torch.cuda.is_available() else "cpu")
mask_generator = SAM2AutomaticMaskGenerator(sam2)

def clean_gemini_json(text):
    """Extracts JSON from Gemini's markdown response."""
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())
    return None

def process_closet(image_path):
    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    print("Segmenting image...")
    masks = mask_generator.generate(image_rgb)
    
    for i, mask in enumerate(masks):
        if mask['area'] < 15000: # Filter small objects
            continue
            
        # 1. Fragment & Save locally
        m = mask['segmentation']
        rgba_image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
        rgba_image[~m] = [0, 0, 0, 0] 
        x, y, w, h = [int(v) for v in mask['bbox']]
        crop = rgba_image[y:y+h, x:x+w]
        
        temp_filename = f"item_{i}.png"
        cv2.imwrite(temp_filename, crop)

        # 2. Upload to Storage
        storage_path = f"{USER_ID}/item_{i}_{os.path.basename(image_path)}"
        with open(temp_filename, "rb") as f:
            supabase.storage.from_("closet-items").upload(storage_path, f)
        
        public_url = supabase.storage.from_("closet-items").get_public_url(storage_path)

        # 3. Prompt Gemini for the WardrobeItem Model
        print(f"Generating data for item {i}...")
        sample_file = genai.upload_file(path=temp_filename)
        
        prompt = f"""
        Analyze this clothing item and return a JSON object that strictly follows this structure:
        {{
          "name": "Specific name of item",
          "category": "Broad category (e.g., Tops, Bottoms, Outerwear, Shoes)",
          "sub_category": "Specific type (e.g., Denim Jacket, Hoodie, Chinos)",
          "primary_color": "Main color",
          "secondary_colors": ["color1", "color2"],
          "pattern": "e.g., Solid, Striped, Floral",
          "material_look": "e.g., Silk, Denim, Leather, Wool",
          "seasonality": ["Spring", "Autumn"],
          "formality": "e.g., Casual, Formal, Business",
          "warmth_level": "e.g., High, Medium, Low",
          "fits_with_colors": ["color1", "color2"],
          "occasion_suitability": ["Work", "Gym", "Party"],
          "tags": ["vintage", "slim-fit", "waterproof"],
          "description": "A brief description for the user"
        }}
        Return ONLY the JSON.
        """
        
        response = gemini_model.generate_content([sample_file, prompt])
        item_data = clean_gemini_json(response.text)

        if item_data:
            # 4. Map to Database (Matches your factory WardrobeItem.fromJson)
            db_payload = {
                "user_id": USER_ID,
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
                "image_url": public_url,
                "description": item_data.get("description"),
                "is_favorite": False
            }
            
            # Insert into Supabase
            supabase.table("wardrobe_items").insert(db_payload).execute()
            print(f"Saved: {item_data.get('name')}")
        
        os.remove(temp_filename)