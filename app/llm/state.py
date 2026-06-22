"""Global state for LLM services."""

import os

from app.llm.client import LLMClient
from app.llm.core.queue import AnyIOModelQueue
from app.llm.core.router import ModelRouter
from app.llm.providers.gemini.client import GeminiClient
from app.llm.providers.openai.client import OpenAIClient

# 1. Initialize the router
router = ModelRouter()

# 2. Register default clients if environment variables are present
# Gemini
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    router.register_client("gemini", GeminiClient(api_key=gemini_api_key))

# OpenAI
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    router.register_client("openai", OpenAIClient(api_key=openai_api_key))

# OpenRouter
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
if openrouter_api_key:
    router.register_client(
        "openrouter",
        OpenAIClient(
            api_key=openrouter_api_key, base_url="https://openrouter.ai/api/v1"
        ),
    )

# 3. Initialize the queue
queue = AnyIOModelQueue(router=router, max_workers=5)

# 4. Initialize the high-level client
client = LLMClient(router=router, queue=queue)
