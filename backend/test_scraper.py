#!/usr/bin/env python3
"""Test script to verify the HiddenLayer website scraping fix"""

from tools import extract_links, fetch_page_content
import sys

def test_hiddenlayer(url: str):
    url = url
    print(f"Testing scraping of: {url}\n")
    
    # Test link extraction
    print("=" * 60)
    print("Testing extract_links()...")
    print("=" * 60)
    links = extract_links(url)
    
    if links:
        print(f"✅ SUCCESS! Found {len(links)} links")
        print(f"{links}")
        for i, link in enumerate(links):
            print(f"{i}. {link['text'][:60]}...")
            print(f"   URL: {link['url']}\n")
    else:
        print("❌ FAILED: No links found")
    
    print("\n" + "=" * 60)
    print("Testing fetch_page_content()...")
    print("=" * 60)
    content = fetch_page_content(url)
    
    if content and not content.startswith("Error"):
        print(f"✅ SUCCESS! Fetched {len(content)} characters")
        print(f"\nFirst 200 characters:\n{content[:200]}...")
    else:
        print(f"❌ FAILED: {content}")

if __name__ == "__main__":
    test_hiddenlayer(sys.argv[1])
