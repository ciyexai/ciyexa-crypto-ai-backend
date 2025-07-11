import httpx
from ciyexa_backend.core.config import settings
from ciyexa_backend.utils.logger import get_logger

logger = get_logger(__name__)

class LLMAgentService:
    def __init__(self):
        self.llm_api_url = settings.LLM_API_BASE_URL

    async def get_llm_response(self, prompt: str) -> str:
        """
        Sends a prompt to the external LLM API and returns the response.
        This service acts as a proxy to the Next.js API route that uses the AI SDK.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.llm_api_url,
                    json={"prompt": prompt},
                    timeout=60.0 # Increased timeout for LLM responses
                )
                response.raise_for_status() # Raise an exception for bad status codes
                data = response.json()
                return data.get("response", "No response from LLM.")
        except httpx.RequestError as e:
            logger.error(f"LLM API request failed: {e}")
            return f"Error communicating with LLM service: {e}"
        except httpx.HTTPStatusError as e:
            logger.error(f"LLM API returned error status {e.response.status_code}: {e.response.text}")
            return f"LLM service returned an error: {e.response.text}"
        except Exception as e:
            logger.error(f"An unexpected error occurred in LLMAgentService: {e}")
            return f"An unexpected error occurred: {e}"
