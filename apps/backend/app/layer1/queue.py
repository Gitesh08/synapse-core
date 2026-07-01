import asyncio
from app.layer1.schemas import NormalizedPayload

# In-process asyncio Queue
# ponytail: Simple in-memory queue. Upgrade path: swap for Redis Streams or RabbitMQ if persistence/scaling is needed.
ingestion_queue: asyncio.Queue[NormalizedPayload] = asyncio.Queue()

async def enqueue(payload: NormalizedPayload) -> None:
    """
    Enqueue a normalized payload into the ingestion buffer.
    
    This in-memory queue is designed to be swappable for Redis Streams 
    or another external queue/stream broker in the future without 
    changing this function's public signature.
    """
    await ingestion_queue.put(payload)
