"""FastAPI lessons 6-15."""
from content_js_sql import M

META = [
    M("fastapi-middleware-cors", "fastapi", "Middleware, CORS and Trusted Hosts", 14, "Intermediate", "Add CORS, HTTPS redirects and request-id middleware without blocking the event loop.", ["Enable CORS", "Add trusted hosts", "Write async middleware"]),
    M("fastapi-auth-oauth2", "fastapi", "OAuth2 and JWT Authentication", 17, "Intermediate", "Password flow, hashed passwords, JWT access tokens and a get_current_user dependency.", ["Hash a password", "Issue a JWT", "Protect a route"]),
    M("fastapi-files-static", "fastapi", "Uploads, Streaming and Static Files", 15, "Intermediate", "Accept files, stream large downloads and mount a static directory.", ["Read an UploadFile", "Stream a response", "Mount StaticFiles"]),
    M("fastapi-testing", "fastapi", "Testing with TestClient", 16, "Intermediate", "pytest fixtures, dependency overrides and asserting on status codes.", ["Override a dependency", "Test auth headers", "Use a test database"]),
    M("fastapi-settings", "fastapi", "Settings with pydantic-settings", 14, "Intermediate", "Load config from the environment, keep secrets out of code and cache settings.", ["Define a Settings class", "Read env vars", "Inject settings with Depends"]),
    M("fastapi-background-ws", "fastapi", "Background Tasks and WebSockets", 16, "Advanced", "Run work after the response and push events over a WebSocket.", ["Add a BackgroundTask", "Accept a WebSocket", "Broadcast a message"]),
    M("fastapi-sqlalchemy-relations", "fastapi", "SQLAlchemy Relationships and Pagination", 16, "Advanced", "One-to-many models, eager loading and page/limit query params.", ["Map a relationship", "Avoid N+1", "Return a page"]),
    M("fastapi-security-headers", "fastapi", "API Security Hardening", 15, "Advanced", "Rate limits, HTTPS, CORS discipline and never leaking stack traces.", ["Rate-limit a route", "Hide details in 500s", "Lock CORS origins"]),
    M("fastapi-openapi", "fastapi", "Custom OpenAPI and Docs", 16, "Advanced", "Tags, examples, description markdown and hiding routes from /docs.", ["Group routes with tags", "Add examples", "Customise the OpenAPI schema"]),
    M("fastapi-production", "fastapi", "Production: Docker and Observability", 16, "Advanced", "Uvicorn workers, health checks, structured logs and tracing.", ["Write a Dockerfile", "Expose /health", "Log request ids"]),
]

CONTENT = {}

CONTENT["fastapi-middleware-cors"] = [
    ("p", "Middleware wraps every request. FastAPI (Starlette) ships CORS, gzip, HTTPS redirect and trusted-host helpers; you can add your own for request ids and timing."),
    ("h2", "CORS"),
    ("p", "A browser on <code>https://app.example.com</code> cannot call <code>https://api.example.com</code> unless the API sends the right headers. Be explicit: <code>[\"*\"]</code> plus cookies is invalid and unsafe."),
    ("code", "python", 'from fastapi.middleware.cors import CORSMiddleware\n\napp.add_middleware(\n    CORSMiddleware,\n    allow_origins=["https://app.example.com"],\n    allow_credentials=True,\n    allow_methods=["GET", "POST", "PATCH", "DELETE"],\n    allow_headers=["Authorization", "Content-Type"],\n)'),
    ("h2", "Trusted hosts and HTTPS"),
    ("code", "python", 'from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware\nfrom fastapi.middleware.trustedhost import TrustedHostMiddleware\n\napp.add_middleware(HTTPSRedirectMiddleware)\napp.add_middleware(TrustedHostMiddleware, allowed_hosts=["api.example.com", "*.example.com"])'),
    ("h2", "Custom middleware"),
    ("code", "python", 'import time, uuid\nfrom starlette.middleware.base import BaseHTTPMiddleware\n\nclass RequestIdMiddleware(BaseHTTPMiddleware):\n    async def dispatch(self, request, call_next):\n        rid = request.headers.get("X-Request-Id", str(uuid.uuid4()))\n        start = time.perf_counter()\n        response = await call_next(request)\n        response.headers["X-Request-Id"] = rid\n        response.headers["X-Process-Ms"] = f"{(time.perf_counter() - start) * 1000:.1f}"\n        return response\n\napp.add_middleware(RequestIdMiddleware)'),
    ("note", "Do not block", "Never run CPU-heavy or synchronous I/O inside middleware. Await async clients, or offload with <code>run_in_threadpool</code>."),
    ("exercise", "Add CORS for <code>http://localhost:5173</code> and middleware that stamps every response with <code>X-Request-Id</code>."),
]

CONTENT["fastapi-auth-oauth2"] = [
    ("p", "The usual API pattern is: register with a hashed password, log in to receive a JWT, send <code>Authorization: Bearer &lt;token&gt;</code> on later requests. FastAPI's OAuth2 helpers generate the docs UI for that flow."),
    ("h2", "Hash passwords"),
    ("code", "python", 'from pwdlib import PasswordHash\n\npwd = PasswordHash.recommended()\n\ndef hash_password(plain: str) -> str:\n    return pwd.hash(plain)\n\ndef verify(plain: str, hashed: str) -> bool:\n    return pwd.verify(plain, hashed)'),
    ("h2", "Issue and read a JWT"),
    ("code", "python", 'from datetime import datetime, timedelta, timezone\nimport jwt\n\nSECRET = "change-me"  # settings.secret_key\nALG = "HS256"\n\ndef create_token(user_id: int) -> str:\n    exp = datetime.now(timezone.utc) + timedelta(minutes=30)\n    return jwt.encode({"sub": str(user_id), "exp": exp}, SECRET, algorithm=ALG)\n\ndef parse_token(token: str) -> int:\n    payload = jwt.decode(token, SECRET, algorithms=[ALG])\n    return int(payload["sub"])'),
    ("h2", "The dependency"),
    ("code", "python", 'from fastapi import Depends, HTTPException\nfrom fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm\n\noauth2 = OAuth2PasswordBearer(tokenUrl="token")\n\ndef get_current_user(token: str = Depends(oauth2), db: Session = Depends(get_db)):\n    try:\n        user_id = parse_token(token)\n    except Exception:\n        raise HTTPException(401, "Invalid token", headers={"WWW-Authenticate": "Bearer"})\n    user = db.get(User, user_id)\n    if not user:\n        raise HTTPException(401, "Invalid token")\n    return user\n\n@app.post("/token")\ndef login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):\n    user = db.query(User).filter(User.email == form.username).first()\n    if not user or not verify(form.password, user.password_hash):\n        raise HTTPException(400, "Incorrect email or password")\n    return {"access_token": create_token(user.id), "token_type": "bearer"}\n\n@app.get("/me")\ndef me(user: User = Depends(get_current_user)):\n    return {"email": user.email}'),
    ("note", "Refresh tokens", "Short-lived access tokens (15–30 min) plus a longer-lived refresh token stored server-side are safer than a one-week JWT the client can keep forever."),
    ("exercise", "Protect <code>GET /me</code> so a missing or bad bearer token returns 401, and a valid token returns the user's email."),
]

CONTENT["fastapi-files-static"] = [
    ("p", "Files are streams, not JSON. FastAPI gives you <code>UploadFile</code> for incoming files, <code>StreamingResponse</code> for outgoing, and <code>StaticFiles</code> for a directory of assets."),
    ("h2", "Uploads"),
    ("code", "python", 'from fastapi import File, UploadFile, HTTPException\nfrom pathlib import Path\n\nUPLOADS = Path("/tmp/uploads")\nUPLOADS.mkdir(exist_ok=True)\nALLOWED = {"image/jpeg", "image/png", "application/pdf"}\n\n@app.post("/files")\nasync def save_file(file: UploadFile = File(...)):\n    if file.content_type not in ALLOWED:\n        raise HTTPException(415, "Unsupported type")\n    dest = UPLOADS / file.filename\n    data = await file.read()\n    if len(data) > 5_000_000:\n        raise HTTPException(413, "Too large")\n    dest.write_bytes(data)\n    return {"name": file.filename, "size": len(data)}'),
    ("h2", "Streaming a download"),
    ("code", "python", 'from fastapi.responses import StreamingResponse\n\n@app.get("/files/{name}")\ndef download(name: str):\n    path = UPLOADS / name\n    if not path.exists():\n        raise HTTPException(404)\n    return StreamingResponse(path.open("rb"), media_type="application/octet-stream",\n                             headers={"Content-Disposition": f\'attachment; filename="{name}"\'})'),
    ("h2", "Static files"),
    ("code", "python", 'from fastapi.staticfiles import StaticFiles\napp.mount("/static", StaticFiles(directory="static"), name="static")'),
    ("note", "Spoofed types", "<code>content_type</code> is client-provided. Check the magic bytes (or a library like python-magic) if the file type matters for security."),
    ("exercise", "Accept a CSV upload, reject anything over 1 MB or not <code>text/csv</code>, and return how many lines it contained."),
]

CONTENT["fastapi-testing"] = [
    ("p", "<code>TestClient</code> runs your app in-process: no real port, real dependency injection, and you can swap the database for a sqlite memory file."),
    ("h2", "A fixture"),
    ("code", "python", 'import pytest\nfrom fastapi.testclient import TestClient\nfrom main import app, get_db\n\n@pytest.fixture\ndef client():\n    def override_db():\n        yield TestingSession()\n    app.dependency_overrides[get_db] = override_db\n    with TestClient(app) as c:\n        yield c\n    app.dependency_overrides.clear()\n\ndef test_health(client):\n    r = client.get("/health")\n    assert r.status_code == 200\n    assert r.json() == {"status": "ok"}'),
    ("h2", "Auth headers"),
    ("code", "python", 'def test_me_requires_token(client):\n    assert client.get("/me").status_code == 401\n\ndef test_me_ok(client):\n    token = client.post("/token", data={"username": "ada@example.com", "password": "secret"}).json()["access_token"]\n    r = client.get("/me", headers={"Authorization": f"Bearer {token}"})\n    assert r.status_code == 200\n    assert r.json()["email"] == "ada@example.com"'),
    ("h2", "Async tests"),
    ("p", "If you need to await inside a test, use <code>httpx.AsyncClient</code> with <code>ASGITransport</code> and <code>pytest-asyncio</code>. For most APIs, the sync <code>TestClient</code> is enough."),
    ("note", "Overrides beat monkeypatch", "Prefer <code>app.dependency_overrides</code> over patching internals. The test then documents the seam your production code already uses."),
    ("exercise", "Write a test that POSTs an invalid body and asserts 422, then a test that POSTs a valid body and asserts 201."),
]

CONTENT["fastapi-settings"] = [
    ("p", "Configuration belongs in the environment. <code>pydantic-settings</code> maps env vars onto a typed class and fails fast if a required secret is missing."),
    ("h2", "A Settings class"),
    ("code", "python", '# pip install pydantic-settings\nfrom functools import lru_cache\nfrom pydantic_settings import BaseSettings, SettingsConfigDict\n\nclass Settings(BaseSettings):\n    model_config = SettingsConfigDict(env_file=".env", extra="ignore")\n    env: str = "dev"\n    database_url: str\n    secret_key: str\n    cors_origins: list[str] = ["http://localhost:5173"]\n\n@lru_cache\ndef get_settings() -> Settings:\n    return Settings()\n\ndef get_db_url(settings: Settings = Depends(get_settings)) -> str:\n    return settings.database_url'),
    ("p", "<code>SECRET_KEY</code> in the environment becomes <code>secret_key</code> on the class. Nested lists can be JSON in the env var."),
    ("h2", "Using it at startup"),
    ("code", "python", 'settings = get_settings()\napp = FastAPI(title="Tasks", debug=settings.env == "dev")'),
    ("note", "Do not print settings", "A debug log of <code>settings.model_dump()</code> will leak the secret key. Log <code>settings.env</code> only."),
    ("exercise", "Add a required <code>database_url</code> and an optional <code>log_level</code> defaulting to <code>INFO</code>, loaded from the environment."),
]

CONTENT["fastapi-background-ws"] = [
    ("p", "Two ways to leave the request/response cycle: run a function after the response is sent, or keep a socket open."),
    ("h2", "BackgroundTasks"),
    ("code", "python", 'from fastapi import BackgroundTasks\n\ndef write_audit(user_id: int, action: str):\n    Path("audit.log").write_text(f"{user_id} {action}\\n", encoding="utf-8")\n\n@app.post("/items")\ndef create(item: ItemIn, bg: BackgroundTasks, user=Depends(get_current_user)):\n    saved = save_item(item)\n    bg.add_task(write_audit, user.id, f"created {saved.id}")\n    return saved'),
    ("p", "These run in the same process. For retries, schedules or work that must survive a restart, use Redis Queue, Celery or a cloud queue instead."),
    ("h2", "WebSockets"),
    ("code", "python", 'from fastapi import WebSocket, WebSocketDisconnect\n\nclients: set[WebSocket] = set()\n\n@app.websocket("/ws")\nasync def ws_endpoint(ws: WebSocket):\n    await ws.accept()\n    clients.add(ws)\n    try:\n        while True:\n            msg = await ws.receive_text()\n            for c in list(clients):\n                await c.send_text(msg)\n    except WebSocketDisconnect:\n        clients.discard(ws)'),
    ("note", "Multiple workers", "An in-memory <code>clients</code> set does not span gunicorn workers. Use Redis pub/sub (or Channel layers) the moment you run more than one process."),
    ("exercise", "Add a background task that writes the new item's id to a log file after <code>POST /items</code> returns 201."),
]

CONTENT["fastapi-sqlalchemy-relations"] = [
    ("p", "Real schemas have relationships. Load them on purpose, and paginate anything that can grow."),
    ("h2", "One-to-many"),
    ("code", "python", 'from sqlalchemy import ForeignKey, String\nfrom sqlalchemy.orm import Mapped, mapped_column, relationship\n\nclass User(Base):\n    __tablename__ = "users"\n    id: Mapped[int] = mapped_column(primary_key=True)\n    email: Mapped[str] = mapped_column(String(120), unique=True)\n    posts: Mapped[list["Post"]] = relationship(back_populates="author")\n\nclass Post(Base):\n    __tablename__ = "posts"\n    id: Mapped[int] = mapped_column(primary_key=True)\n    title: Mapped[str] = mapped_column(String(200))\n    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))\n    author: Mapped[User] = relationship(back_populates="posts")'),
    ("h2", "Eager loading"),
    ("code", "python", 'from sqlalchemy.orm import selectinload\n\nposts = db.scalars(\n    select(Post).options(selectinload(Post.author)).limit(20)\n).all()'),
    ("h2", "Pagination"),
    ("code", "python", 'from fastapi import Query\n\n@app.get("/posts")\ndef list_posts(page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100),\n               db: Session = Depends(get_db)):\n    q = select(Post).order_by(Post.id.desc())\n    total = db.scalar(select(func.count()).select_from(Post))\n    items = db.scalars(q.offset((page - 1) * size).limit(size)).all()\n    return {"total": total, "page": page, "size": size, "items": items}'),
    ("note", "Offset vs cursor", "Large offsets are slow. For feeds, paginate with <code>WHERE id &lt; :last_id ORDER BY id DESC LIMIT n</code>."),
    ("exercise", "Return posts with <code>author.email</code> included, using <code>selectinload</code>, paginated with <code>page</code> and <code>size</code>."),
]

CONTENT["fastapi-security-headers"] = [
    ("p", "An open API on the internet will be scanned within minutes. Rate-limit brute force, do not leak internals, and keep CORS tight."),
    ("h2", "Rate limiting"),
    ("code", "python", '# pip install slowapi\nfrom slowapi import Limiter, _rate_limit_exceeded_handler\nfrom slowapi.util import get_remote_address\nfrom slowapi.errors import RateLimitExceeded\n\nlimiter = Limiter(key_func=get_remote_address)\napp.state.limiter = limiter\napp.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)\n\n@app.post("/token")\n@limiter.limit("5/minute")\ndef login(...):\n    ...'),
    ("h2", "Error responses"),
    ("code", "python", 'from fastapi.responses import JSONResponse\n\n@app.exception_handler(Exception)\nasync def unhandled(request, exc):\n    # log the traceback with the request id, never send it to the client\n    return JSONResponse({"detail": "Internal Server Error"}, status_code=500)'),
    ("h2", "A short checklist"),
    ("ul", [
        "HTTPS only; HSTS at the load balancer.",
        "CORS allow-list of exact origins, not <code>*</code> with credentials.",
        "Validate file types and sizes; store uploads outside the web root.",
        "Least-privilege database role; secrets from the environment.",
        "Dependency updates; pin versions in production.",
    ]),
    ("note", "Verbose 500s", "<code>debug=True</code> in production returns tracebacks in the docs UI and in responses. Keep it off."),
    ("exercise", "Rate-limit <code>/token</code> to 5 requests per minute per IP and return a generic 500 body for unhandled exceptions."),
]

CONTENT["fastapi-openapi"] = [
    ("p", "The automatic docs are a product surface. Tags, summaries and examples make them usable for the next person (including you in six months)."),
    ("h2", "Tags and metadata"),
    ("code", "python", 'app = FastAPI(\n    title="Tasks API",\n    version="1.2.0",\n    description="CRUD for personal tasks. Authenticate via `/token`.",\n    openapi_tags=[\n        {"name": "tasks", "description": "Create and list tasks"},\n        {"name": "auth", "description": "Login and current user"},\n    ],\n)\n\n@app.get("/tasks", tags=["tasks"], summary="List tasks", response_description="A page of tasks")\ndef list_tasks():\n    ...'),
    ("h2", "Examples on models"),
    ("code", "python", 'from pydantic import BaseModel, Field, ConfigDict\n\nclass TaskIn(BaseModel):\n    model_config = ConfigDict(json_schema_extra={\n        "examples": [{"title": "Write tests", "done": False}]\n    })\n    title: str = Field(..., min_length=1, max_length=100, description="Shown in the list")\n    done: bool = False'),
    ("h2", "Hide internal routes"),
    ("code", "python", '@app.get("/internal/metrics", include_in_schema=False)\ndef metrics():\n    return PlainTextResponse("ok")'),
    ("p", "You can also replace the schema entirely with <code>app.openapi = custom_openapi</code> if you need to inject a security scheme globally."),
    ("exercise", "Give the app a title and version, tag auth vs tasks, and hide a <code>/health</code> route from the schema while keeping it callable."),
]

CONTENT["fastapi-production"] = [
    ("p", "Production FastAPI is an ASGI server, several workers, a reverse proxy, and enough observability to debug the next outage."),
    ("h2", "Docker"),
    ("code", "dockerfile", 'FROM python:3.12-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt\nCOPY . .\nEXPOSE 8000\nCMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]'),
    ("p", "For a lot of blocking I/O, more workers help. For a lot of <code>async def</code> waiting on the network, fewer workers and a bigger event loop often win. Measure."),
    ("h2", "Health and readiness"),
    ("code", "python", '@app.get("/health", include_in_schema=False)\ndef health(db: Session = Depends(get_db)):\n    db.execute(text("SELECT 1"))\n    return {"status": "ok"}'),
    ("h2", "Structured logs"),
    ("code", "python", 'import logging, json\n\nclass JsonLog(logging.Formatter):\n    def format(self, rec):\n        return json.dumps({"level": rec.levelname, "msg": rec.getMessage()})\n\nlogging.basicConfig(level="INFO")\nlogging.getLogger().handlers[0].setFormatter(JsonLog())'),
    ("ul", [
        "Put a request id on every log line (middleware).",
        "Do not log tokens, passwords or full request bodies.",
        "Export OpenTelemetry traces if you have more than one service.",
    ]),
    ("note", "Gunicorn", "<code>gunicorn -k uvicorn.workers.UvicornWorker main:app</code> is the same server with gunicorn's process management. Platforms like Cloud Run can just run uvicorn."),
    ("exercise", "Write a Dockerfile that installs deps, copies the app, and starts uvicorn on port 8000, plus a <code>/health</code> endpoint that pings the database."),
]
