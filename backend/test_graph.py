import asyncio
import os
import sys
from dotenv import load_dotenv
from models import Website, Event
from graph import app_graph

load_dotenv()

async def test_graph(url: str):
    print("--- Starting Graph Test ---")
    
    # Create a dummy website object
    # Using a known AI security blog for relevance
    website = Website(
        name="Test - Zenity", 
        url=url, 
        description="Test Description"
    )
    
    print(f"Testing with website: {website.url}")
    
    try:
        # Invoke the graph
        result = await app_graph.ainvoke({"website": website})
        print(f"Langchain return: {result}")
        ev = result.get("final_event")
        i = 0
        for e in ev:
            print("\n✅ SUCCESS: Event found and analyzed!")
            print(f"{i}.Title: {e.title}")
            print(f"{i}.Url: {e.url}")
            print(f"{i}.Summary: {e.analysis}")
            i=i+1

    except Exception as e:
        print(f"\n❌ EXCEPTION during test: {e}")

if __name__ == "__main__":
    asyncio.run(test_graph(sys.argv[1]))
