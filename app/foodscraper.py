import requests
from bs4 import BeautifulSoup
import re
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

class FoodScraper:
    def __init__(self):
        self.sources = {
            "Wikipedia": "https://en.wikipedia.org/wiki/List_of_foods",
            "Food.com": "https://www.food.com/ideas/ultimate-a-z-food-list-7655",
            "BBC GoodFood": "https://www.bbcgoodfood.com/recipes/a-z",
            "AllRecipes": "https://www.allrecipes.com/ingredients-a-z-6740416"
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def scrape_wikipedia(self, keyword):
        url = self.sources["Wikipedia"]
        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            foods = []
            
            # Find all list items containing food names
            for li in soup.select('div.mw-parser-output ul li'):
                text = li.get_text().strip()
                # Match items starting with keyword (case insensitive)
                if re.match(f'^{keyword.lower()}', text.lower()):
                    # Clean the text (remove footnotes, etc.)
                    clean_text = re.sub(r'\[.*?\]', '', text).strip()
                    foods.append(clean_text)
            return foods[:100]  # Limit to top 100 matches
            
        except Exception as e:
            print(f"Wikipedia scraping error: {e}")
            return []

    def scrape_food_com(self, keyword):
        url = self.sources["Food.com"]
        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            foods = []
            
            # Food.com lists items in paragraphs
            for p in soup.select('div.article-content p'):
                text = p.get_text().strip()
                if re.match(f'^{keyword.lower()}', text.lower()):
                    clean_text = re.sub(r'\s+', ' ', text).strip()
                    foods.append(clean_text)
            return foods[:100]
            
        except Exception as e:
            print(f"Food.com scraping error: {e}")
            return []

    def scrape_bbc_goodfood(self, keyword):
        url = self.sources["BBC GoodFood"]
        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            foods = []
            
            # BBC GoodFood uses list items with links
            for a in soup.select('div.az-list__wrapper a'):
                text = a.get_text().strip()
                if re.match(f'^{keyword.lower()}', text.lower()):
                    foods.append(text)
            return foods[:100]
            
        except Exception as e:
            print(f"BBC GoodFood scraping error: {e}")
            return []

    def scrape_allrecipes(self, keyword):
        url = self.sources["AllRecipes"]
        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            foods = []
            
            # AllRecipes uses heading elements
            for h3 in soup.select('div.article-body h3'):
                text = h3.get_text().strip()
                if re.match(f'^{keyword.lower()}', text.lower()):
                    foods.append(text)
            return foods[:100]
            
        except Exception as e:
            print(f"AllRecipes scraping error: {e}")
            return []

    def search_food_items(self, keyword, max_workers=4):
        """Search all sources concurrently for food items starting with keyword"""
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                "Wikipedia": executor.submit(self.scrape_wikipedia, keyword),
                "Food.com": executor.submit(self.scrape_food_com, keyword),
                "BBC GoodFood": executor.submit(self.scrape_bbc_goodfood, keyword),
                "AllRecipes": executor.submit(self.scrape_allrecipes, keyword)
            }
            
            for source, future in futures.items():
                # results[source] = future.result()
                results.extend(future.result())
        distinct_elements = list(set(results))
        distinct_elements.sort()
        return distinct_elements

    

# Usage Example
if __name__ == "__main__":
    scraper = FoodScraper()
    
    # Search for foods starting with "apple"
    keyword = "apple"
    results = scraper.search_food_items(keyword)
    
    # Print results
    for source, foods in results.items():
        print(f"\n{source} Results ({len(foods)} items):")
        print("\n".join(foods[:10]))  # Print first 10 items
    
    # Save to CSV
    scraper.save_to_csv(results, f"{keyword}_foods.csv")