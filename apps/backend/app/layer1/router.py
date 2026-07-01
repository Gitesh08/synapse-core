from fastapi import APIRouter
from app.layer1.schemas import IngestPayload, normalize
from app.layer1.queue import enqueue

router = APIRouter(prefix="/synapse")

@router.post("/ingest", response_model=dict)
async def ingest(payload: IngestPayload):
    # Normalized purely in-memory
    normalized = normalize(payload)
    
    # Enqueued asynchronously without blocking
    await enqueue(normalized)
    
    return {
        "status": "queued",
        "hash": normalized.content_hash,
        "timestamp": normalized.timestamp
    }
