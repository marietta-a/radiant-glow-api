import re
import torch
from fastapi import HTTPException
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from datasets import Dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

class FoodGenerator:
    def __init__(self):
        self.model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    #     self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)

    #     # Example empty dataset (must be filled later)
    #     self.data_set = {
    #         "prompt": [" Italian weight management diets",],
    #         "response": [
    #             {
    #                 "category": "Italian Low-Calorie Lunch Options (Weight Management)",
    #                 "description": "Traditional Italian lunch dishes modified for calorie control while maintaining authentic flavors.",
    #                 "items": [
    #                 {
    #                     "label": "Zucchini Noodle Primavera",
    #                     "emoji": "🥒🇮🇹🍝",
    #                     "nutrient_proportion": {
    #                     "protein": "0.25",
    #                     "carbohydrates": "0.50",
    #                     "fat": "0.25"
    #                     },
    #                     "calories_aggregate": "280 / serving",
    #                     "health_benefit": [
    #                     "Low-carb alternative to pasta, reducing calorie intake",
    #                     "Rich in vitamins A and C from fresh vegetables",
    #                     "Contains healthy fats from olive oil and pine nuts",
    #                     "High water content promotes hydration and satiety"
    #                     ],
    #                     "health_risk": [
    #                     "Potential allergic reaction (tree nuts)",
    #                     "May cause digestive discomfort if eaten raw in large quantities"
    #                     ],
    #                     "ingredient": [
    #                     {
    #                         "name": "Zucchini (spiralized)",
    #                         "quantity": "2 medium",
    #                         "emoji": "🥒"
    #                     },
    #                     {
    #                         "name": "Cherry tomatoes",
    #                         "quantity": "1/2 cup",
    #                         "emoji": "🍅"
    #                     },
    #                     {
    #                         "name": "Fresh basil",
    #                         "quantity": "1/4 cup",
    #                         "emoji": "🌿"
    #                     },
    #                     {
    #                         "name": "Pine nuts",
    #                         "quantity": "1 tbsp",
    #                         "emoji": "🌰"
    #                     },
    #                     {
    #                         "name": "Extra virgin olive oil",
    #                         "quantity": "1 tbsp",
    #                         "emoji": "🫒"
    #                     }
    #                     ],
    #                     "recipe": [
    #                     "Spiralize zucchini into noodle shapes",
    #                     "Quickly blanch in boiling water for 1 minute",
    #                     "Toss with halved cherry tomatoes, torn basil leaves",
    #                     "Toast pine nuts lightly in a dry pan",
    #                     "Drizzle with olive oil and season with salt and pepper"
    #                     ],
    #                     "risk_color": "green"
    #                 },
    #                 {
    #                     "label": "Grilled Eggplant Caprese Stack",
    #                     "emoji": "🍆🇮🇹🧀",
    #                     "nutrient_proportion": {
    #                     "protein": "0.30",
    #                     "carbohydrates": "0.30",
    #                     "fat": "0.40"
    #                     },
    #                     "calories_aggregate": "320 / serving (2 stacks)",
    #                     "health_benefit": [
    #                     "High in antioxidants from eggplant and tomatoes",
    #                     "Good source of calcium from fresh mozzarella",
    #                     "Healthy fats from olive oil aid nutrient absorption",
    #                     "Low glycemic index helps maintain stable blood sugar"
    #                     ],
    #                     "health_risk": [
    #                     "High in histamines (tomatoes, cheese)",
    #                     "Dairy sensitivity possible"
    #                     ],
    #                     "ingredient": [
    #                     {
    #                         "name": "Eggplant (sliced 1/2\" thick)",
    #                         "quantity": "1 medium",
    #                         "emoji": "🍆"
    #                     },
    #                     {
    #                         "name": "Fresh mozzarella",
    #                         "quantity": "4 oz",
    #                         "emoji": "🧀"
    #                     },
    #                     {
    #                         "name": "Tomato (sliced)",
    #                         "quantity": "1 medium",
    #                         "emoji": "🍅"
    #                     },
    #                     {
    #                         "name": "Fresh basil leaves",
    #                         "quantity": "8 large",
    #                         "emoji": "🌿"
    #                     },
    #                     {
    #                         "name": "Balsamic glaze",
    #                         "quantity": "1 tsp",
    #                         "emoji": "🍯"
    #                     }
    #                     ],
    #                     "recipe": [
    #                     "Grill eggplant slices until tender (about 3 min per side)",
    #                     "Layer eggplant, tomato slice, mozzarella, and basil leaves",
    #                     "Repeat to create stack",
    #                     "Drizzle lightly with balsamic glaze",
    #                     "Serve at room temperature"
    #                     ],
    #                     "risk_color": "yellow"
    #                 }
    #                 ]
    #             },
    #             {
    #                 "category": "Italian Light Dinner Solutions (Weight Management)",
    #                 "description": "Evening meals that satisfy Italian culinary cravings while supporting weight loss goals.",
    #                 "items": [
    #                 {
    #                     "label": "Pesto-Stuffed Chicken with Roasted Vegetables",
    #                     "emoji": "🍗🇮🇹🌿",
    #                     "nutrient_proportion": {
    #                     "protein": "0.50",
    #                     "carbohydrates": "0.20",
    #                     "fat": "0.30"
    #                     },
    #                     "calories_aggregate": "380 / serving",
    #                     "health_benefit": [
    #                     "High protein content supports muscle retention during weight loss",
    #                     "Vegetables provide fiber for digestive health",
    #                     "Healthy fats from pesto support nutrient absorption",
    #                     "Low-carb preparation helps maintain ketosis if desired"
    #                     ],
    #                     "health_risk": [
    #                     "Potential allergen (nuts in pesto)",
    #                     "Undercooked poultry risk if not prepared properly"
    #                     ],
    #                     "ingredient": [
    #                     {
    #                         "name": "Chicken breast",
    #                         "quantity": "6 oz",
    #                         "emoji": "🍗"
    #                     },
    #                     {
    #                         "name": "Basil pesto",
    #                         "quantity": "2 tbsp",
    #                         "emoji": "🌿"
    #                     },
    #                     {
    #                         "name": "Zucchini (diced)",
    #                         "quantity": "1 cup",
    #                         "emoji": "🥒"
    #                     },
    #                     {
    #                         "name": "Bell peppers (sliced)",
    #                         "quantity": "1/2 cup",
    #                         "emoji": "🫑"
    #                     },
    #                     {
    #                         "name": "Olive oil",
    #                         "quantity": "1 tsp",
    #                         "emoji": "🫒"
    #                     }
    #                     ],
    #                     "recipe": [
    #                     "Preheat oven to 400°F (200°C)",
    #                     "Butterfly chicken breast and spread pesto inside",
    #                     "Secure with toothpicks and place on baking sheet",
    #                     "Toss vegetables with olive oil and arrange around chicken",
    #                     "Roast for 20-25 minutes until chicken reaches 165°F (74°C)"
    #                     ],
    #                     "risk_color": "yellow"
    #                 },
    #                 {
    #                     "label": "Seafood Cioppino Light",
    #                     "emoji": "🍤🇮🇹🍅",
    #                     "nutrient_proportion": {
    #                     "protein": "0.45",
    #                     "carbohydrates": "0.30",
    #                     "fat": "0.25"
    #                     },
    #                     "calories_aggregate": "290 / serving",
    #                     "health_benefit": [
    #                     "Rich in omega-3 fatty acids from seafood",
    #                     "Lyopene from cooked tomatoes supports heart health",
    #                     "Low-calorie yet satisfying broth-based dish",
    #                     "Excellent source of iodine and selenium"
    #                     ],
    #                     "health_risk": [
    #                     "Shellfish allergies",
    #                     "High sodium if using canned ingredients"
    #                     ],
    #                     "ingredient": [
    #                     {
    #                         "name": "White fish fillet",
    #                         "quantity": "4 oz",
    #                         "emoji": "🐟"
    #                     },
    #                     {
    #                         "name": "Shrimp (peeled)",
    #                         "quantity": "6 large",
    #                         "emoji": "🍤"
    #                     },
    #                     {
    #                         "name": "Tomato (diced)",
    #                         "quantity": "1 cup",
    #                         "emoji": "🍅"
    #                     },
    #                     {
    #                         "name": "White wine",
    #                         "quantity": "1/4 cup",
    #                         "emoji": "🍷"
    #                     },
    #                     {
    #                         "name": "Garlic (minced)",
    #                         "quantity": "2 cloves",
    #                         "emoji": "🧄"
    #                     }
    #                     ],
    #                     "recipe": [
    #                     "Sauté garlic in olive oil until fragrant",
    #                     "Add tomatoes and wine, simmer for 10 minutes",
    #                     "Add fish and shrimp, cover and cook 5-7 minutes",
    #                     "Season with Italian herbs and pepper",
    #                     "Serve with lemon wedge"
    #                     ],
    #                     "risk_color": "yellow"
    #                 }
    #                 ]
    #             },
    #             {
    #                 "category": "Italian Breakfast Alternatives (Weight Management)",
    #                 "description": "Morning meals inspired by Italian tradition but optimized for portion control and nutrition.",
    #                 "items": [
    #                 {
    #                     "label": "Ricotta and Berry Breakfast Bowl",
    #                     "emoji": "🥣🇮🇹🫐",
    #                     "nutrient_proportion": {
    #                     "protein": "0.35",
    #                     "carbohydrates": "0.40",
    #                     "fat": "0.25"
    #                     },
    #                     "calories_aggregate": "240 / serving",
    #                     "health_benefit": [
    #                     "High protein start to the day reduces snacking",
    #                     "Antioxidants from berries support cellular health",
    #                     "Calcium from ricotta promotes bone strength",
    #                     "Low glycemic impact helps control cravings"
    #                     ],
    #                     "health_risk": [
    #                     "Dairy sensitivity possible",
    #                     "Natural sugars from fruit"
    #                     ],
    #                     "ingredient": [
    #                     {
    #                         "name": "Part-skim ricotta",
    #                         "quantity": "1/2 cup",
    #                         "emoji": "🧀"
    #                     },
    #                     {
    #                         "name": "Mixed berries",
    #                         "quantity": "3/4 cup",
    #                         "emoji": "🫐"
    #                     },
    #                     {
    #                         "name": "Chia seeds",
    #                         "quantity": "1 tsp",
    #                         "emoji": "🌱"
    #                     },
    #                     {
    #                         "name": "Lemon zest",
    #                         "quantity": "1/2 tsp",
    #                         "emoji": "🍋"
    #                     },
    #                     {
    #                         "name": "Honey",
    #                         "quantity": "1/2 tsp",
    #                         "emoji": "🍯"
    #                     }
    #                     ],
    #                     "recipe": [
    #                     "Mix ricotta with lemon zest",
    #                     "Top with fresh berries",
    #                     "Sprinkle chia seeds",
    #                     "Drizzle lightly with honey",
    #                     "Let sit 5 minutes before eating"
    #                     ],
    #                     "risk_color": "green"
    #                 },
    #                 {
    #                     "label": "Frittata Muffins with Sun-Dried Tomatoes",
    #                     "emoji": "🧁🇮🇹🍅",
    #                     "nutrient_proportion": {
    #                     "protein": "0.45",
    #                     "carbohydrates": "0.20",
    #                     "fat": "0.35"
    #                     },
    #                     "calories_aggregate": "180 / serving (2 muffins)",
    #                     "health_benefit": [
    #                     "Portion-controlled protein source",
    #                     "Convenient make-ahead breakfast option",
    #                     "Sun-dried tomatoes provide concentrated nutrients",
    #                     "Helps maintain muscle mass during calorie restriction"
    #                     ],
    #                     "health_risk": [
    #                     "Egg allergy",
    #                     "High cholesterol for sensitive individuals"
    #                     ],
    #                     "ingredient": [
    #                     {
    #                         "name": "Eggs",
    #                         "quantity": "4 large",
    #                         "emoji": "🥚"
    #                     },
    #                     {
    #                         "name": "Sun-dried tomatoes",
    #                         "quantity": "1/4 cup",
    #                         "emoji": "🍅"
    #                     },
    #                     {
    #                         "name": "Baby spinach",
    #                         "quantity": "1 cup",
    #                         "emoji": "🥬"
    #                     },
    #                     {
    #                         "name": "Parmesan cheese",
    #                         "quantity": "2 tbsp",
    #                         "emoji": "🧀"
    #                     },
    #                     {
    #                         "name": "Olive oil",
    #                         "quantity": "1 tsp",
    #                         "emoji": "🫒"
    #                     }
    #                     ],
    #                     "recipe": [
    #                     "Preheat oven to 350°F (175°C)",
    #                     "Whisk eggs with grated parmesan",
    #                     "Chop tomatoes and spinach, mix into eggs",
    #                     "Grease muffin tin with olive oil",
    #                     "Divide mixture into 6 muffin cups",
    #                     "Bake 15-18 minutes until set"
    #                     ],
    #                     "risk_color": "yellow"
    #                 }
    #                 ]
    #             }
    #         ]
    #     }

    #     # Load the base model
    #     self.model = AutoModelForCausalLM.from_pretrained(
    #         self.model_id,
    #         device_map="cpu",  # use CPU if no GPU
    #         torch_dtype=torch.float32,  # use FP32 for CPU
    #         trust_remote_code=True,
    #         attn_implementation="eager",
    #     )

    #     # Prepare model for LoRA fine-tuning
    #     self.model = prepare_model_for_kbit_training(self.model)

    #     # Setup LoRA configuration
    #     lora_config = LoraConfig(
    #         r=16,  # Rank size (small = lighter, big = more powerful)
    #         lora_alpha=32,
    #         target_modules=["q_proj", "v_proj"],  # typical for transformers
    #         lora_dropout=0.05,
    #         bias="none",
    #         task_type="CAUSAL_LM"
    #     )

    #     # Apply LoRA
    #     self.model = get_peft_model(self.model, lora_config)

    #     # Prepare dataset
    #     self.train_dataset = Dataset.from_dict(self.data_set)

    #     # Tokenize dataset
    #     def tokenize_function(examples):
    #         return self.tokenizer(
    #             examples["prompt"],
    #             text_target=examples["response"],
    #             truncation=True,
    #             padding="max_length",
    #             max_length=2048,  # 8192 is very heavy for most consumer GPUs
    #         )

    #     self.train_dataset = self.train_dataset.map(tokenize_function, batched=True)

    #     # Training args
    #     self.training_args = TrainingArguments(
    #         output_dir="./deepseek-food-finetuned",
    #         per_device_train_batch_size=2,
    #         gradient_accumulation_steps=4,
    #         num_train_epochs=3,
    #         learning_rate=2e-4,
    #         warmup_steps=100,
    #         logging_dir="./logs",
    #         logging_steps=10,
    #         save_total_limit=2,
    #         fp16=True,
    #         push_to_hub=False,
    #         save_strategy="epoch"
    #     )

    #     self.trainer = Trainer(
    #         model=self.model,
    #         args=self.training_args,
    #         train_dataset=self.train_dataset,
    #         tokenizer=self.tokenizer,
    #     )

    # def format_sample(self, prompt, response):
    #     return {
    #         "input_ids": self.tokenizer.encode(prompt, truncation=True, max_length=2048),
    #         "labels": self.tokenizer.encode(response, truncation=True, max_length=2048)
    #     }

    # def extract_list_items(self, text):
    #     matches = re.findall(r'\[(.*?)\]', text, re.DOTALL)
    #     if matches:
    #         content_inside_brackets = matches[0].strip()
    #         result = f"[{content_inside_brackets}]"
    #         return result
    #     else:
    #         print("No square brackets found.")
    #         return None

    # def get_search_text_from_chat(self, text):
    #     try:
    #         generator = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer, device=0)

    #         response = generator(
    #             text,
    #             max_new_tokens=300,  # careful: use small numbers for generation
    #             do_sample=True,
    #             temperature=0.7
    #         )
    #         return response[0]['generated_text']
    #     except Exception as e:
    #         print(f"An error occurred: {e}")
    #         raise HTTPException(status_code=500, detail=str(e))

    def search_food(self, user_input):
        try:
            # food_list = self.get_search_text_from_chat(user_input)
            # print(food_list)
            # return food_list
            pipe = pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0", torch_dtype=torch.bfloat16, device_map="auto")

            # We use the tokenizer's chat template to format each message - see https://huggingface.co/docs/transformers/main/en/chat_templating
            messages = [
                {
                    "role": "system",
                    "content": "You are a friendly chatbot in charge of generating structured output for food that",
                },
                {"role": "user", "content": "Suggest classes of food that fall under weight management"},
            ]
            prompt = pipe.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            outputs = pipe(prompt, max_new_tokens=256, do_sample=True, temperature=0.7, top_k=50, top_p=0.95)
         
            return outputs[0]["generated_text"]
        except Exception as e:
            print(f"An error occurred: {e}")
            raise HTTPException(status_code=500, detail=str(e))
