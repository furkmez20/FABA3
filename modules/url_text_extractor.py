import requests
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urlparse

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def extract_text_from_url(url):
    """
    Fetches and extracts readable text content from a given website URL.
    Returns a list of paragraphs.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        # Extract text from paragraph and article tags
        paragraphs = [p.get_text(strip=True) for p in soup.find_all(['p', 'article']) if p.get_text(strip=True)]

        # Filter out short or empty lines
        cleaned = [p for p in paragraphs if len(p) > 40]

        return cleaned

    except Exception as e:
        print(f"❌ Error fetching URL content: {e}")
        return []

def convert_url_to_json(url, output_path="url_content.json"):
    """
    Fetches text from a URL and saves it in a JSON format similar to uploaded files.
    Returns (json_path, paragraphs).
    """
    if not is_valid_url(url):
        raise ValueError("Invalid URL provided.")

    paragraphs = extract_text_from_url(url)

    if not paragraphs:
        raise ValueError("No readable content found at the provided URL.")

    json_data = [{"id": i+1, "text": para} for i, para in enumerate(paragraphs)]

    output_dir = os.path.dirname(output_path) or os.getcwd()
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    final_json_path = os.path.join(output_dir, os.path.basename(output_path))

    with open(final_json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    return final_json_path, paragraphs
