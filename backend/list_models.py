import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

os.environ["ALL_PROXY"] = "http://127.0.0.1:7890" 

if not api_key:
    print("Error: GOOGLE_API_KEY not found in environment.")
else:
    genai.configure(api_key=api_key, transport="rest")
    try:
        print("Listing available models:")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)
    except Exception as e:
        print(f"Error listing models: {e}")
