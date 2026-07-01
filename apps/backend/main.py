from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from synapse.registry import WeightRegistry
from synapse.retrieval_engine import RetrievalEngine
from synapse.models import RecallRequest
from synapse.testing.fixtures import seed_sample_memories
from typing import List

app = FastAPI(title="Synapse Core API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Synapse Core Backend running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/memories")
async def get_memories():
    """Returns all traces in the registry for the logs dashboard."""
    registry = WeightRegistry()
    await registry.init_db()
    traces = await registry.list_all(batch_size=1000)
    
    # If it's completely empty (first run), insert the mock fixtures so the frontend has something to show!
    if not traces:
        from synapse.models import MemoryTrace
        for t in seed_sample_memories():
            # Convert the raw Layer 2 mock output into our Layer 3 typed model
            mt = MemoryTrace(**t.__dict__)
            await registry.upsert(mt)
        traces = await registry.list_all(batch_size=1000)
        
    # Convert inf to None for JSON compliance
    import math
    response = []
    for t in traces:
        # Depending on Pydantic version, model_dump() or dict() is used
        t_dict = t.model_dump() if hasattr(t, "model_dump") else t.dict()
        if math.isinf(t_dict["weight_initial"]):
            t_dict["weight_initial"] = None
        response.append(t_dict)
        
    return response

@app.post("/api/recall")
async def execute_recall(request: RecallRequest):
    """Executes a Layer 4 recall for the frontend dashboard."""
    registry = WeightRegistry()
    await registry.init_db()
    engine = RetrievalEngine(registry)
    result = await engine.recall(request)
    return result.model_dump() if hasattr(result, "model_dump") else result.dict()
