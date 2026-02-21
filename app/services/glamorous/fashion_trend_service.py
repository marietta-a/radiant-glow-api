import json
import os
import feedparser
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

CACHE_FILE = "fashion_cache.json"

def fetch_vogue_trends():
    print(f"📡 Fetching Official Vogue Feed at {datetime.now()}...")
    # Using the official RSS feed is 100% more reliable than scraping HTML
    RSS_URL = "https://www.vogue.com/feed/category/fashion-trends/rss"
    
    try:
        feed = feedparser.parse(RSS_URL)
        
        trend_list = []
        
        for entry in feed.entries[:15]: # Get top 15 trends
            # Extract Image URL (Vogue puts it in the 'media_content' or 'links' field)
            img_url = "https://via.placeholder.com/600x800?text=Vogue+Fashion"
            if 'media_content' in entry:
                img_url = entry.media_content[0]['url']
            elif 'links' in entry:
                for link in entry.links:
                    if 'image' in link.get('type', ''):
                        img_url = link.get('href')

            # Clean up description (RSS descriptions sometimes contain HTML tags)
            description = entry.get('summary', '')
            if '<' in description:
                import re
                description = re.sub('<[^<]+?>', '', description) # Remove HTML tags

            trend_list.append({
                "title": entry.get('title', 'Fashion Update'),
                "subtitle": "TRENDING NOW",
                "description": description[:150] + "...", # Shorten description
                "image_url": img_url,
                "editor": entry.get('author', 'Vogue Editors'),
                "comment": "Analyzed for GlamAI Personal Stylist",
                "published": entry.get('published', ''),
                "source_link": entry.get('link', '#')
            })

        if not trend_list:
            print("⚠️ Feed was empty. Checking backup method...")
            return None

        cache_data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data": trend_list
        }

        with open(CACHE_FILE, "w") as f:
            json.dump(cache_data, f, indent=4)
        
        print(f"✅ Cache updated with {len(trend_list)} items.")
        return cache_data

    except Exception as e:
        print(f"❌ Feed fetch failed: {e}")
        return None