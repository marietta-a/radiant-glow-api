

from ddgs import DDGS
import time 


async def get_duckduckgo_image_urls(query: str, num_images: int = 2) -> list[str]:
    start = time.time()
    """Search DuckDuckGo Images and return a list of image URLs."""
    if not isinstance(num_images, int) or num_images <= 0:
        raise ValueError("num_images must be a positive integer")

    ddgs = DDGS()  # Initialize DuckDuckGo Search
    results = ddgs.images(query, max_results=num_images)  # Corrected method call
        
    end = time.time()
    elapsed = end - start

    print(f"Elapsed time: {elapsed} seconds")
    # print(results)
    return [result["image"] for result in results if "image" in result]