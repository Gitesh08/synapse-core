import os
import json
import logging
import httpx
from pydantic import BaseModel, Field
from app.layer1.schemas import NormalizedPayload

logger = logging.getLogger(__name__)

class ValenceResult(BaseModel):
    valence_score: int = Field(..., description="Valence score from 1 to 5")
    reason: str = Field(..., description="Short justification for the score")

NVIDIA_NIM_API_KEY = os.getenv("NVIDIA_NIM_API_KEY", "")
NIM_API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
# ponytail: Using meta/llama-3.1-8b-instruct as the default Llama 3.1 8B model.
NIM_MODEL = os.getenv("NVIDIA_NIM_MODEL", "meta/llama-3.1-8b-instruct")

SYSTEM_PROMPT = """
You are a memory importance classifier. Your only job is to score how important a piece of text is for an AI agent to remember long-term.

Output ONLY valid JSON: {"valence_score": <int 1-5>, "reason": "<one sentence>"}
No preamble. No markdown. No explanation outside the JSON.

Scoring rubric:
1 = Ephemeral/Junk — typos, filler, greetings, trivial chitchat ("ok", "lol", "the sky is blue")
2 = Session Context — useful only right now, no long-term value ("I am testing this endpoint", "A is the first letter of the alphabet")
3 = General Fact — stable, publicly known fact with some relevance ("Python is a programming language", "Postgres supports JSON columns")
4 = High-Value Memory — personal preference, recurring pattern, or strong opinion ("I prefer Python over JavaScript", "always use async for I/O-bound tasks")
5 = Core Instinct / Absolute Rule — explicit directive, hard constraint, identity-level rule ("ALWAYS use Postgres, NEVER use MongoDB", "My name is Vinay, I am the developer")

Examples:
Input: "ok got it" → {"valence_score": 1, "reason": "Filler acknowledgment with no lasting value."}
Input: "A is the first letter of the alphabet" → {"valence_score": 2, "reason": "Trivial public fact with no agent-specific relevance."}
Input: "Python supports async/await natively" → {"valence_score": 3, "reason": "General programming fact, stable and moderately useful."}
Input: "I love using Python for all backend work" → {"valence_score": 4, "reason": "Strong personal preference that should influence future suggestions."}
Input: "Always use Postgres. Never use MongoDB under any circumstances." → {"valence_score": 5, "reason": "Explicit absolute directive — core rule for this agent."}
"""

async def score_valence(payload: NormalizedPayload) -> ValenceResult:
    """
    Score the valence of the payload using NVIDIA NIM API.
    Retries once on failure, defaulting to valence_score=2 if both attempts fail.
    """
    api_key = os.getenv("NVIDIA_NIM_API_KEY", NVIDIA_NIM_API_KEY)
    if not api_key:
        logger.warning("NVIDIA_NIM_API_KEY not set. Defaulting to valence_score=2.")
        return ValenceResult(valence_score=2, reason="Scoring failed — defaulted to session context")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    body = {
        "model": NIM_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": payload.text}
        ],
        "response_format": {"type": "json_object"}
    }

    async def make_call() -> ValenceResult:
        # ponytail: Using httpx directly to keep dependencies minimal.
        async with httpx.AsyncClient(timeout=15.0) as client:
            print("Sending request to NVIDIA NIM API...")
            response = await client.post(NIM_API_URL, headers=headers, json=body)
            response.raise_for_status()
            res_data = response.json()
            content = res_data["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            
            # Support both new and old keys in case LLM outputs the old ones
            valence_score = int(parsed.get("valence_score", parsed.get("score", 2)))
            # Clamp score between 1 and 5
            valence_score = max(1, min(5, valence_score))
            reason = str(parsed.get("reason", parsed.get("reasoning", "")))
            return ValenceResult(valence_score=valence_score, reason=reason)

    try:
        return await make_call()
    except Exception as e:
        logger.warning(f"First attempt to score valence failed: {e}. Retrying once...")
        try:
            return await make_call()
        except Exception as e2:
            logger.error(f"Second attempt to score valence failed: {e2}. Defaulting to valence_score=2.")
            return ValenceResult(valence_score=2, reason="Scoring failed — defaulted to session context")

