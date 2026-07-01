import os
import asyncio
from pathlib import Path
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# ponytail: Load .env from project root to ensure it is found regardless of uvicorn's starting directory.
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from fastapi import FastAPI
from synapse.core import SynapseEngine
from app.layer1.router import router as layer1_router
from app.layer2.consumer import run_consumer


import logging
import cognee

logger = logging.getLogger(__name__)

background_tasks = set()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Point the client to the locally running or cloud Cognee server if configured
    # ponytail: If COGNEE_BASE_URL/COGNEE_URL is empty or conflicts with our FastAPI port (8000), run Cognee in-process.
    cognee_url = os.getenv("COGNEE_BASE_URL", os.getenv("COGNEE_URL", ""))
    cognee_api_key = os.getenv("COGNEE_API_KEY", "")
    
    # Clean up default placeholder
    if cognee_api_key == "your_cognee_api_key_here":
        cognee_api_key = ""
        
    if cognee_url and cognee_url != "http://localhost:8000" and cognee_url != "http://localhost:8080":
        try:
            await cognee.serve(url=cognee_url, api_key=cognee_api_key)
            logger.info(f"Connected to Cognee server at {cognee_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Cognee server at {cognee_url}: {e}")
    else:
        logger.info("Running Cognee in-process (local database).")



    # Start Layer 2 background consumer
    consumer_task = asyncio.create_task(run_consumer())
    background_tasks.add(consumer_task)
    
    yield
    
    # Graceful shutdown: cancel consumer task and await its termination
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass
    background_tasks.discard(consumer_task)
    
    try:
        await cognee.disconnect()
        logger.info("Disconnected from Cognee server.")
    except Exception as e:
        logger.error(f"Failed to disconnect from Cognee server: {e}")


app = FastAPI(title="Synapse Core API", lifespan=lifespan)
engine = SynapseEngine()

app.include_router(layer1_router)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Synapse Core Backend running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}


