from urllib.parse import urljoin

import httpx

from tenacity import retry
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_random_exponential

from ice.agents.base import Agent
from ice.settings import settings


class OughtInferenceAgent(Agent):
    def __init__(self, engine: str):
        self.url = urljoin(settings.OUGHT_INFERENCE_URL, engine)

    @retry(wait=wait_random_exponential(), stop=stop_after_attempt(3))
    async def relevance(
        self, *, question, context, verbose=False, default=None
    ) -> float:
        assert settings.OUGHT_INFERENCE_API_KEY, "Ought Inference API key not set"
        async with httpx.AsyncClient() as client:
            client.headers["x-api-key"] = settings.OUGHT_INFERENCE_API_KEY
            response = await client.post(
                self.url, json=dict(query=question, documents=[context])
            )
            response.raise_for_status()
        return response.json()["results"][0]["score"]
