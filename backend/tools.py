import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
from dotenv import load_dotenv

load_dotenv()

# Proxy configuration based on environment variable
USE_PROXY = os.getenv("USE_PROXY", "0") == "1"
PROXY_URL = os.getenv("PROXY_URL", "http://127.0.0.1:7890")

PROXIES = {
    'http': PROXY_URL,
    'https': PROXY_URL
} if USE_PROXY else None

def fetch_page_content(url: str) -> str:
    """
    Fetches the text content of a web page.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        response = requests.get(url, headers=headers, proxies=PROXIES, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
            
        text = soup.get_text(separator=' ', strip=True)
        return text[:15000] # Limit content length to avoid token limits
    except Exception as e:
        return f"Error fetching {url}: {str(e)}"

def extract_links(url: str) -> list[dict]:
    """
    Extracts all links from a page, returning their text and absolute href.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        response = requests.get(url, headers=headers, proxies=PROXIES, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)
            full_url = urljoin(url, href)
            if text and len(text) > 5: # Filter out empty or very short links
                links.append({"text": text, "url": full_url})
        
        # Deduplicate based on URL
        unique_links = {l['url']: l for l in links}.values()
        return list(unique_links)
    except Exception as e:
        print(f"Error extracting links from {url}: {str(e)}")
        return []
