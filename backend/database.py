import json
import os
from typing import List, Dict, Optional
from models import Website, Event, Prompt
from datetime import datetime

DATA_DIR = "data"
WEBSITES_FILE = os.path.join(DATA_DIR, "websites.json")
EVENTS_FILE = os.path.join(DATA_DIR, "events.json")
PROMPTS_FILE = os.path.join(DATA_DIR, "prompts.json")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

def load_prompts() -> List[Prompt]:
    if not os.path.exists(PROMPTS_FILE):
        return []
    with open(PROMPTS_FILE, "r") as f:
        data = json.load(f)
        return [Prompt(**item) for item in data]

def save_prompts(prompts: List[Prompt]):
    with open(PROMPTS_FILE, "w") as f:
        data = [p.model_dump(mode='json') for p in prompts]
        json.dump(data, f, indent=2)

def get_prompt(name: str) -> Optional[Prompt]:
    prompts = load_prompts()
    return next((p for p in prompts if p.name == name), None)

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

def load_websites() -> List[Website]:
    if not os.path.exists(WEBSITES_FILE):
        return []
    with open(WEBSITES_FILE, "r") as f:
        data = json.load(f)
        return [Website(**item) for item in data]

def save_websites(websites: List[Website]):
    with open(WEBSITES_FILE, "w") as f:
        # Convert datetime objects to string for JSON serialization
        data = [w.model_dump(mode='json') for w in websites]
        json.dump(data, f, indent=2)

def load_events() -> List[Event]:
    if not os.path.exists(EVENTS_FILE):
        return []
    with open(EVENTS_FILE, "r") as f:
        data = json.load(f)
        return [Event(**item) for item in data]

def save_events(events: List[Event]):
    with open(EVENTS_FILE, "w") as f:
        data = [e.model_dump(mode='json') for e in events]
        json.dump(data, f, indent=2)

def init_db():
    # Initialize with the user provided list if empty
    if not os.path.exists(WEBSITES_FILE):
        initial_websites = [
            Website(name="Zenity Blog", url="https://www.zenity.io/blog/", description="Enterprise Agent Security, Copilot, RAG"),
            Website(name="HiddenLayer Research", url="https://hiddenlayer.com/research/", description="Adversarial ML, Model Hijacking"),
            Website(name="Protect AI / Huntr", url="https://www.protectai.com/blog", description="AI Supply Chain Vulnerabilities"),
            Website(name="Wiz Research", url="https://www.wiz.io/blog", description="Cloud AI Infrastructure, Tenant Isolation"),
            Website(name="Enkrypt AI", url="https://www.enkryptai.com/blog", description="LLM Jailbreaking & Red Teaming"),
            Website(name="Huntr.com Feed", url="https://huntr.com/", description="AI Bug Bounty Feed"),
            Website(name="MITRE ATLAS", url="https://atlas.mitre.org/", description="Real-world AI attacks mapped to ATT&CK"),
            Website(name="Hugging Face Security", url="https://huggingface.co/blog/security", description="Malicious Model Scanning"),
            Website(name="Google Project Zero", url="https://googleprojectzero.blogspot.com/", description="Low-level vulnerabilities"),
            Website(name="arXiv (Cryptography and Security)", url="https://arxiv.org/list/cs.CR/recent", description="Academic research on AI security"),
            # New Sources Added
            Website(name="OpenAI Safety", url="https://openai.com/safety", description="Core model safety updates, superalignment"),
            Website(name="Anthropic Research", url="https://www.anthropic.com/research", description="Constitutional AI, mechanistic interpretability"),
            Website(name="Microsoft Security (AI)", url="https://www.microsoft.com/en-us/security/blog/topic/artificial-intelligence/", description="Copilot security, enterprise threat intel"),
            Website(name="Cloudflare AI Blog", url="https://blog.cloudflare.com/tag/ai/", description="AI Gateway security, prompt injection WAF"),
            Website(name="Unit 42 (Palo Alto)", url="https://unit42.paloaltonetworks.com/tag/artificial-intelligence/", description="Wild AI attacks, real-world vulnerabilities"),
            Website(name="Darktrace Blog", url="https://darktrace.com/blog", description="Offensive AI, autonomous response trends"),
            Website(name="Pillar Security", url="https://pillar.security/blog", description="Red Teaming, MLOps security")
        ]
        save_websites(initial_websites)
    
    # Initialize default prompts if not exists
    if not os.path.exists(PROMPTS_FILE):
        default_prompts = [
            Prompt(
                name="filter_links_prompt",
                description="Filters links to identify relevant AI security articles.",
                input_variables=["links"],
                template="""You are an AI Security Researcher. Your goal is to identify the single and recent article link from the provided list that discusses a specific AI Security Event, Attack, Vulnerability, or Research.
        
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
        
        Return a JSON object array, each array item with a key "selected_url" containing the URL. If nothing is relevant, return null."""
            ),
            Prompt(
                name="analyze_article_prompt",
                description="Analyzes article content to extract security details.",
                input_variables=["content"],
                template="""You are an expert AI Security Analyst. Analyze the following article content and extract the security details.
            
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
            
            IMPORTANT: Ensure 'published_date' is in YYYY-MM-DD format. If the date is not explicitly mentioned, try to infer it from the context or metadata. If absolutely no date can be found, use today's date."""
            ),
            Prompt(
                name="monitor_find_latest_issue_prompt",
                 description="Finds the latest newsletter issue link.",
                 input_variables=["links"],
                 template="""You are looking for the link to the *latest* newsletter issue from a list of links found on the archive page.
        
        Links:
        {links}
        
        Return a JSON object with "latest_issue_url". If not found, return null.
        Prefer links that look like dates or "Issue #...".
        """
            ),
            Prompt(
                 name="monitor_filter_links_prompt",
                 description="Filters newsletter links for AI security relevance.",
                 input_variables=["links"],
                 template="""You are an AI Security Watchdog. 
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
            ),
            Prompt(
                name="monitor_analyze_prompt",
                description="Analyzes monitor content for sentiment and security details.",
                input_variables=["content"],
                template="""Analyze the following article for AI Security details.
        
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
        ]
        save_prompts(default_prompts)

init_db()
