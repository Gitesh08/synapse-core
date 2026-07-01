import os
import json
import logging
import httpx
import cognee
import uuid
from typing import Any
from datetime import datetime, timezone
from app.layer1.schemas import NormalizedPayload
from app.layer2.valence import ValenceResult
from app.layer2.kinetics import get_kinetic_params
from app.layer2.trace import CognitiveTrace
from app.layer3 import registry

logger = logging.getLogger(__name__)

NVIDIA_NIM_API_KEY = os.getenv("NVIDIA_NIM_API_KEY", "")
NIM_API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
NIM_MODEL = os.getenv("NVIDIA_NIM_MODEL", "meta/llama-3.1-8b-instruct")



async def safe_remember(text: str, metadata: dict) -> Any:
    """
    Call cognee.remember, trying to pass metadata, and falling back on TypeError.
    """
    try:
        # ponytail: Try passing metadata as requested by the spec, but fall back if the local client raises TypeError.
        return await cognee.remember(text, metadata=metadata)
    except TypeError as e:
        if "metadata" in str(e) or "unexpected keyword argument" in str(e).lower():
            logger.warning("cognee.remember does not support 'metadata' in this version. Falling back to simple remember.")
            return await cognee.remember(text)
        raise

async def detect_contradiction(new_text: str, existing_rules: list) -> str | None:
    """
    Detect if the new core rule contradicts any of the existing core rules.
    Returns the node_id/id of the contradicting rule if found, otherwise None.
    """
    if not existing_rules:
        return None

    # ponytail: LLM-based contradiction detection. Fallback to None if API key is missing.
    api_key = os.getenv("NVIDIA_NIM_API_KEY", NVIDIA_NIM_API_KEY)
    if not api_key:
        logger.warning("NVIDIA_NIM_API_KEY not set. Skipping contradiction detection.")
        return None

    rules_data = []
    for rule in existing_rules:
        rule_id = getattr(rule, "id", getattr(rule, "node_id", None))
        rule_text = getattr(rule, "text", getattr(rule, "content", None))
        if not rule_text and hasattr(rule, "dict"):
            rule_dict = rule.dict()
            rule_text = rule_dict.get("text") or rule_dict.get("content")
        if not rule_text and isinstance(rule, dict):
            rule_text = rule.get("text") or rule.get("content")
            rule_id = rule_id or rule.get("id") or rule.get("node_id")

        if rule_text and rule_id:
            rules_data.append({"id": str(rule_id), "text": rule_text})

    if not rules_data:
        return None

    prompt = f"""You are a contradiction detector. Compare the new core rule with the list of existing core rules.
New Core Rule: "{new_text}"

Existing Core Rules:
{json.dumps(rules_data, indent=2)}

Determine if the new core rule directly contradicts any of the existing core rules (e.g., "always use Postgres" contradicts "never use Postgres").
If there is a direct contradiction, return a JSON object with the "contradicting_id" field set to the ID of the contradicting rule.
If there is no contradiction, return a JSON object with the "contradicting_id" field set to null.

Output ONLY valid JSON matching this schema:
{{
  "contradicting_id": "string or null"
}}
"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    body = {
        "model": NIM_MODEL,
        "messages": [
            {"role": "system", "content": "You are a precise contradiction detector. Output only JSON."},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"}
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(NIM_API_URL, headers=headers, json=body)
            response.raise_for_status()
            res_data = response.json()
            content = res_data["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            contradicting_id = parsed.get("contradicting_id")
            if contradicting_id:
                logger.info(f"Contradiction detected: new rule '{new_text}' contradicts existing rule ID '{contradicting_id}'")
                return contradicting_id
    except Exception as e:
        logger.warning(f"Contradiction detection failed: {e}. Falling back to no contradiction.")

    return None

async def route(payload: NormalizedPayload, valence: ValenceResult) -> dict:
    """
    Route the normalized payload to the appropriate storage action in Cognee based on its valence score.
    """
    score = valence.valence_score

    if score == 1:
        logger.info(f"Payload {payload.content_hash} scored 1 (Ephemeral/Junk). Dropping.")
        return {"action": "dropped", "hash": payload.content_hash}

    elif score in (2, 3, 4):
        params = get_kinetic_params(score)
        w_initial = params["w_initial"]
        decay_rate = params["decay_rate"]
        
        logger.info(f"Payload {payload.content_hash} scored {score}. Kinetics: w_initial={w_initial}, decay_rate={decay_rate}")
        
        metadata = {
            "weight": w_initial,
            "decay_rate": decay_rate,
            "last_accessed": payload.timestamp,
            "valence": score,
            "hash": payload.content_hash,
        }
        
        try:
            await safe_remember(payload.text, metadata=metadata)
            node_id = payload.content_hash
        except Exception as e:
            logger.error(f"Cognee remember failed: {e}")
            raise
            
        # Construct and register the Layer 3 trace
        now = datetime.now(timezone.utc)
        trace = CognitiveTrace(
            node_id=node_id,
            text=payload.text,
            dataset="general",
            valence_score=score,
            weight_initial=w_initial,
            decay_rate=decay_rate,
            last_accessed=now,
            created_at=now,
            reason=valence.reason,
        )
        
        try:
            await registry.upsert(trace)
        except Exception as e:
            logger.error(f"Failed to upsert trace to Layer 3 registry: {e}")

        return {
            "action": "stored_context",
            "weight": w_initial,
            "decay_rate": decay_rate,
            "hash": payload.content_hash,
            "node_id": node_id
        }

    elif score == 5:
        logger.info(f"Payload {payload.content_hash} scored 5 (Core Instinct). Storing as core rule.")
        
        # Check for contradicting existing core rules
        old_node_id = None
        try:
            # ponytail: Using query_text instead of query to match cognee.recall's signature.
            # Using query="core rules" as specified in the updated spec.
            existing_rules = await cognee.recall(query_text="core rules", top_k=5)
            old_node_id = await detect_contradiction(payload.text, existing_rules)
            if old_node_id:
                logger.info(f"Forgetting contradicting core rule: {old_node_id}")
                # ponytail: Using forget signature forget(data_id=...)
                await cognee.forget(data_id=old_node_id)
        except Exception as e:
            logger.warning(f"Error checking/forgetting contradicting rules in Cognee: {e}")

        # Store new core rule
        metadata = {
            "weight": None,
            "decay_rate": 0.0,
            "valence": 5,
            "hash": payload.content_hash,
        }
        
        try:
            await safe_remember(payload.text, metadata=metadata)
            node_id = payload.content_hash
            
            # Improve to lock in heavy edge weighting
            logger.info(f"Locking in core rule with improve. Node ID: {node_id}")
            try:
                await cognee.improve(node_id)
            except Exception as e:
                logger.warning(f"Cognee improve failed for core rule (expected if cloud improve is 404): {e}")
        except Exception as e:
            logger.error(f"Cognee remember failed for core rule: {e}")
            raise


        # Construct and register the Layer 3 trace
        now = datetime.now(timezone.utc)
        trace = CognitiveTrace(
            node_id=node_id,
            text=payload.text,
            dataset="general",
            valence_score=5,
            weight_initial=None,   # signals infinite weight to Layer 3
            decay_rate=0.0,
            last_accessed=now,
            created_at=now,
            reason=valence.reason,
        )
        
        try:
            await registry.upsert(trace)
        except Exception as e:
            logger.error(f"Failed to upsert trace to Layer 3 registry: {e}")

        return {
            "action": "stored_core_rule",
            "hash": payload.content_hash,
            "node_id": node_id,
            "replaced": old_node_id
        }

    return {"action": "unknown", "hash": payload.content_hash}
