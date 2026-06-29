from fastapi import FastAPI
from synapse.core import SynapseEngine

app = FastAPI(title="Synapse Core API")
engine = SynapseEngine()

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Synapse Core Backend running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
