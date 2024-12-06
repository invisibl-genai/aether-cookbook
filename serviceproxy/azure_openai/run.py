import os

from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv(override=True)

client = AzureOpenAI(
    api_key=os.getenv("AETHER_API_KEY"),
    azure_endpoint=os.getenv("AETHER_PROXY_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
)

prompt = "Hi! Tell me about yourself."

response = client.chat.completions.create(
    model=os.getenv("AZURE_PROVIDER_MODEL"),
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt},
    ],
)

print(response.choices[0].message.content)
