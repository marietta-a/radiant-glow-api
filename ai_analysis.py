from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI
from os import getenv
from dotenv import load_dotenv
from helper import *


class AIAnalysis:

    def __init__(self):
        load_dotenv()
        self.apiKey = getenv("OPENROUTER_API_KEY")
        self.baseUrl = getenv("OPENROUTER_BASE_URL")        
        self.model = getenv("MODEL")
        self.appUrl = getenv("APP_URL")
        self.appName = getenv("APP_NAME")
        self.max_tokens=100000
        self.max_tokens_tiny=8000
        self.llm = ChatOpenAI(
            openai_api_key=self.apiKey,
            openai_api_base=self.baseUrl,
            model_name=self.model,
            max_tokens= self.max_tokens,
            model_kwargs={
                # "headers": {
                # "HTTP-Referer": self.appUrl,
                # "X-Title": self.appName,
                # }
            },
        )

        self.tiny_llm = ChatOpenAI(
            openai_api_key=self.apiKey,
            openai_api_base=self.baseUrl,
            model_name=self.model,
            max_tokens= self.max_tokens_tiny,
            model_kwargs={
                # "headers": {
                # "HTTP-Referer": self.appUrl,
                # "X-Title": self.appName,
                # }
            },
        )

    def search_food(self, query):

        template = """using the sample json format below as a guide. The response should be a json formatted list of foods that start with {query}.
                        Sample json output format:
                    [
                        {{
                            "name": "Fufu",
                            "description": "A staple food in many African countries, made from boiled and pounded starchy vegetables like cassava, yams, or plantains.",
                            "region": "West Africa, Central Africa",
                            "type": "Staple food"
                        }},
                        {{
                            "name": "Fufu de Platano",
                            "description": "A variation of fufu made primarily from green plantains, commonly found in Caribbean and West African cuisine.",
                            "region": "Caribbean, West Africa",
                            "type": "Staple food"
                        }},
                        {{
                            "name": "Fufu Corn",
                            "description": "A version of fufu made from fermented corn dough, often eaten with soups or stews.",
                            "region": "West Africa",
                            "type": "Staple food"
                        }},
                        {{
                            "name": "Fufu Flour",
                            "description": "Pre-processed flour made from cassava, yam, or plantain, used to prepare fufu more quickly.",
                            "region": "Global (African diaspora)",
                            "type": "Processed food"
                        }},
                        {{
                            "name": "Fufu and Egusi Soup",
                            "description": "A traditional West African dish consisting of fufu served with a rich, melon seed-based soup.",
                            "region": "Nigeria, Ghana, Cameroon",
                            "type": "Complete dish"
                        }},
                        {{
                            "name": "Fufu and Light Soup",
                            "description": "A Ghanaian favorite where fufu is paired with a light, tomato-based soup often containing fish or meat.",
                            "region": "Ghana",
                            "type": "Complete dish"
                        }}
                    ]
                    """

        prompt = PromptTemplate(input_variables=["query"], template=template)

        chain = prompt | self.tiny_llm
        response = chain.invoke({"query": f"{query}"})
        try:
            return extract_json_list(response.content)
        except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))
        
    def get_diet_suggestions(self, category, category_item, country=None, state=None, city=None, limit=20):

        template = """
            [
                {{
                "category": "Desserts",
                "description": "Desserts are sweet, indulgent dishes typically served at the end of a meal",
                "items": [
                {{
                "label": "Baked Pear with Cinnamon",
                "emoji": "🍐✨🍩",
                "nutrient_proportion": {{
                "protein": "0.03",
                "carbohydrates": "0.9",
                "fat": "0.07"
                }},
                "calories_aggregate": 150 / serving,
                "health_benefit": [
                "Fiber",
                "Vitamins",
                "Antioxidants"
                ],
                "health_risk": [
                "Potential sugar content",
                "Possible allergic reaction (to pear)"
                ],
                "ingredient": [
                {{
                "name": "Pear",
                "quantity": "1 medium",
                "emoji", "🍐"
                }},
                {{
                "name": "Cinnamon",
                "quantity": "1/4 tsp"
                "emoji", "🍂"
                }}
                ],
                "recipe": [
                "Core pear and sprinkle with cinnamon.",
                "Bake at 375F until soft (about 20 minutes)."
                ],
                "risk_color": "green"
                }},
                {{
                "label": "Fruit Skewers with a Drizzle of Honey",
                "emoji": "🍓🍍🍐🍯",
                "nutrient_proportion": {{
                "protein": "0.05",
                "carbohydrates": "0.9",
                "fat": "0.05"
                }},
                "calories_aggregate": 120 / serving,
                "health_benefit": [
                "Vitamins",
                "Minerals",
                "Hydration"
                ],
                "health_risk": [
                "High sugar content",
                "Potential for bee sting allergy (honey)"
                ],
                "ingredient": [
                {{
                "name": "Assorted fruits (grapes, melon, berries)",
                "quantity": "1 cup",
                "emoji", "🍇🍉🍓"
                }},
                {{
                "name": "Honey",
                "quantity": "1 tsp (optional)",
                "emoji", "🍯"
                }}
                ],
                "recipe": [
                "Thread fruit onto skewers.",
                "Drizzle with honey (optional)."
                ],
                "risk_color": "green"
                }},
                {{
                "label": "Roasted Sweet Potato with Cinnamon",
                "emoji": "🍠🍂",
                "nutrient_proportion": {{
                "protein": "0.05",
                "carbohydrates": "0.85",
                "fat": "0.1"
                }},
                "calories_aggregate": 130 / serving,
                "health_benefit": [
                "Vitamin A",
                "Fiber",
                "Antioxidants"
                ],
                "health_risk": [
                "Potential sugar content",
                "Oxalates (if prone to kidney stones)"
                ],
                "ingredient": [
                {{
                "name": "Sweet potato (small)",
                "quantity": "1",
                "emoji", "🍠"
                }},
                {{
                "name": "Cinnamon",
                "quantity": "1/4 tsp",
                "emoji", "🍂"
                }}
                ],
                "recipe": [
                "Bake sweet potato until soft.",
                "Sprinkle with cinnamon."
                ],
                "risk_color": "green"
                }}
                ]
                }}
            ]
            using the template above,  generate json formatted output of {limit} {category_item} food items (very nutritive - green color range) that fall under {category} category 
            using cuisines from {country} {state} {city}. 
            Analyze and ensure items generate meets it's goal with an optimal level of accuracy
            Note:
            health benefits should also indicate illness it may cure and how it meets the goal, {category}, 
            calories_aggregate should be / serving
            color Must not be null
            recipe should be detailed. Steps should include all ingredients
            use maximum accuracy for computation
        """

        prompt = PromptTemplate(
           input_variables=["category", 'category_item', 'country', 'state', 'city', 'limit'], 
           template=template
        )

        chain = prompt | self.llm
        response = chain.invoke({"category": f"{category}", 
                                 'category_item': f"{category_item}",
                                 'country': f"{country}",
                                 'state': f"{state}",
                                 'city': f"{city}",
                                 'limit': f"{limit}"
                                 })
        try:
            print(response.content)
            return extract_json_list(response.content)
        except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

    def get_object_count(self, query):

        template = """generate a list of distinct labels and the number of times the label occurs in {query}.
                        output format as shown below:
                    [
                        {{
                            "label": "tomato",
                            "count": 3
                        }},
                        {{
                            "label": "avocado",
                            "count": 3
                        }},
                        {{
                            "label": "egg",
                            "count": 5
                        }},
                        {{
                            "label": "cheese",
                            "count": 3
                        }}
                    ]
                    """

        prompt = PromptTemplate(input_variables=["query"], template=template)

        chain = prompt | self.tiny_llm
        response = chain.invoke({"query": f"{query}"})
        try:
            print(response.content)
            return extract_json_list(response.content)
        except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))
        
        
    def get_diet_suggestions(self, category, category_item, country=None, state=None, city=None, limit=20):

        template = """
            [
                {{
                "category": "Desserts",
                "description": "Desserts are sweet, indulgent dishes typically served at the end of a meal",
                "items": [
                {{
                "label": "Baked Pear with Cinnamon",
                "emoji": "🍐✨🍩",
                "nutrient_proportion": {{
                "protein": "0.03",
                "carbohydrates": "0.9",
                "fat": "0.07"
                }},
                "calories_aggregate": 150 / serving,
                "health_benefit": [
                "Fiber",
                "Vitamins",
                "Antioxidants"
                ],
                "health_risk": [
                "Potential sugar content",
                "Possible allergic reaction (to pear)"
                ],
                "ingredient": [
                {{
                "name": "Pear",
                "quantity": "1 medium",
                "emoji", "🍐"
                }},
                {{
                "name": "Cinnamon",
                "quantity": "1/4 tsp"
                "emoji", "🍂"
                }}
                ],
                "recipe": [
                "Core pear and sprinkle with cinnamon.",
                "Bake at 375F until soft (about 20 minutes)."
                ],
                "risk_color": "green"
                }},
                {{
                "label": "Fruit Skewers with a Drizzle of Honey",
                "emoji": "🍓🍍🍐🍯",
                "nutrient_proportion": {{
                "protein": "0.05",
                "carbohydrates": "0.9",
                "fat": "0.05"
                }},
                "calories_aggregate": 120 / serving,
                "health_benefit": [
                "Vitamins",
                "Minerals",
                "Hydration"
                ],
                "health_risk": [
                "High sugar content",
                "Potential for bee sting allergy (honey)"
                ],
                "ingredient": [
                {{
                "name": "Assorted fruits (grapes, melon, berries)",
                "quantity": "1 cup",
                "emoji", "🍇🍉🍓"
                }},
                {{
                "name": "Honey",
                "quantity": "1 tsp (optional)",
                "emoji", "🍯"
                }}
                ],
                "recipe": [
                "Thread fruit onto skewers.",
                "Drizzle with honey (optional)."
                ],
                "risk_color": "green"
                }},
                {{
                "label": "Roasted Sweet Potato with Cinnamon",
                "emoji": "🍠🍂",
                "nutrient_proportion": {{
                "protein": "0.05",
                "carbohydrates": "0.85",
                "fat": "0.1"
                }},
                "calories_aggregate": 130 / serving,
                "health_benefit": [
                "Vitamin A",
                "Fiber",
                "Antioxidants"
                ],
                "health_risk": [
                "Potential sugar content",
                "Oxalates (if prone to kidney stones)"
                ],
                "ingredient": [
                {{
                "name": "Sweet potato (small)",
                "quantity": "1",
                "emoji", "🍠"
                }},
                {{
                "name": "Cinnamon",
                "quantity": "1/4 tsp",
                "emoji", "🍂"
                }}
                ],
                "recipe": [
                "Bake sweet potato until soft.",
                "Sprinkle with cinnamon."
                ],
                "risk_color": "green"
                }}
                ]
                }}
            ]
            using the template above,  generate json formatted output of {limit} {category_item} food items (very nutritive - green color range) that fall under {category} category 
            using cuisines from {country} {state} {city}. 
            Analyze and ensure items generate meets it's goal with an optimal level of accuracy
            Note:
            health benefits should also indicate illness it may cure and how it meets the goal, {category}, 
            calories_aggregate should be / serving
            color Must not be null
            recipe should be detailed. Steps should include all ingredients
            use maximum accuracy for computation
        """

        prompt = PromptTemplate(
           input_variables=["category", 'category_item', 'country', 'state', 'city', 'limit'], 
           template=template
        )

        chain = prompt | self.llm
        response = chain.invoke({"category": f"{category}", 
                                 'category_item': f"{category_item}",
                                 'country': f"{country}",
                                 'state': f"{state}",
                                 'city': f"{city}",
                                 'limit': f"{limit}"
                                 })
        try:
            print(response.content)
            return extract_json_list(response.content)
        except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))