"""Express lessons 5-15."""
from content_js_sql import M

META = [
    M("express-validation", "express", "Validation with Zod", 14, "Beginner", "Parse params, query and body with a schema and return 400s that clients can use.", ["Validate a body", "Reuse a schema", "Fail closed on extra fields"]),
    M("express-errors", "express", "Async Errors and Central Handlers", 14, "Intermediate", "Wrap async routes, throw http-errors and keep a single error middleware.", ["Forward async errors", "Throw an HttpError", "Hide 500 details"]),
    M("express-sessions", "express", "Sessions, Cookies and CSRF", 16, "Intermediate", "Server-side sessions vs JWT, cookie flags and CSRF for cookie-based auth.", ["Store a session", "Set cookie flags", "Protect a state-changing route"]),
    M("express-uploads", "express", "File Uploads with Multer", 14, "Intermediate", "Accept multipart files, cap size and write to disk or S3.", ["Use multer", "Limit size and type", "Return a public URL"]),
    M("express-security", "express", "Helmet, CORS and Rate Limits", 15, "Intermediate", "Secure headers, an origin allow-list and brute-force protection on login.", ["Add helmet", "Configure CORS", "Rate-limit /login"]),
    M("express-testing", "express", "Testing with Supertest", 16, "Intermediate", "Hit your app with supertest, isolate the database and assert on status and body.", ["Write a request test", "Reset state between tests", "Test an auth header"]),
    M("express-typescript", "express", "Express with TypeScript", 16, "Intermediate", "Typed Request handlers, a tsconfig that works for Node and extending Express types.", ["Type a handler", "Augment Request", "Run with tsx"]),
    M("express-websockets", "express", "WebSockets", 15, "Advanced", "Upgrade an HTTP server to WebSocket and broadcast with care across processes.", ["Attach a ws server", "Broadcast a message", "Authenticate a socket"]),
    M("express-structure", "express", "Layered Project Structure", 15, "Advanced", "Split routes, services and data access so handlers stay thin.", ["Draw the layers", "Keep SQL out of routes", "Add a request id"]),
    M("express-logging", "express", "Logging and Request Ids", 14, "Advanced", "Structured logs with pino, a request id, and what never to log.", ["Log JSON", "Stamp a request id", "Redact secrets"]),
    M("express-deploy", "express", "Deploy with Docker", 15, "Advanced", "A production Node image, health checks, graceful shutdown and env-based config.", ["Write a Dockerfile", "Handle SIGTERM", "Expose /health"]),
]

CONTENT = {}

CONTENT["express-validation"] = [
    ("p", "Hand-rolled <code>if (!title)</code> checks drift. A schema library such as <strong>zod</strong> parses and types the input, and gives the client a list of field errors."),
    ("h2", "A reusable helper"),
    ("code", "javascript", 'import { z } from "zod";\n\nexport function validate(schema) {\n  return (req, res, next) => {\n    const parsed = schema.safeParse({\n      body: req.body,\n      params: req.params,\n      query: req.query,\n    });\n    if (!parsed.success) {\n      return res.status(400).json({ errors: parsed.error.flatten() });\n    }\n    req.valid = parsed.data;\n    next();\n  };\n}'),
    ("h2", "Using it"),
    ("code", "javascript", 'const CreateTask = z.object({\n  body: z.object({\n    title: z.string().trim().min(1).max(100),\n    done: z.boolean().optional(),\n  }),\n});\n\napp.post("/tasks", validate(CreateTask), (req, res) => {\n  const { title, done = false } = req.valid.body;\n  res.status(201).json({ id: 1, title, done });\n});'),
    ("h2", "Params and query"),
    ("code", "javascript", 'const GetTask = z.object({\n  params: z.object({ id: z.coerce.number().int().positive() }),\n  query: z.object({ include: z.enum(["author"]).optional() }),\n});'),
    ("note", "Unknown keys", "Zod strips unknown keys by default. Use <code>.strict()</code> on the body if you want to 400 on extra fields instead."),
    ("exercise", "Validate <code>POST /users</code> so <code>email</code> is an email and <code>age</code> is an integer 13–120, returning 400 with field errors otherwise."),
]

CONTENT["express-errors"] = [
    ("p", "In Express 4, a rejected promise inside an async handler never reaches your error middleware unless you forward it. One wrapper plus one handler keeps that consistent."),
    ("h2", "Wrap async routes"),
    ("code", "javascript", 'const wrap = (fn) => (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);\n\napp.get("/tasks/:id", wrap(async (req, res) => {\n  const task = await db.task.find(req.params.id);\n  if (!task) {\n    const err = new Error("Task not found");\n    err.status = 404;\n    throw err;\n  }\n  res.json(task);\n}));'),
    ("p", "Express 5 does this for you. Until you are on 5, the wrapper (or <code>express-async-errors</code>) is required."),
    ("h2", "The error middleware"),
    ("code", "javascript", 'app.use((err, req, res, next) => {\n  const status = err.status || 500;\n  if (status >= 500) console.error({ err, requestId: req.requestId });\n  res.status(status).json({\n    error: status >= 500 ? "Internal Server Error" : err.message,\n  });\n});'),
    ("h2", "http-errors"),
    ("code", "javascript", 'import createError from "http-errors";\nthrow createError(409, "Email already registered");'),
    ("note", "Four arguments", "If you omit <code>next</code> in the signature, Express will not treat the function as error middleware. Always write <code>(err, req, res, next)</code>."),
    ("exercise", "Add a wrap helper and an error middleware that returns 404 JSON for not-found and a generic message for 500s."),
]

CONTENT["express-sessions"] = [
    ("p", "JWTs are convenient for APIs. Browser apps often do better with a <strong>server-side session</strong> in a cookie: you can revoke it, and you do not store secrets in localStorage."),
    ("h2", "express-session"),
    ("code", "javascript", 'import session from "express-session";\nimport pgSimple from "connect-pg-simple";\n\nconst PgStore = pgSimple(session);\napp.set("trust proxy", 1);\napp.use(session({\n  store: new PgStore({ pool, tableName: "session" }),\n  secret: process.env.SESSION_SECRET,\n  resave: false,\n  saveUninitialized: false,\n  cookie: { httpOnly: true, secure: true, sameSite: "lax", maxAge: 7 * 24 * 3600 * 1000 },\n}));\n\napp.post("/login", wrap(async (req, res) => {\n  const user = await verify(req.body);\n  req.session.userId = user.id;\n  res.json({ ok: true });\n}));'),
    ("h2", "CSRF for cookie auth"),
    ("p", "A cookie is sent automatically. A malicious site can POST to your API unless you require a CSRF token (double-submit cookie, or <code>SameSite=strict</code> plus a custom header)."),
    ("code", "javascript", 'app.use((req, res, next) => {\n  if (["GET", "HEAD", "OPTIONS"].includes(req.method)) return next();\n  if (req.get("X-Requested-With") !== "XMLHttpRequest") {\n    return res.status(403).json({ error: "CSRF" });\n  }\n  next();\n});'),
    ("note", "JWT vs session", "Mobile clients and other servers still prefer Bearer JWTs. Cookie sessions fit first-party browsers. Do not put a JWT in localStorage on a web app if you can use httpOnly cookies."),
    ("exercise", "Save <code>userId</code> in the session on login and write middleware that 401s when it is missing."),
]

CONTENT["express-uploads"] = [
    ("p", "<strong>Multer</strong> parses <code>multipart/form-data</code>. Combine it with size limits and an allow-list of MIME types."),
    ("h2", "Disk storage"),
    ("code", "javascript", 'import multer from "multer";\nimport { randomUUID } from "node:crypto";\nimport path from "node:path";\n\nconst upload = multer({\n  storage: multer.diskStorage({\n    destination: "uploads/",\n    filename: (_req, file, cb) => cb(null, randomUUID() + path.extname(file.originalname)),\n  }),\n  limits: { fileSize: 5 * 1024 * 1024 },\n  fileFilter: (_req, file, cb) => {\n    cb(null, ["image/jpeg", "image/png", "application/pdf"].includes(file.mimetype));\n  },\n});\n\napp.post("/files", upload.single("file"), (req, res) => {\n  if (!req.file) return res.status(400).json({ error: "file required" });\n  res.status(201).json({ name: req.file.filename, size: req.file.size });\n});'),
    ("p", "On a multi-instance host, disk is the wrong destination. Stream to S3 with <code>@aws-sdk/client-s3</code> and store only the key."),
    ("note", "MIME spoofing", "Browsers set <code>mimetype</code> from the extension. For high-risk uploads, inspect the file header (file-type) after it lands."),
    ("exercise", "Accept a single image under 2 MB, reject other types with 400, and return the generated filename."),
]

CONTENT["express-security"] = [
    ("p", "Three packages cover a surprising amount of production hygiene: Helmet for headers, cors for browsers, express-rate-limit for brute force."),
    ("h2", "Helmet and CORS"),
    ("code", "javascript", 'import helmet from "helmet";\nimport cors from "cors";\n\napp.use(helmet());\napp.use(cors({\n  origin: ["https://app.example.com"],\n  credentials: true,\n  methods: ["GET", "POST", "PATCH", "DELETE"],\n}));'),
    ("h2", "Rate limits"),
    ("code", "javascript", 'import rateLimit from "express-rate-limit";\n\nconst loginLimiter = rateLimit({\n  windowMs: 60_000,\n  limit: 5,\n  standardHeaders: "draft-7",\n  legacyHeaders: false,\n});\napp.post("/login", loginLimiter, loginHandler);\n\napp.use("/api", rateLimit({ windowMs: 60_000, limit: 100 }));'),
    ("h2", "Body size"),
    ("code", "javascript", 'app.use(express.json({ limit: "32kb" }));'),
    ("note", "Trust proxy", "If you are behind Nginx or a load balancer, <code>app.set(\"trust proxy\", 1)</code> so rate limits see the real client IP, not the proxy."),
    ("exercise", "Add Helmet, restrict CORS to one origin, and limit <code>/login</code> to 5 posts per minute."),
]

CONTENT["express-testing"] = [
    ("p", "<strong>Supertest</strong> calls your <code>app</code> without binding a port. Pair it with a test database or an in-memory fake."),
    ("h2", "A first test"),
    ("code", "javascript", 'import request from "supertest";\nimport { app } from "../src/app.js";\n\ntest("GET /health", async () => {\n  const res = await request(app).get("/health");\n  expect(res.status).toBe(200);\n  expect(res.body).toEqual({ status: "ok" });\n});\n\ntest("POST /tasks validates", async () => {\n  const res = await request(app).post("/tasks").send({});\n  expect(res.status).toBe(400);\n});'),
    ("h2", "Auth"),
    ("code", "javascript", 'test("GET /me needs a token", async () => {\n  await request(app).get("/me").expect(401);\n  const { body } = await request(app).post("/login").send({ email: "ada@example.com", password: "secret" });\n  await request(app).get("/me").set("Authorization", `Bearer ${body.token}`).expect(200);\n});'),
    ("p", "Export <code>app</code> without calling <code>listen</code> (do that in <code>server.js</code>). Reset tables in <code>beforeEach</code> or wrap tests in transactions."),
    ("note", "Jest vs node:test", "Node's built-in test runner plus supertest is enough. Jest is fine if your team already uses it."),
    ("exercise", "Write tests for 201 on a valid task POST, 400 on an empty title, and 401 on a protected route without a token."),
]

CONTENT["express-typescript"] = [
    ("p", "TypeScript catches the <code>req.body.title</code> that might be missing. Express types are generic; you extend them for <code>req.user</code>."),
    ("h2", "Setup"),
    ("code", "bash", "npm install express\nnpm install -D typescript @types/express @types/node tsx\nnpx tsc --init"),
    ("code", "javascript", '// tsconfig.json (ideas)\n// { "compilerOptions": { "strict": true, "esModuleInterop": true, "module": "NodeNext" } }'),
    ("h2", "Typed handlers"),
    ("code", "javascript", 'import { Router, type Request, type Response, type NextFunction } from "express";\n\ninterface Authed extends Request {\n  userId?: number;\n}\n\nexport function auth(req: Authed, res: Response, next: NextFunction) {\n  // ...\n  req.userId = 1;\n  next();\n}'),
    ("h2", "Module augmentation"),
    ("code", "javascript", '// types/express.d.ts\ndeclare global {\n  namespace Express {\n    interface Request {\n      userId?: number;\n      requestId: string;\n    }\n  }\n}\nexport {};'),
    ("code", "bash", "npx tsx src/index.ts          # dev\nnpx tsc && node dist/index.js  # prod"),
    ("exercise", "Augment <code>Request</code> with <code>userId</code> and type an <code>auth</code> middleware that sets it."),
]

CONTENT["express-websockets"] = [
    ("p", "WebSockets are an upgrade on the same HTTP server. The <code>ws</code> package is small; Socket.IO adds rooms and fallbacks if you need them."),
    ("h2", "Attach to the HTTP server"),
    ("code", "javascript", 'import http from "node:http";\nimport { WebSocketServer } from "ws";\nimport { app } from "./app.js";\n\nconst server = http.createServer(app);\nconst wss = new WebSocketServer({ server, path: "/ws" });\n\nwss.on("connection", (socket, req) => {\n  socket.on("message", (raw) => {\n    for (const client of wss.clients) {\n      if (client.readyState === 1) client.send(String(raw));\n    }\n  });\n});\n\nserver.listen(3000);'),
    ("h2", "Auth"),
    ("p", "The browser cannot set an <code>Authorization</code> header on the handshake. Send a one-time ticket as a query param, or read the session cookie and verify it on <code>connection</code>."),
    ("note", "Many processes", "Each Node process has its own client set. Pub/sub through Redis when you run more than one replica."),
    ("exercise", "Reject a connection that has no <code>?token=</code> query param, and echo messages only to that socket (not a broadcast)."),
]

CONTENT["express-structure"] = [
    ("p", "A growing Express app becomes unreadable when SQL, validation and HTTP live in one file. A simple layering is enough."),
    ("h2", "Folders"),
    ("code", "text", "src/\n  app.js            # middleware, mounts routers, error handler\n  server.js         # listen\n  routes/tasks.js\n  services/tasks.js # business rules\n  db/tasks.js       # SQL or Prisma\n  middleware/auth.js\n  lib/async.js"),
    ("h2", "Thin handlers"),
    ("code", "javascript", '// routes/tasks.js\nrouter.post("/", validate(CreateTask), wrap(async (req, res) => {\n  const task = await tasksService.create(req.userId, req.valid.body);\n  res.status(201).json(task);\n}));\n\n// services/tasks.js\nexport async function create(userId, input) {\n  return db.tasks.insert({ ...input, userId });\n}'),
    ("p", "Services throw domain errors (<code>err.status = 409</code>); the HTTP layer maps them. Tests can hit services without supertest."),
    ("exercise", "Move a SQL insert out of a route into <code>db/tasks.js</code> and a <code>create</code> function in <code>services/tasks.js</code>."),
]

CONTENT["express-logging"] = [
    ("p", "<code>console.log</code> is not a log pipeline. <strong>Pino</strong> writes JSON, is fast, and works with request ids."),
    ("h2", "Pino HTTP"),
    ("code", "javascript", 'import pino from "pino";\nimport pinoHttp from "pino-http";\nimport { randomUUID } from "node:crypto";\n\nexport const logger = pino({ level: process.env.LOG_LEVEL || "info" });\n\napp.use(pinoHttp({\n  logger,\n  genReqId: (req) => req.headers["x-request-id"] || randomUUID(),\n  customProps: (req) => ({ userId: req.userId }),\n  serializers: {\n    req(req) { return { method: req.method, url: req.url }; },\n  },\n}));'),
    ("h2", "Never log"),
    ("ul", [
        "Passwords, tokens, cookies, full authorization headers.",
        "Entire request bodies that might contain PII.",
        "Stack traces to the client (only to the log).",
    ]),
    ("p", "In development, <code>pino-pretty</code> makes JSON readable. In production, ship JSON to your host's log drain."),
    ("exercise", "Stamp every request with an id (incoming header or a new UUID) and log method, url, status and duration as JSON."),
]

CONTENT["express-deploy"] = [
    ("p", "Node in production is a small Docker image, a health endpoint, and a process that leaves the load balancer before it dies."),
    ("h2", "Dockerfile"),
    ("code", "dockerfile", 'FROM node:22-alpine\nWORKDIR /app\nCOPY package*.json ./\nRUN npm ci --omit=dev\nCOPY . .\nUSER node\nEXPOSE 3000\nCMD ["node", "src/server.js"]'),
    ("h2", "Graceful shutdown"),
    ("code", "javascript", 'const server = app.listen(process.env.PORT || 3000);\n\nfunction shutdown() {\n  server.close(() => process.exit(0));\n  setTimeout(() => process.exit(1), 10_000).unref();\n}\nprocess.on("SIGTERM", shutdown);\nprocess.on("SIGINT", shutdown);'),
    ("h2", "Health"),
    ("code", "javascript", 'app.get("/health", async (_req, res) => {\n  await pool.query("SELECT 1");\n  res.json({ status: "ok" });\n});'),
    ("note", "NODE_ENV", "Set <code>NODE_ENV=production</code> so Express caches templates and dependencies skip dev tools. Read <code>PORT</code> and secrets from the environment."),
    ("exercise", "Add SIGTERM handling that stops accepting connections and a <code>/health</code> that pings the database."),
]
