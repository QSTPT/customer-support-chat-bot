A minimal, production-shaped **FastAPI** backend that streams a **Groq** LLM response to the client token-by-token over **Server-Sent Events (SSE)**, using the official async `groq` SDK. # FastAPI + Groq SSE Streaming

<img width="92" height="20" alt="Python" src="https://github.com/user-attachments/assets/76cf2d5a-fa0c-4bf5-948f-60dc7ec64c9d" />

FastAPI<svg xmlns="http://www.w3.org/2000/svg" width="102" height="20" role="img" aria-label="FastAPI: 0.115+"><title>FastAPI: 0.115+</title><filter id="blur"><feGaussianBlur stdDeviation="16"/></filter><linearGradient id="s" x2="0" y2="100%"><stop offset="0" stop-color="#bbb" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient><clipPath id="r"><rect width="102" height="20" rx="3"/></clipPath><g clip-path="url(#r)"><rect width="51" height="20" fill="#555"/><rect x="51" width="51" height="20" fill="#009688"/><rect width="102" height="20" fill="url(#s)"/></g><g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" text-rendering="geometricPrecision" font-size="110"><g transform="scale(.1)"><g aria-hidden="true" fill="#010101"><text x="265" y="150" fill-opacity=".8" filter="url(#blur)" textLength="410">FastAPI</text><text x="265" y="150" fill-opacity=".3" textLength="410">FastAPI</text></g><text x="265" y="140" textLength="410">FastAPI</text></g><g transform="scale(.1)"><g aria-hidden="true" fill="#010101"><text x="755" y="150" fill-opacity=".8" filter="url(#blur)" textLength="410">0.115+</text><text x="755" y="150" fill-opacity=".3" textLength="410">0.115+</text></g><text x="755" y="140" textLength="410">0.115+</text></g></g></svg>


Model

---

## Features

- **Real token streaming** — `text/event-stream` response driven by `AsyncGroq` + `async for`, no buffering.
- **Typed SSE events** — `start`, `token`, `error`, `done` so the client always knows the stream state.
- **Fully async** — nothing blocks the event loop; one shared Groq client for the whole process.
- **Disconnect-safe** — the stream aborts as soon as the client goes away, so no tokens are wasted.
- **Config via env** — no secrets in code, validated with `pydantic-settings`.
- **Built-in demo client** — a single `static/index.html` page using the native `EventSource` API.
- **Health endpoint** — `/health` for uptime checks and to confirm the active model.

---

## API

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/health` | Liveness check; returns the active model name. |
| `POST` | `/sse/chat` | Streams a Groq completion. JSON body: `prompt`, `system`, `temperature`, `max_tokens`. |
| `GET` | `/sse/chat?prompt=...` | Same stream, GET variant for the browser's native `EventSource`. |
| `GET` | `/docs` | Auto-generated Swagger UI. |
| `GET` | `/` | Static demo client. |

**Event contract**

```
event: start
data: {"model": "llama-3.3-70b-versatile"}

event: token
data: {"delta": "Hello"}

event: error
data: {"message": "..."}

event: done
data: [DONE]
```

---

## 1. Project structure

```
fastapi-groq-sse/
├── .env                   # your real secrets (never commit)
├── .env.example           # template to copy from
├── .gitignore
├── README.md
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── main.py            # app factory, CORS, lifespan, router wiring
│   ├── config.py          # env-backed Settings (pydantic-settings)
│   ├── groq_client.py     # shared AsyncGroq client + clean shutdown
│   ├── schemas.py         # ChatRequest validation model
│   └── routes/
│       ├── __init__.py
│       ├── health.py      # GET /health
│       └── chat.py        # SSE endpoint + event formatter
└── static/
    └── index.html         # EventSource demo client
```

**What each module owns**

| File | Responsibility |
| --- | --- |
| `app/main.py` | Creates the app, mounts CORS, static files and routers, opens/closes the Groq client. |
| `app/config.py` | Reads and validates `.env`; cached with `lru_cache` so it is parsed once. |
| `app/groq_client.py` | Single lazily-created `AsyncGroq` instance shared across requests. |
| `app/schemas.py` | Request validation and safe defaults for prompt and sampling params. |
| `app/routes/chat.py` | Builds SSE frames and streams Groq deltas to the client. |
| `app/routes/health.py` | Trivial status endpoint. |

---

## 2. Requirements & usage

**Prerequisites**

- Python **3.11+** (the code uses `str | None` union syntax)
- A **Groq API key** from console.groq.com/keys
- `pip` and `venv` (or `uv` / `poetry` if you prefer)

**`requirements.txt`**

```
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
groq>=0.11.0
pydantic>=2.7.0
pydantic-settings>=2.3.0
python-dotenv>=1.0.1
```

| Package | Why it is needed |
| --- | --- |
| `fastapi` | Web framework, routing, `StreamingResponse`, OpenAPI docs. |
| `uvicorn[standard]` | ASGI server. The `[standard]` extra adds `uvloop`  • `httptools` for faster streaming. |
| `groq` | Official Groq SDK; provides the async streaming client. |
| `pydantic` | Request validation models. |
| `pydantic-settings` | Loads and validates settings from `.env`. |
| `python-dotenv` | Reads the `.env` file. |

**Install**

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Environment variables**

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `GROQ_API_KEY` | Yes | — | Your Groq API key. The app fails fast on startup if missing. |
| `GROQ_MODEL` | No | `llama-3.3-70b-versatile` | Any Groq-hosted chat model ID. |
| `CORS_ORIGINS` | No | `*` | Comma-separated allowed origins, e.g. `http://localhost:5173`. |

---

## 3. Important notes before running

<aside>
⚠️

Read these first — each one has caused a "why isn't it streaming?" moment for someone.

</aside>

1. **Create your `.env` first.** Copy `.env.example` to `.env` and paste a real `GROQ_API_KEY`. The app deliberately fails at startup rather than at first request if the key is missing.
2. **Never commit `.env`.** Make sure `.gitignore` contains `.env`, `.venv/`, and `__pycache__/`. If a key ever leaks, rotate it in the Groq console immediately.
3. **Python 3.11 or newer.** Older versions will raise a `TypeError` on the `X | None` annotations.
4. **Route order matters.** `app.mount("/", StaticFiles(...))` must be registered **after** the routers, otherwise the static mount shadows `/health` and `/sse/chat`.
5. **Don't disable streaming accidentally.** Any middleware that reads or rewrites the full response body (gzip, some logging middleware) will buffer SSE and break token-by-token delivery. Exclude the SSE route from such middleware.
6. **Behind a reverse proxy**, disable buffering or nothing arrives until the stream ends:
    
    ```
    location /sse/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 3600s;
    }
    ```
    
7. **Use `curl -N`** when testing from the terminal. Without `-N`, curl buffers output and the stream looks frozen.
8. **Set CORS properly** if your frontend runs on a different origin (e.g. Vite on `:5173`). A wildcard origin combined with credentials is rejected by browsers.
9. **Watch your rate limits and token budget.** Groq enforces per-model request and token limits; a burst of long streams can hit them quickly.
10. **One worker is enough for local dev.** With `--reload`, don't also pass `--workers`; they conflict.

---

## 4. How to run the project

**Step by step**

```bash
# 1. Clone and enter the project
git clone <your-repo-url> fastapi-groq-sse
cd fastapi-groq-sse

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure secrets
cp .env.example .env             # Windows: copy .env.example .env
# open .env and paste your real GROQ_API_KEY

# 5. Start the dev server
uvicorn app.main:app --reload --port 8000
```

Then open:

- **Demo client** → `http://localhost:8000`
- **Swagger UI** → `http://localhost:8000/docs`

**Verify from the terminal**

```bash
# health check
curl -N http://localhost:8000/health
# => {"status":"ok","model":"llama-3.3-70b-versatile"}

# stream via POST
curl -N -X POST http://localhost:8000/sse/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Explain SSE in one sentence."}'

# stream via GET (EventSource-compatible)
curl -N "http://localhost:8000/sse/chat?prompt=Say%20hello"
```

**Consume from JavaScript**

```jsx
const es = new EventSource("/sse/chat?prompt=Hello");
es.addEventListener("token", (e) => {
  process.stdout.write(JSON.parse(e.data).delta);
});
es.addEventListener("done", () => es.close());
```

**Production-ish run**

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 --proxy-headers
```

**Troubleshooting**

| Symptom | Likely cause |
| --- | --- |
| Everything arrives at once at the end | A proxy or middleware is buffering; see note 6, or you forgot `curl -N`. |
| `ValidationError: groq_api_key` on startup | `.env` missing or the key name is misspelled. |
| `404` on `/health` | The static mount was registered before the routers. |
| CORS error in the browser console | Add your frontend origin to `CORS_ORIGINS`. |
| Stream ends instantly with an `error` event | Invalid API key, unknown model ID, or a Groq rate limit. |

---

## 5. Known limits

- **Stateless — no conversation history.** Every request is a fresh single-turn call. Multi-turn requires adding a `messages` list to `ChatRequest` and storing history somewhere.
- **Native `EventSource` is GET-only**, which caps prompt length at the URL limit (~2–8 KB). Use the POST endpoint with `fetch` + `ReadableStream` (or `@microsoft/fetch-event-source`) for long prompts and custom headers.
- **No authentication or rate limiting.** The endpoint is wide open; add auth and per-user throttling before exposing it publicly.
- **No retry or resume.** If the stream breaks mid-response, the partial output is lost. There is no `Last-Event-ID` / replay support.
- **No persistence.** Nothing is logged or stored — no request history, no token accounting, no analytics.
- **No token/cost tracking.** Usage stats from the final chunk are not captured or exposed.
- **No cancellation endpoint.** Streams stop only when the client disconnects; there is no explicit "cancel job" API.
- **Single-process client.** The shared `AsyncGroq` client is per-worker, so connection pooling doesn't span workers.
- **Long-lived connections need tuning.** Load balancers, proxies, and serverless platforms often cap idle or total connection time; some platforms don't support SSE at all.
- **No tool calling, function calling, or structured output** — plain text deltas only.
- **Errors surface inside the stream**, not as HTTP status codes, since headers are already sent once streaming starts.

---

## 6. Roadmap

<aside>
🛠️

**Prompts will be customized later based on Phase_2.** The current `system` prompt and defaults in `app/schemas.py` are placeholders only — they exist to make the stream testable. The final prompt design, wording, and parameters will be defined and replaced as part of **Phase_2**.

</aside>

Until then, treat these as temporary:

- The default `system` prompt in `ChatRequest`
- `temperature` and `max_tokens` defaults
- The single-message (no history) request shape

---

## License

MIT — use it however you like.
