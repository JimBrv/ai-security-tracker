
import os
from typing import List, Optional, Dict, Any, TypedDict
from datetime import datetime
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
import httpx
from dotenv import load_dotenv

from models import Website, Event, Analysis
from tools import fetch_page_content, extract_links
from database import save_events, load_events

load_dotenv()
model = os.getenv("GOOGLE_MODEL")
api_key = os.getenv("GOOGLE_API_KEY")

# --- State Definition ---
class MonitorState(TypedDict):
    source_url: str # e.g., "https://tldr.tech/ai"
    latest_issue_url: Optional[str]
    found_links: List[Dict[str, str]]
    selected_links: Optional[List[Dict[str, str]]]
    analysis_results: Optional[List[Event]]
    error: Optional[str]

# --- Nodes ---

def find_latest_issue_node(state: MonitorState):
    print(f"--- Finding latest issue from {state['source_url']} ---")
    links = extract_links(state['source_url'])
    
    # Heuristic: Find the first link that looks like a date or "Daily Update" or matches the pattern
    # For TLDR, links are usually /ai/YYYY-MM-DD
    
    # We can use LLM to find the "latest issue" link if regex is brittle, but let's try a simple LLM approach for robustness
    
    use_proxy = os.getenv("USE_PROXY", "0") == "1"
    proxy_url = os.getenv("PROXY_URL", "http://127.0.0.1:7890")
    
    if use_proxy:
            transport = httpx.HTTPTransport(proxy=proxy_url)
            client = httpx.Client(transport=transport)
    else:
            client = httpx.Client()

    llm = ChatGoogleGenerativeAI(
        model=model, 
        api_key=api_key,
        temperature=0,
        client=client
    )
    
    parser = JsonOutputParser()
    prompt = ChatPromptTemplate.from_template(
        """
        You are looking for the link to the *latest* newsletter issue from a list of links found on the archive page.
        
        Links:
        {links}
        
        Return a JSON object with "latest_issue_url". If not found, return null.
        Prefer links that look like dates or "Issue #...".
        """
    )
    
    # Limit links to top 50 to save context
    links_subset = links[:50]
    
    chain = prompt | llm | parser
    
    try:
        result = chain.invoke({"links": links_subset})
        if result and result.get("latest_issue_url"):
            print(f"Found latest issue: {result['latest_issue_url']}")
            return {"latest_issue_url": result['latest_issue_url']}
        else:
            return {"error": "Could not find latest issue URL"}
            
    except Exception as e:
        print(f"Error finding latest issue: {e}")
        return {"error": f"Error finding latest issue: {str(e)}"}


def fetch_newsletter_links_node(state: MonitorState):
    url = state.get("latest_issue_url")
    if not url:
        return {"error": "No issue URL to fetch"}
        
    print(f"--- Fetching links from issue {url} ---")
    links = extract_links(url)
    print(f"Found {len(links)} links in newsletter")
    return {"found_links": links}

def filter_monitor_links_node(state: MonitorState):
    print("--- Filtering relevant links for AI Security ---")
    links = state['found_links']
    if not links:
        return {"error": "No links found"}
        
    links_subset = links[:300]
    
    use_proxy = os.getenv("USE_PROXY", "0") == "1"
    proxy_url = os.getenv("PROXY_URL", "http://127.0.0.1:7890")
    
    if use_proxy:
        transport = httpx.HTTPTransport(proxy=proxy_url)
        client = httpx.Client(transport=transport)
    else:
        client = httpx.Client()
    
    llm = ChatGoogleGenerativeAI(
        model=model, 
        api_key=api_key,
        temperature=0,
        client=client
    )
    
    parser = JsonOutputParser()
    
    prompt = ChatPromptTemplate.from_template(
        """
        You are an AI Security Watchdog. 
        Identify articles related to:
        - "AI attack event"
        - "AI threat"
        - "AI vulnerability"
        - Adversarial Machine Learning
        - LLM Injection / Jailbreak
        
        Ignore:
        - General AI news (new models, generic business news)
        - Sponsors/Ads
        - Social media profiles
        
        Links:
        {links}
        
        Return a JSON object array, each with "selected_url" containing the URL.
        """
    )

    chain = prompt | llm | parser
    
    try:
        result = chain.invoke({"links": links_subset})
        select = []

        if result is None: 
            return {"selected_links": []} # Return empty list, not error, to complete gracefully
        
        for l in result:
             selected_link_obj = next((j for j in links if j['url'] == l['selected_url']), None)
             if selected_link_obj:
                select.append(selected_link_obj)
    
        print(f"Selected {len(select)} relevant links")
        return {"selected_links": select}
            
    except Exception as e:
        return {"error": f"Filtering failed: {str(e)}"}

def analyze_monitor_node(state: MonitorState):
    print("--- Analyzing monitor content ---")
    urls = state.get('selected_links', [])
    
    if not urls:
        print("No URLs selected to analyze")
        return {"analysis_results": []}

    existing_events = load_events()
    existing_urls = {event.url for event in existing_events}
    
    new_urls = [u for u in urls if u["url"] not in existing_urls]
    
    if not new_urls:
         print("All URLs already analyzed.")
         return {"analysis_results": []}

    resultList = []
    
    use_proxy = os.getenv("USE_PROXY", "0") == "1"
    proxy_url = os.getenv("PROXY_URL", "http://127.0.0.1:7890")
    
    if use_proxy:
        transport = httpx.HTTPTransport(proxy=proxy_url)
        client = httpx.Client(transport=transport)
    else:
        client = httpx.Client()

    llm = ChatGoogleGenerativeAI(
            model=model,
            api_key=api_key,
            temperature=0,
            client=client 
    )
    
    parser = JsonOutputParser(pydantic_object=Analysis)
    
    prompt = ChatPromptTemplate.from_template(
        """
        Analyze the following article for AI Security details.
        
        Article Content:
        {content}
        
        Return a JSON object matching Analysis schema.
        IMPORTANT: Start with the field "sentiment" which should be "Critical", "Negative", "Neutral", "Positive".
        - Critical/Negative: Attacks, vulnerabilities, threats found.
        - Neutral: Research without immediate threat, or general discussion.
        - Positive: Defenses, fixes, improvements.
        
        Schema:
        {{
            "sentiment": "Critical/Negative/Neutral/Positive",
            "summary": "Brief summary",
            "attack_vectors": ["List..."],
            "vulnerabilities": ["List..."],
            "affected_components": ["List..."],
            "impact_level": "Critical/High/Medium/Low",
            "technical_details": "Details...",
            "published_date": "YYYY-MM-DD"
        }}
        """
    )
    
    chain = prompt | llm | parser

    for u in new_urls:
        content = fetch_page_content(u["url"])
        if not content: continue
        
        try:
            analysis_data = chain.invoke({"content": content})
            analysis = Analysis(**analysis_data)
            
            event = Event(
                title=u['text'],
                url=u['url'],
                source_website_id="monitor-" + state['source_url'], # Virtual ID
                analysis=analysis,
                scan_date=datetime.now(),
                raw_content_snippet=content[:500] + "..."
            )
            resultList.append(event)
            print(f"Analyzed {u['url']}: {analysis.sentiment} \n {analysis} \n")
            
        except Exception as e:
            print(f"Failed to analyze {u['url']}: {e}")
            
    return {"analysis_results": resultList}

def save_monitor_result_node(state: MonitorState):
    events = state.get("analysis_results", [])
    if events:
        print(f"Saving {len(events)} new events")
        existing = load_events()
        existing.extend(events)
        save_events(existing)
    return {}

# --- Graph ---
def build_monitor_graph():
    workflow = StateGraph(MonitorState)
    
    workflow.add_node("find_latest_issue", find_latest_issue_node)
    workflow.add_node("fetch_newsletter_links", fetch_newsletter_links_node)
    workflow.add_node("filter_monitor_links", filter_monitor_links_node)
    workflow.add_node("analyze_monitor", analyze_monitor_node)
    workflow.add_node("save_monitor_result", save_monitor_result_node)
    
    workflow.set_entry_point("find_latest_issue")
    
    workflow.add_edge("find_latest_issue", "fetch_newsletter_links")
    workflow.add_edge("fetch_newsletter_links", "filter_monitor_links")
    workflow.add_edge("filter_monitor_links", "analyze_monitor")
    workflow.add_edge("analyze_monitor", "save_monitor_result")
    workflow.add_edge("save_monitor_result", END)
    
    return workflow.compile()

monitor_graph = build_monitor_graph()

def generate_daily_summary_report():
    print("--- Generating Daily Summary ---")
    events = load_events()
    
    # Filter for today's events
    today = datetime.now().date()
    today_events = [e for e in events if e.scan_date.date() == today]
    
    if not today_events:
        return "No events found for today."
        
    # Group by impact or sentiment
    summary_text = f"Daily AI Security Summary for {today}\\n\\n"
    summary_text += f"Total Events: {len(today_events)}\\n\\n"
    
    for e in today_events:
        sent = e.analysis.sentiment if hasattr(e.analysis, 'sentiment') else 'N/A'
        summary_text += f"- [{sent}] {e.title} ({e.analysis.impact_level})\\n"
        summary_text += f"  {e.analysis.summary}\\n"
        summary_text += f"  Link: {e.url}\\n\\n"
        
    return summary_text
