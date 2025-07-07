import os
import requests

class AhaAPI:
    def __init__(self, base_url):
        self.api_key = os.getenv('AHA_API_KEY')
        if not self.api_key:
            raise ValueError('AHA_API_KEY environment variable not set.')
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    def fetch_features(self, product_id, per_page=20):
        all_features = []
        page = 1
        while True:
            url = f"{self.base_url}/api/v1/products/{product_id}/features?page={page}&per_page={per_page}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            features = data.get('features', [])
            all_features.extend(features)
            # Stop if less than per_page returned (last page)
            if len(features) < per_page:
                break
            page += 1
        return {'features': all_features} 