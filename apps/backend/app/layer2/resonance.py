import logging
import cognee
from app.layer1.schemas import NormalizedPayload

logger = logging.getLogger(__name__)

RESONANCE_THRESHOLD = 0.92

async def check_resonance(payload: NormalizedPayload) -> dict | None:
    """
    Checks if the incoming payload text already exists in memory with high similarity.
    If yes, reinforces the memory in Cognee and returns the match.
    If no, returns None.
    """
    try:
        # ponytail: Using query_text as defined in cognee.recall's signature to avoid TypeError.
        results = await cognee.recall(query_text=payload.text, top_k=1)
        if not results:
            return None

        top_result = results[0]
        
        # ponytail: Checking multiple potential score attributes to handle various Cognee return types.
        score = getattr(top_result, "score", None)
        if score is None:
            score = getattr(top_result, "similarity_score", None)
        if score is None and hasattr(top_result, "metadata"):
            score = top_result.metadata.get("score") if isinstance(top_result.metadata, dict) else getattr(top_result.metadata, "score", None)
        if score is None and isinstance(top_result, dict):
            score = top_result.get("score") or top_result.get("similarity_score")
            
        # Default to 0.0 if we couldn't find a score but got a result
        score_val = float(score) if score is not None else 0.0
            
        if score_val > RESONANCE_THRESHOLD:
            node_id = getattr(top_result, "id", getattr(top_result, "node_id", None))
            if node_id is None and isinstance(top_result, dict):
                node_id = top_result.get("id") or top_result.get("node_id")
                
            logger.info(f"Resonance check hit: score={score_val} > {RESONANCE_THRESHOLD}. Reinforcing node {node_id}")
            if node_id:
                try:
                    await cognee.improve(node_id)
                except Exception as e:
                    logger.warning(f"Cognee improve reinforcement failed (expected if cloud improve is 404): {e}")
            
            return {
                "id": str(node_id) if node_id else None,
                "score": score_val,
                "text": getattr(top_result, "text", getattr(top_result, "content", str(top_result)))
            }
            
    except Exception as e:
        logger.error(f"Cognee recall error in check_resonance: {e}. Failing open to scoring.")
        
    return None
