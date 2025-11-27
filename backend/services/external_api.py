import httpx

class ExternalApiService:
    async def fetch_data(self, url: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
