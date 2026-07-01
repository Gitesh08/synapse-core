from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CognitiveTrace(BaseModel):
    """
    CognitiveTrace represents the metadata register for Layer 3.
    """
    node_id: str           # MUST match the Cognee node ID from cognee.remember()
    text: str
    dataset: str = "general"
    valence_score: int     # 2-5 only (score=1 is dropped before reaching here)
    # ponytail: weight_initial=None represents infinite weight (Core Instinct).
    # Using Optional[float] instead of float("inf") because infinity is not JSON-serializable.
    weight_initial: Optional[float] = None
    decay_rate: float
    last_accessed: datetime
    created_at: datetime
    reason: str
