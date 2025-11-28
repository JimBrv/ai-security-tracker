#!/usr/bin/env python3
"""Debug script to see what's happening with the request"""

import requests

def debug_request():
    url = "https://hiddenlayer.com/research/"
    
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
    
    proxies = {
        'http': 'http://127.0.0.1:7890',
        'https': 'http://127.0.0.1:7890'
    }
    
    print(f"Requesting: {url}\n")
    
    try:
        response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"Content-Encoding: {response.headers.get('Content-Encoding')}")
        print(f"Content-Length: {len(response.content)} bytes")
        print(f"Text Length: {len(response.text)} characters")
        print(f"\nResponse Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        
        print(f"\n\nFirst 500 characters of response.text:")
        print(response.text[:500])
        
        print(f"\n\nFirst 100 bytes of response.content:")
        print(response.content[:100])
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_request()
