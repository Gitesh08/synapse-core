import logging
from app.layer1.schemas import NormalizedPayload
from app.layer2.resonance import check_resonance
from app.layer2.valence import score_valence
from app.layer2.router_logic import route

logger = logging.getLogger(__name__)

async def evaluate(payload: NormalizedPayload) -> dict:
    """
    Orchestrate the Layer 2 pipeline:
    1. Resonance check: if duplicate found, reinforce and return.
    2. Valence scoring: score payload text from 1-5 using SLM.
    3. Routing: store context/rules or drop based on valence score.
    
    Wrapped in try/except to prevent individual item failures from crashing the consumer loop.
    """
    try:
        logger.info(f"Starting Layer 2 evaluation for payload: {payload.content_hash}")
        
        # 1. Resonance Check
        resonance_match = await check_resonance(payload)
        if resonance_match:
            logger.info(f"Payload {payload.content_hash} reinforced via resonance check.")
            return {
                "action": "reinforced",
                "hash": payload.content_hash,
                "resonance_match": resonance_match
            }
            
        # 2. Valence Scoring
        valence = await score_valence(payload)
        logger.info(f"Payload {payload.content_hash} scored {valence.valence_score}. Reason: {valence.reason}")
        
        # 3. Routing
        routing_result = await route(payload, valence)
        logger.info(f"Payload {payload.content_hash} evaluation complete. Result: {routing_result}")
        return routing_result

        
    except Exception as e:
        logger.error(f"Error evaluating payload {payload.content_hash}: {e}", exc_info=True)
        return {
            "action": "error",
            "hash": payload.content_hash,
            "error": str(e)
        }
