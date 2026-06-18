"""LLM 客户端：统一 OpenAI 兼容协议。"""

from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

PROVIDERS: dict[str, dict[str, Any]] = {
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o-mini",
    },
    "anthropic": {
        "base_url": "https://api.anthropic.com/v1",
        "default_model": "claude-3-5-haiku-latest",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1",
        "default_model": "deepseek-chat",
    },
}


def get_api_key(provider: str) -> str | None:
    s = get_settings()
    return {
        "openai": s.openai_api_key,
        "anthropic": s.anthropic_api_key,
        "deepseek": s.deepseek_api_key,
    }.get(provider)


def chat_llm(
    messages: list[dict[str, str]],
    provider: str | None = None,
    model: str | None = None,
    temperature: float = 0.7,
) -> str:
    """调用 LLM 返回字符串。"""
    s = get_settings()
    provider = provider or s.default_llm_provider
    api_key = get_api_key(provider)
    if not api_key:
        raise RuntimeError(f"未配置 {provider.upper()}_API_KEY")
    cfg = PROVIDERS[provider]
    model = model or cfg["default_model"]

    if provider == "anthropic":
        return _chat_anthropic(api_key, cfg["base_url"], model, messages, temperature)
    return _chat_openai_compatible(api_key, cfg["base_url"], model, messages, temperature)


def _chat_openai_compatible(
    api_key: str, base_url: str, model: str,
    messages: list[dict], temperature: float,
) -> str:
    url = f"{base_url}/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": messages, "temperature": temperature}
    resp = httpx.post(url, headers=headers, json=payload, timeout=60.0)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _chat_anthropic(
    api_key: str, base_url: str, model: str,
    messages: list[dict], temperature: float,
) -> str:
    url = f"{base_url}/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }
    system = next((m["content"] for m in messages if m["role"] == "system"), None)
    chat_msgs = [m for m in messages if m["role"] != "system"]
    payload: dict[str, Any] = {
        "model": model, "max_tokens": 4096, "messages": chat_msgs, "temperature": temperature,
    }
    if system:
        payload["system"] = system
    resp = httpx.post(url, headers=headers, json=payload, timeout=60.0)
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]


def stream_chat_llm(
    messages: list[dict[str, str]],
    provider: str | None = None,
    model: str | None = None,
    temperature: float = 0.7,
):
    """流式输出。"""
    s = get_settings()
    provider = provider or s.default_llm_provider
    if provider == "anthropic":
        raise NotImplementedError("Anthropic 流式待实现")
    api_key = get_api_key(provider)
    if not api_key:
        raise RuntimeError(f"未配置 {provider.upper()}_API_KEY")
    cfg = PROVIDERS[provider]
    model = model or cfg["default_model"]
    url = f"{cfg['base_url']}/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": messages, "temperature": temperature, "stream": True}
    with httpx.stream("POST", url, headers=headers, json=payload, timeout=60.0) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines():
            if line.startswith("data: "):
                data = line[6:]
                if data.strip() == "[DONE]":
                    break
                try:
                    chunk = json.loads(data)
                    delta = chunk["choices"][0]["delta"].get("content")
                    if delta:
                        yield delta
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue