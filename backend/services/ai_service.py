"""
AIService — direct conversion of com.interview.ai.service.AIService.

Wraps the Groq API (OpenAI-compatible chat completions endpoint)
using httpx instead of Spring's RestTemplate.
"""

import logging
import httpx
from config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# Reuse a single httpx client (fixes the "new RestTemplate per call" issue from Java)
_client = httpx.Client(timeout=60.0)


def call_ai(prompt: str) -> str:
    """
    Mirrors AIService.callAI(String prompt).
    Sends a chat completion request to the Groq API and returns the content string.
    """

    api_key = settings.groq_api_key
    api_url = settings.groq_api_url
    model = settings.groq_api_model

    if not api_key or not api_key.strip():
        logger.error("Missing Groq API key. Set GROQ_API_KEY in .env.")
        return "Error calling AI service"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }

    try:
        response = _client.post(api_url, headers=headers, json=body)
        response.raise_for_status()
        response_body = response.json()

        choices = response_body.get("choices")
        if not choices:
            logger.error("No choices in Groq API response")
            return "Error calling AI service"

        message = choices[0].get("message")
        if not message:
            logger.error("No message in choice")
            return "Error calling AI service"

        content = message.get("content")
        if content is None:
            logger.error("No content in Groq API message")
            return "Error calling AI service"

        return str(content).strip()

    except Exception as e:
        logger.error("Error calling Groq AI API: %s", e)
        return "Error calling AI service"
