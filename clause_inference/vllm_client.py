"""
VLLM Client - LLM Call Module

Uses text-only LLM calls.
"""

import asyncio
import json
from typing import List, Dict, Optional
from openai import AsyncOpenAI


def load_prompt(prompt_path: str) -> str:
    """Load prompt from file"""
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


# ============================================================================
# Qwen3.5 recommended decoding settings (fixed by design; see Qwen docs).
# Only `seed` is varied across runs to average sampling variance.
# ============================================================================
QWEN_TEMPERATURE = 1.0
QWEN_TOP_P = 0.95
QWEN_TOP_K = 20
QWEN_MAX_TOKENS = 60000
QWEN_PRESENCE_PENALTY = 1.5  # thinking mode only


# ============================================================================
# VLLMClient Class
# ============================================================================

class VLLMClient:
    """
    VLM/LLM asynchronous call client
    
    Args:
        api_url: VLLM API server URL
        api_key: API key
        model_name: Default model name (default: qwen3.5_397b_a17b)
    """
    
    def __init__(
        self,
        api_url: str = "http://localhost:8000/v1",
        api_key: str = "",
        model_name: str = "qwen3.5_9b",
        enable_thinking: bool = False
    ):
        self.api_url = api_url
        self.api_key = api_key
        self.model_name = model_name
        self.enable_thinking = enable_thinking
        self.client: Optional[AsyncOpenAI] = None
    
    async def __aenter__(self):
        import httpx
        # Set timeout (for thinking mode - needs longer time)
        timeout = httpx.Timeout(120.0, connect=30.0)
        self.client = AsyncOpenAI(
            base_url=self.api_url,
            api_key=self.api_key,
            http_client=httpx.AsyncClient(timeout=timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.close()
    
    async def call(
        self,
        prompt: str,
        system_prompt: str = "",
        model: Optional[str] = None,
        seed: int = 0,
        enable_thinking: Optional[bool] = None
    ) -> Dict:
        """
        Call LLM - basically asynchronous.

        Decoding parameters (temperature, top_p, top_k, max_tokens) are fixed to
        the Qwen3.5 recommended settings by design; see the QWEN_* constants.
        Only `seed` is variable, so multiple runs can be averaged by changing it.

        Args:
            prompt: User prompt
            system_prompt: System prompt
            model: Model name (use default if None)
            seed: Sampling seed (vary across runs to average sampling variance)
            enable_thinking: Override instance thinking mode (use default if None)

        Returns:
            Model response (dict)
        """
        model = model or self.model_name

        # Determine enable_thinking: argument > instance default
        enable_thinking = enable_thinking if enable_thinking is not None else self.enable_thinking

        return await self._call_llm(
            prompt=prompt,
            system_prompt=system_prompt,
            model=model,
            seed=seed,
            enable_thinking=enable_thinking
        )
    
    async def _call_llm(
        self,
        prompt: str,
        system_prompt: str,
        model: str,
        seed: int,
        enable_thinking: bool = False
    ) -> Dict:
        """Call LLM (text only).

        temperature / top_p / top_k / max_tokens are fixed to the Qwen3.5
        recommended decoding settings (QWEN_* constants); only `seed` varies.
        """
        # Process system prompt
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({
            "role": "user",
            "content": prompt
        })

        # Qwen3.5 recommended decoding settings, fixed by design.
        common_params = dict(
            model=model,
            messages=messages,
            temperature=QWEN_TEMPERATURE,
            top_p=QWEN_TOP_P,
            max_tokens=QWEN_MAX_TOKENS,
            seed=seed,
        )
        if not enable_thinking:
            resp = await self.client.chat.completions.create(
                **common_params,
                extra_body={"top_k": QWEN_TOP_K, "chat_template_kwargs": {"enable_thinking": enable_thinking}}
            )
        else:
            resp = await self.client.chat.completions.create(
                **common_params,
                presence_penalty=QWEN_PRESENCE_PENALTY,
                extra_body={"top_k": QWEN_TOP_K}
            )
        
        result_content = resp.choices[0].message.content
        
        # Extract reasoning content (thinking/reasoning part)
        raw_reasoning = ""
        if hasattr(resp.choices[0].message, 'reasoning_content') and resp.choices[0].message.reasoning_content:
            raw_reasoning = resp.choices[0].message.reasoning_content
        
        # raw_response includes reasoning_content for debugging
        raw_response = result_content if result_content else (raw_reasoning if raw_reasoning else "")
        
        # If content is None, try to extract JSON from reasoning_content
        if not result_content and raw_reasoning:
            result_content = raw_reasoning
        
        # Try JSON parsing
        if result_content:
            try:
                # Remove markdown code blocks
                cleaned = result_content.replace("```json", "").replace("```", "")
                result_json = json.loads(cleaned)
            except json.JSONDecodeError:
                result_json = {"raw_response": result_content}
        else:
            # If both result_content and raw_reasoning are empty
            result_json = {}
        
        return {
            "result": result_json,
            "raw_response": raw_response,
            "raw_reasoning": raw_reasoning[:500] if raw_reasoning else ""
        }