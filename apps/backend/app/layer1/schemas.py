import hashlib
import time
from pydantic import BaseModel, Field

class IngestPayload(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)

class NormalizedPayload(BaseModel):
    text: str
    timestamp: float
    content_hash: str

def normalize(payload: IngestPayload) -> NormalizedPayload:
    # ponytail: Using simple python string strip. Leading/trailing whitespace is ignored for hash determinism.
    stripped_text = payload.text.strip()
    content_hash = hashlib.sha256(stripped_text.encode("utf-8")).hexdigest()
    timestamp = time.time()
    return NormalizedPayload(
        text=stripped_text,
        timestamp=timestamp,
        content_hash=content_hash
    )
