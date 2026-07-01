import logging
from datetime import datetime, timezone
from tenacity import retry, stop_after_attempt, wait_exponential
from .registry import WeightRegistry
from .config import settings
from .decay import calculate_current_weight
from . import cognee_client

logger = logging.getLogger(__name__)

class ConsolidationEngine:
    def __init__(self, registry: WeightRegistry):
        self.registry = registry

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def _forget_with_retry(self, node_id: str):
        """Attempts to remove memory from cognee with exponential backoff."""
        await cognee_client.forget(node_id)

    async def sweep_once(self) -> None:
        """
        Pages through the active registry, evaluates the current weight, 
        and prunes if W_current <= prune_floor.
        """
        logger.info("Starting consolidation sweep...")
        
        batch_size = 100
        offset = 0
        now = datetime.now(timezone.utc)
        
        while True:
            traces = await self.registry.list_active(batch_size=batch_size, offset=offset)
            if not traces:
                break
                
            for trace in traces:
                elapsed_timedelta = now - trace.last_accessed
                elapsed_hours = elapsed_timedelta.total_seconds() / 3600.0
                
                w_current = calculate_current_weight(
                    trace.weight_initial, 
                    trace.decay_rate, 
                    elapsed_hours
                )
                
                if w_current <= settings.prune_floor:
                    # Time to prune
                    if settings.consolidation_dry_run:
                        logger.info(f"[DRY RUN] Would prune node {trace.node_id} (W={w_current:.2f} <= {settings.prune_floor})")
                        continue
                        
                    try:
                        await self._forget_with_retry(trace.node_id)
                        await self.registry.mark_pruned(trace.node_id)
                        logger.info(f"Pruned node {trace.node_id} (W={w_current:.2f} <= {settings.prune_floor})")
                    except Exception as e:
                        # Log error, mark pending, and move on.
                        logger.error(f"Failed to prune node {trace.node_id} in graph: {e}")
                        await self.registry.mark_pending_prune(trace.node_id)
                else:
                    logger.debug(f"Kept node {trace.node_id} (W={w_current:.2f} > {settings.prune_floor})")

            offset += batch_size

        logger.info("Consolidation sweep finished.")
