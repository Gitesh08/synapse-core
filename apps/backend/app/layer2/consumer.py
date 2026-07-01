import asyncio
import logging
from app.layer1.queue import ingestion_queue
from app.layer2.evaluate import evaluate

logger = logging.getLogger(__name__)

async def run_consumer() -> None:
    """
    Continuous background consumer that drains the ingestion_queue and evaluates each payload.
    """
    logger.info("Starting Synapse Layer 2 background consumer...")
    try:
        while True:
            # Wait for a payload to arrive on the queue
            payload = await ingestion_queue.get()
            
            logger.info(f"Consumer popped payload from queue: {payload.content_hash}")
            try:
                # Process payload through Layer 2 pipeline
                await evaluate(payload)
            except Exception as e:
                logger.error(f"Unexpected error in consumer loop during evaluate: {e}", exc_info=True)
            finally:
                # Signal that the queue item is processed
                ingestion_queue.task_done()
                
    except asyncio.CancelledError:
        logger.info("Synapse Layer 2 background consumer task cancelled.")
    except Exception as e:
        logger.critical(f"Synapse Layer 2 background consumer crashed: {e}", exc_info=True)
