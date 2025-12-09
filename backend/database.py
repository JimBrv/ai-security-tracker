import json
import os
from typing import List, Dict
from models import Website, Event
from datetime import datetime

DATA_DIR = "data"
WEBSITES_FILE = os.path.join(DATA_DIR, "websites.json")
EVENTS_FILE = os.path.join(DATA_DIR, "events.json")

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

init_db()
