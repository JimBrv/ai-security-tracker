import asyncio
import os
from dotenv import load_dotenv
from models import Website
from graph import app_graph

load_dotenv()

async def test_graph():
    print("--- Starting Graph Test ---")
    
    # Create a dummy website object
    # Using a known AI security blog for relevance
    website = Website(
        name="Test - Zenity", 
        url="https://www.zenity.io/blog/", 
        description="Test Description"
    )
    
    print(f"Testing with website: {website.url}")
    
    try:
        # Invoke the graph
        result = await app_graph.ainvoke({"website": website})
        
        if result.get("final_event"):
            print("\n✅ SUCCESS: Event found and analyzed!")
            print(f"Title: {result['final_event'].title}")
            print(f"Summary: {result['final_event'].analysis.summary}")
        elif result.get("error"):
            print(f"\n❌ ERROR in Graph Execution: {result['error']}")
        else:
            print("\n⚠️  Graph completed but no event found (this might be normal if no relevant links).")
            
    except Exception as e:
        print(f"\n❌ EXCEPTION during test: {e}")

if __name__ == "__main__":
    asyncio.run(test_graph())
