import asyncio
from monitor_graph import monitor_graph
from models import Event

async def main():
    print("Testing Monitor Agent...")
    source_url = "https://tldr.tech/ai"
    
    # Run the graph
    result = await monitor_graph.ainvoke({"source_url": source_url})
    
    if result.get("error"):
        print(f"Error: {result['error']}")
    else:
        print("Success!")
        events = result.get("analysis_results", [])
        print(f"Found {len(events)} events.")
        for e in events:
            print(f"- [{e.analysis.sentiment}] {e.title}")
            print(f"  Url: {e.url}")

if __name__ == "__main__":
    asyncio.run(main())
