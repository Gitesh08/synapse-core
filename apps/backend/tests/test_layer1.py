import pytest
from httpx import ASGITransport, AsyncClient
from app.layer1.queue import ingestion_queue
from app.layer1.schemas import IngestPayload, normalize
from main import app

@pytest.mark.asyncio
async def test_ingest_valid():
    # Clear queue before test
    while not ingestion_queue.empty():
        ingestion_queue.get_nowait()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/synapse/ingest", json={"text": "hello world"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "queued"
    assert "hash" in data
    assert "timestamp" in data
    assert ingestion_queue.qsize() == 1

@pytest.mark.asyncio
async def test_ingest_empty_string():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/synapse/ingest", json={"text": ""})
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_ingest_too_long():
    long_text = "a" * 10001
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/synapse/ingest", json={"text": long_text})
    assert response.status_code == 422

def test_hash_determinism():
    payload1 = IngestPayload(text="  hello world  ")
    payload2 = IngestPayload(text="hello world")
    
    norm1 = normalize(payload1)
    norm2 = normalize(payload2)
    
    assert norm1.content_hash == norm2.content_hash
    assert norm1.text == "hello world"

def test_hash_different():
    payload1 = IngestPayload(text="hello world 1")
    payload2 = IngestPayload(text="hello world 2")
    
    norm1 = normalize(payload1)
    norm2 = normalize(payload2)
    
    assert norm1.content_hash != norm2.content_hash

@pytest.mark.asyncio
async def test_queue_size_increases():
    # Clear queue before test
    while not ingestion_queue.empty():
        ingestion_queue.get_nowait()
        
    initial_size = ingestion_queue.qsize()
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        await ac.post("/synapse/ingest", json={"text": "test queue"})
        
    assert ingestion_queue.qsize() == initial_size + 1
    item = await ingestion_queue.get()
    assert item.text == "test queue"

from packages.shared.synapse.client import SynapseClient

@pytest.mark.asyncio
async def test_synapse_client_ingest():
    # Clear queue before test
    while not ingestion_queue.empty():
        ingestion_queue.get_nowait()
        
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        client = SynapseClient(base_url="http://test")
        await client.client.aclose()  # close the default one
        client.client = ac  # inject the test client
        
        response = await client.ingest("hello from client")
        assert response["status"] == "queued"
        assert "hash" in response
        assert "timestamp" in response
        assert ingestion_queue.qsize() == 1


