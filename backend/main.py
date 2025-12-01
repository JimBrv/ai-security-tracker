from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uvicorn
import os
from dotenv import load_dotenv

from models import Website, Event
from database import load_websites, save_websites, load_events, save_events
from graph import app_graph

load_dotenv()

app = FastAPI(title="AI Security Tracker API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Endpoints ---

@app.get("/websites")
def get_websites():
    websites = load_websites()
    events = load_events()
    
    # Calculate event counts
    result = []
    for w in websites:
        count = sum(1 for e in events if e.source_website_id == w.id)
        # Create a dict response with the extra field
        w_dict = w.model_dump()
        w_dict['event_count'] = count
        result.append(w_dict)
        
    return result

@app.post("/websites", response_model=Website)
def add_website(website: Website):
    websites = load_websites()
    websites.append(website)
    save_websites(websites)
    return website

@app.delete("/websites/{website_id}")
def delete_website(website_id: str):
    websites = load_websites()
    websites = [w for w in websites if w.id != website_id]
    save_websites(websites)
    return {"status": "success"}

@app.get("/events", response_model=List[Event])
def get_events():
    return load_events()

async def run_scan_task(website: Website):
    print(f"Starting background scan for {website.name}")
    try:
        # Invoke the graph
        result = await app_graph.ainvoke({"website": website})
        if result.get("analysis_result") == "OK":
            print(f"Scan complete for {website.name}: ")
        elif result.get("error"):
            print(f"Scan failed for {website.name}: {result['error']}")
        else:
            print(f"Scan complete for {website.name}: No relevant events found.")
    except Exception as e:
        print(f"Error running scan for {website.name}: {e}")

@app.post("/scan/{website_id}")
async def scan_website(website_id: str, background_tasks: BackgroundTasks):
    websites = load_websites()
    website = next((w for w in websites if w.id == website_id), None)
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")
    
    background_tasks.add_task(run_scan_task, website)
    return {"status": "Scan started", "website": website.name}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
