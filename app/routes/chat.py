import asyncio
import json
import logging
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from app.config import Settings, get_settings
from app.groq_client import get_groq_client
from app.schemas import ChatRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sse", tags=["sse"])

SSE_HEADERS = {
    "Cache-Control": "no-cache, no-transform",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",  # disable nginx buffering
}


def sse(data: str, event: str | None = None) -> str:
    """Format one SSE frame. Every line of data needs its own `data:` prefix."""
    lines = [f"event: {event}"] if event else []
    lines += [f"data: {line}" for line in data.split("\n")]
    return "\n".join(lines) + "\n\n"


async def groq_event_stream(
    body: ChatRequest, request: Request, settings: Settings
) -> AsyncGenerator[str, None]:
    client = get_groq_client()
    yield sse(json.dumps({"model": settings.groq_model}), event="start")

    try:
        stream = await client.chat.completions.create(
            model=settings.groq_model,
            messages=body.messages,
            temperature=body.temperature,
            max_tokens=body.max_tokens,
            stream=True,
        )

        async for chunk in stream:
            if await request.is_disconnected():
                logger.info("client disconnected, aborting stream")
                break

            delta = chunk.choices[0].delta.content if chunk.choices else None
            if delta:
                yield sse(json.dumps({"delta": delta}), event="token")

    except asyncio.CancelledError:
        logger.info("stream cancelled")
        raise
    except Exception as exc:  # noqa: BLE001
        logger.exception("groq stream failed")
        yield sse(json.dumps({"message": str(exc)}), event="error")
    finally:
        yield sse("[DONE]", event="done")


@router.post("/chat")
async def chat_sse(
    body: ChatRequest,
    request: Request,
    settings: Settings = Depends(get_settings),
) -> StreamingResponse:
    return StreamingResponse(
        groq_event_stream(body, request, settings),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )


@router.get("/chat")
async def chat_sse_get(
    prompt: str,
    request: Request,
    settings: Settings = Depends(get_settings),
) -> StreamingResponse:
    """GET variant so the native browser `EventSource` API can be used."""
    return StreamingResponse(
        groq_event_stream(ChatRequest(prompt=prompt), request, settings),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )