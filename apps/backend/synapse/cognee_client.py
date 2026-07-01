"""
Thin wrapper around cognee API to isolate internal code from signature changes.
"""
import logging
logger = logging.getLogger(__name__)
try:
    import cognee
except ImportError:
    cognee = None

async def remember(text: str, dataset: str = "general") -> str:
    """Wrapper for cognee.remember"""
    return await cognee.remember(text, dataset_name=dataset)

async def recall(query: str, dataset: str = "general", top_k: int = 5) -> list[dict]:
    """Wrapper for cognee.recall"""
    try:
        return await cognee.recall(query, datasets=[dataset])
    except Exception as e:
        logger.warning(f"Cognee recall failed (likely because graph DB is empty/uninitialized): {e}")
        return []

async def improve(node_id: str) -> None:
    """Wrapper for cognee.improve to reinforce a memory."""
    await cognee.improve(node_id)

async def forget(node_id: str) -> None:
    """Wrapper for cognee.forget to prune a memory."""
    await cognee.forget(node_id)
