import os

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI

endpoint = os.getenv(
    "AZURE_OPENAI_ENDPOINT",
    "https://foundry-agentic-ai-us2094b-dev.openai.azure.com/",
)

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default",
)

client = AzureOpenAI(
    azure_endpoint=endpoint,
    azure_ad_token_provider=token_provider,
    api_version="2024-10-21",
)

response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {
            "role": "user",
            "content": "Explain Kubernetes CrashLoopBackOff in one sentence.",
        }
    ],
    max_tokens=100,
)

print(response.choices[0].message.content)
