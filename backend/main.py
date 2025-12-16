from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uvicorn
import os
from dotenv import load_dotenv

from models import Website, Event, Prompt
from database import load_websites, save_websites, load_events, save_events
from graph import app_graph
from monitor_graph import monitor_graph, generate_daily_summary_report

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

# --- Prompt Endpoints ---

@app.get("/prompts", response_model=List[Prompt])
def get_prompts():
    from database import load_prompts
    return load_prompts()

@app.post("/prompts/{name}", response_model=Prompt)
def update_prompt(name: str, prompt: Prompt):
    from database import load_prompts, save_prompts
    prompts = load_prompts()
    
    # Check if prompt exists
    existing_index = next((i for i, p in enumerate(prompts) if p.name == name), None)
    
    if existing_index is not None:
        prompts[existing_index] = prompt
    else:
        # Prevent creating arbitrary new prompts that the system doesn't know about? 
        # For now, let's allow updating existing ones. 
        # If we want to allow new ones, we'd append.
        # But system code relies on specific names.
        raise HTTPException(status_code=404, detail="Prompt not found")
        
    save_prompts(prompts)
    return prompt

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

async def run_monitor_task(source_url: str):
    print(f"Starting background monitor for {source_url}")
    try:
        result = await monitor_graph.ainvoke({"source_url": source_url})
        if result.get("error"):
            print(f"Monitor failed for {source_url}: {result['error']}")
        else:
            print(f"Monitor complete for {source_url}")
    except Exception as e:
        print(f"Error running monitor for {source_url}: {e}")

class MonitorRequest(BaseModel):
    source_url: str

@app.post("/monitor/run")
async def run_monitor(request: MonitorRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_monitor_task, request.source_url)
    return {"status": "Monitor started", "source": request.source_url}

@app.get("/monitor/summary")
def get_monitor_summary():
    return {"summary": generate_daily_summary_report()}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
