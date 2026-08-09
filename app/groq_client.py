from groq import AsyncGroq

from app.config import get_settings

_client: AsyncGroq | None = None


def get_groq_client() -> AsyncGroq:
    """Lazily create one shared AsyncGroq client for the whole process."""
    global _client
    if _client is None:
        _client = AsyncGroq(api_key=get_settings().groq_api_key)
    return _client


async def close_groq_client() -> None:
    global _client
    if _client is not None:
        await _client.close()
        _client = None