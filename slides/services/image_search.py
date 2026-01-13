"""
Google Image Search Service
Converts AI-generated image queries into actual image URLs using Google Custom Search API
"""
import os
import requests
from typing import Optional, List, Dict

class ImageSearchService:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        self.search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        
        if not self.api_key or not self.search_engine_id:
            print("Warning: Google Search API credentials not configured")
            print("Set GOOGLE_SEARCH_API_KEY and GOOGLE_SEARCH_ENGINE_ID in .env")
    
    def search_images(self, query: str, num_results: int = 3) -> List[Dict[str, str]]:
        """
        Search for images using Google Custom Search API
        
        Args:
            query: Search query string
            num_results: Number of results to return (max 10)
            
        Returns:
            List of dicts with 'url', 'title', 'thumbnail' keys
        """
        if not self.api_key or not self.search_engine_id:
            # Return placeholder if API not configured
            return self._get_placeholder_images(query, num_results)
        
        try:
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'searchType': 'image',
                'num': min(num_results, 10),
                'safe': 'active',  # Safe search for educational content
                'imgSize': 'large',
                'fileType': 'jpg|png'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            results = []
            for item in data.get('items', []):
                results.append({
                    'url': item.get('link'),
                    'title': item.get('title'),
                    'thumbnail': item.get('image', {}).get('thumbnailLink'),
                    'width': item.get('image', {}).get('width'),
                    'height': item.get('image', {}).get('height')
                })
            
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"Image search failed: {e}")
            return self._get_placeholder_images(query, num_results)
        except Exception as e:
            print(f"Unexpected error in image search: {e}")
            return self._get_placeholder_images(query, num_results)
    
    def get_best_image(self, query: str) -> Optional[str]:
        """
        Get the best (first) image URL for a query
        
        Args:
            query: Search query string
            
        Returns:
            Image URL or None
        """
        results = self.search_images(query, num_results=1)
        if results and len(results) > 0:
            return results[0].get('url')
        return None
    
    def _get_placeholder_images(self, query: str, num_results: int) -> List[Dict[str, str]]:
        """
        Return placeholder image data when API is not available
        Uses placeholder image services
        """
        placeholders = []
        for i in range(num_results):
            # Using picsum.photos as a fallback placeholder service
            placeholders.append({
                'url': f'https://picsum.photos/800/600?random={hash(query) + i}',
                'title': f'Placeholder for: {query}',
                'thumbnail': f'https://picsum.photos/200/150?random={hash(query) + i}',
                'width': 800,
                'height': 600
            })
        return placeholders
    
    def batch_search(self, queries: List[str]) -> Dict[str, str]:
        """
        Search for multiple images at once
        
        Args:
            queries: List of search query strings
            
        Returns:
            Dict mapping query to best image URL
        """
        results = {}
        for query in queries:
            url = self.get_best_image(query)
            if url:
                results[query] = url
        return results
