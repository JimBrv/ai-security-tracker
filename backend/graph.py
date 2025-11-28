import os
from typing import List, Optional, Dict, Any
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
import httpx

from models import Website, Event, Analysis
from tools import fetch_page_content, extract_links
from database import save_events, load_events

# --- State Definition ---
class AgentState(TypedDict):
    website: Website
    found_links: List[Dict[str, str]]
    selected_link: Optional[Dict[str, str]]
    article_content: Optional[str]
    analysis_result: Optional[Analysis]
    final_event: Optional[Event]
    error: Optional[str]

# --- Nodes ---

def fetch_links_node(state: AgentState):
    print(f"--- Fetching links from {state['website'].url} ---")
    links = extract_links(state['website'].url)
    return {"found_links": links}

def filter_links_node(state: AgentState):
    print("--- Filtering relevant links ---")
    links = state['found_links']
    if not links:
        return {"error": "No links found"}

    # Simple heuristic: limit to first 30 links to avoid context overflow
    links_subset = links[:30]
    
    # Configure proxy for Gemini API
    proxy_url = "http://127.0.0.1:7890"
    transport = httpx.HTTPTransport(proxy=proxy_url)
    client = httpx.Client(transport=transport)
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp", 
        temperature=0,
        client=client
    )
    
    parser = JsonOutputParser()
    
    prompt = ChatPromptTemplate.from_template(
        """
        You are an AI Security Researcher. Your goal is to identify the SINGLE most relevant and recent article link from the provided list that discusses a specific AI Security Event, Attack, Vulnerability, or Research.
        
        Focus on:
        - New attack techniques against AI/LLMs.
        - Vulnerabilities in AI infrastructure or libraries.
        - Security research papers (adversarial ML, etc.).
        - Real-world AI security incidents.
        
        Ignore:
        - General company news or marketing.
        - Generic "What is AI" articles.
        - Links to login pages, social media, or homepages.
        
        Links:
        {links}
        
        Return a JSON object with a single key "selected_url" containing the full URL of the best match. If nothing is relevant, return null.
        """
    )
    
    chain = prompt | llm | parser
    
    try:
        result = chain.invoke({"links": links_subset})
        selected_url = result.get("selected_url")
        
        if selected_url:
            # Find the original link object to get the text
            selected_link_obj = next((l for l in links if l['url'] == selected_url), None)
            return {"selected_link": selected_link_obj}
        else:
            return {"error": "No relevant articles found"}
            
    except Exception as e:
        return {"error": f"Filtering failed: {str(e)}"}

def analyze_article_node(state: AgentState):
    print("--- Analyzing article ---")
    if not state.get('selected_link'):
        return {"error": "No link selected"}
        
    url = state['selected_link']['url']
    content = fetch_page_content(url)
    
    if not content:
        return {"error": "Failed to fetch content"}
    
    # Configure proxy for Gemini API
    proxy_url = "http://127.0.0.1:7890"
    transport = httpx.HTTPTransport(proxy=proxy_url)
    client = httpx.Client(transport=transport)
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp", 
        temperature=0,
        client=client
    )
    
    parser = JsonOutputParser(pydantic_object=Analysis)
    
    prompt = ChatPromptTemplate.from_template(
        """
        You are an expert AI Security Analyst. Analyze the following article content and extract the security details.
        
        Article Content:
        {content}
        
        Return a JSON object matching this schema:
        {{
            "summary": "Brief summary of the event/research",
            "attack_vectors": ["List of specific attack vectors mentioned"],
            "vulnerabilities": ["List of vulnerabilities or CVEs"],
            "affected_components": ["List of affected libraries, models, or platforms"],
            "impact_level": "Critical/High/Medium/Low",
            "technical_details": "A short paragraph explaining the technical aspect of the attack/finding"
        }}
        """
    )
    
    chain = prompt | llm | parser
    
    try:
        analysis_data = chain.invoke({"content": content})
        analysis = Analysis(**analysis_data)
        
        # Create the Event object
        event = Event(
            title=state['selected_link']['text'],
            url=url,
            source_website_id=state['website'].id,
            analysis=analysis,
            raw_content_snippet=content[:500] + "..."
        )
        
        return {"analysis_result": analysis, "final_event": event}
        
    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}

def save_result_node(state: AgentState):
    print("--- Saving result ---")
    if state.get('final_event'):
        existing_events = load_events()
        # Simple check to avoid duplicates based on URL
        if not any(e.url == state['final_event'].url for e in existing_events):
            existing_events.append(state['final_event'])
            save_events(existing_events)
            return {"final_event": state['final_event']} # Pass through
        else:
             print("Duplicate event, skipping save.")
    return {}

# --- Graph Construction ---

def build_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("fetch_links", fetch_links_node)
    workflow.add_node("filter_links", filter_links_node)
    workflow.add_node("analyze_article", analyze_article_node)
    workflow.add_node("save_result", save_result_node)
    
    workflow.set_entry_point("fetch_links")
    
    workflow.add_edge("fetch_links", "filter_links")
    
    def check_filter(state):
        if state.get("error"):
            return END
        return "analyze_article"
        
    workflow.add_conditional_edges("filter_links", check_filter)
    
    def check_analysis(state):
        if state.get("error"):
            return END
        return "save_result"
        
    workflow.add_conditional_edges("analyze_article", check_analysis)
    
    workflow.add_edge("save_result", END)
    
    return workflow.compile()

app_graph = build_graph()
