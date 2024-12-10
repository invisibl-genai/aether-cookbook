import os

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(override=True)

genai.configure(
    api_key=os.getenv("AETHER_API_KEY"),
    transport="rest",
    client_options={"api_endpoint": os.getenv("AETHER_PROXY_ENDPOINT")},
)

prompt = "Hi! Tell me about yourself."


# https://github.com/google-gemini/generative-ai-python/blob/main/samples/text_generation.py
model = genai.GenerativeModel(os.getenv("GOOGLE_PROVIDER_MODEL"))
response = model.generate_content(
    prompt,
    generation_config={"temperature": 1.0},
)
print(response.text)
