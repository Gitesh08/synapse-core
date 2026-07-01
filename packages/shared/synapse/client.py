import httpx

class SynapseClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        # ponytail: keeping AsyncClient instance managed within the client or as a context manager.
        self.client = httpx.AsyncClient(base_url=self.base_url)

    async def ingest(self, text: str) -> dict:
        """
        Ingest a text payload into Synapse.
        """
        response = await self.client.post("/synapse/ingest", json={"text": text})
        response.raise_for_status()
        return response.json()

    async def close(self) -> None:
        """
        Close the underlying HTTP client.
        """
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
