"""Gemini-only configuration using Google's documented compatibility endpoint."""
import os
from openai import OpenAI

DEFAULT_MODEL = 'gemini-3.1-flash-lite'
GEMINI_BASE_URL = 'https://generativelanguage.googleapis.com/v1beta/openai/'


def model_name() -> str:
    return os.getenv('GEMINI_MODEL', '').strip() or DEFAULT_MODEL


def create_client(*, timeout: float = 30, max_retries: int = 1) -> OpenAI:
    key = os.getenv('GEMINI_API_KEY', '').strip()
    if not key:
        raise ValueError('Configure GEMINI_API_KEY no arquivo .env com uma chave do Google AI Studio.')
    return OpenAI(api_key=key, base_url=GEMINI_BASE_URL, timeout=timeout, max_retries=max_retries)
