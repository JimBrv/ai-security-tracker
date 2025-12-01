import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
import httpx
from dotenv import load_dotenv

from models import Website, Event, Analysis
from tools import fetch_page_content, extract_links
from tools import fetch_page_content, extract_links
from database import save_events, load_events, load_websites, save_websites

load_dotenv()
model = os.getenv("GOOGLE_MODEL")
api_key = os.getenv("GOOGLE_API_KEY")


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
    print(f"Found {len(links)} links")
    return {"found_links": links}

def filter_links_node(state: AgentState):
    print("--- Filtering relevant links ---")
    links = state['found_links']
    print(f"Found {len(links)} links")
    #print(links)
    if not links:
        return {"error": "No links found"}

    # Simple heuristic: limit to first 200 links to avoid context overflow
    # it's ok for top10 sites
    links_subset = links[:300]
    
    # Configure proxy for Gemini API based on environment variable
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
        client=client,
        # model="gemini-2.0-flash-001"
        # client_options={
        #     "api_endpoint": "https://api.apiyi.com/v1"
        # }
    )
    
    parser = JsonOutputParser()
    
    prompt = ChatPromptTemplate.from_template(
        """
        You are an AI Security Researcher. Your goal is to identify the single and recent article link from the provided list that discusses a specific AI Security Event, Attack, Vulnerability, or Research.
        
        Focus on:
        - New attack techniques against AI/LLMs， and AI Agents.
        - New vulnerabilities found in AI infrastructure or libraries.
        - AI Security research papers for adversarial ML, attack and vulnerabbilities research.
        - Real-world AI security incidents.
        - Published in last 6 months.
        
        Ignore:
        - General company news or marketing.
        - General company products or solutions.
        - Generic "What is AI" or "What is the AI top threat"  articles.
        - Links to login pages, social media, or homepages, ads.
        - Links to other sites
        
        Links:
        {links}
        
        Return a JSON object array, each array item with a key "selected_url" containing the URL. If nothing is relevant, return null.
        """
    )

    chain = prompt | llm | parser
    
    try:
        result = chain.invoke({"links": links_subset})
        select = []

        if result is None: 
            return {"error": "No relevant articles found"}
        
        for i, l in enumerate(result):
             print(f"{i}. {l['selected_url']}")
             selected_link_obj = next((j for j in links if j['url'] == l['selected_url']), None)
             select.append(selected_link_obj)
    
        return {"selected_link": select}
            
    except Exception as e:
        return {"error": f"Filtering failed: {str(e)}"}

def analyze_article_node(state: AgentState):
    print("--- Analyzing article ---")
    if not state.get('selected_link'):
        return {"error": "No link selected"}
        
    urls = state['selected_link']
    resultList = []
    cnt = 0
    for i, u in enumerate(urls):
        content = fetch_page_content(u["url"])
    
        if not content:
            print("error: null content!")
            return {"error": "Failed to fetch NULL content"}
        
        # Configure proxy for Gemini API based on environment variable
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
            # model="gemini-2.0-flash-001",
            # client_options={
            #     "api_endpoint": "https://api.apiyi.com/v1"
            # }   
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
                "technical_details": "A short paragraph explaining the technical aspect of the attack/finding",
                "published_date": "YYYY-MM-DD"
            }}
            
            IMPORTANT: Ensure 'published_date' is in YYYY-MM-DD format. If the date is not explicitly mentioned, try to infer it from the context or metadata. If absolutely no date can be found, use today's date.
            """
        )
        
        chain = prompt | llm | parser
    
        try:
            analysis_data = chain.invoke({"content": content})
            analysis = Analysis(**analysis_data)
            
            # Create the Event object
            try:
                pub_date = datetime.strptime(analysis.published_date, "%Y-%m-%d") if analysis.published_date else datetime.now()
            except ValueError:
                print(f"Date parse error for {analysis.published_date}, using now()")
                pub_date = datetime.now()

            event = Event(
                title=u['text'],
                url=u['url'],
                source_website_id=state['website'].id,
                analysis=analysis,
                published_at=pub_date,
                raw_content_snippet=content[:500] + "..."
            )

            resultList.append(event)
            print(f"{cnt}.{u['url']} Model Summary: {analysis}")
            cnt=cnt+1
            
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}

    return {"analysis_result": "OK", "final_event": resultList}


def save_result_node(state: AgentState):
    print("--- Saving result ---")
    evList = state.get('final_event')
    existing_events = load_events()

    for i, ev in enumerate(evList):
        # Simple check to avoid duplicates based on URL
        if not any(e.url == ev.url for e in existing_events):
            existing_events.append(ev)
            save_events(existing_events)
        else:
            print("Duplicate event, skipping save.")
            
    # Update website last_scraped_at
    websites = load_websites()
    for w in websites:
        if w.id == state['website'].id:
            w.last_scraped_at = datetime.now()
            print(f"Updated last_scraped_at for {w.name}")
            break
    save_websites(websites)
    
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
