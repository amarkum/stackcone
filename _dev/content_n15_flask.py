"""Flask lessons 5-15."""
from content_js_sql import M

META = [
    M("flask-config-factory", "flask", "Config Objects and the App Factory", 14, "Beginner", "Split development and production config and construct the app in a factory.", ["Write config classes", "Load from the environment", "Create the app in a factory"]),
    M("flask-auth", "flask", "Authentication with Flask-Login", 16, "Intermediate", "Sessions, password hashes and protecting views with Flask-Login.", ["Hash a password", "Log a user in", "Protect a route"]),
    M("flask-rest-json", "flask", "JSON APIs", 15, "Intermediate", "Build a small JSON API with status codes, error handlers and marshmallow or pydantic.", ["Return JSON", "Validate a body", "Map errors to status codes"]),
    M("flask-errors-logging", "flask", "Error Handlers and Logging", 14, "Intermediate", "Catch 404/500 consistently and log with a request id.", ["Register error handlers", "Log exceptions", "Add a request id"]),
    M("flask-uploads", "flask", "File Uploads and Static Media", 14, "Intermediate", "Accept files safely, store them outside the code tree and serve them in development.", ["Save an upload", "Reject bad types", "Serve media locally"]),
    M("flask-testing", "flask", "Testing Flask Apps", 16, "Intermediate", "pytest, the test client, app context and covering auth and JSON routes.", ["Write a fixture", "Post JSON", "Force a login in tests"]),
    M("flask-security", "flask", "CSRF, XSS and Hardening", 15, "Advanced", "WTF CSRF, escaping, cookies, rate limits and HTTPS.", ["Turn on CSRF", "Set secure cookies", "Rate-limit login"]),
    M("flask-caching-jobs", "flask", "Caching and Background Jobs", 16, "Advanced", "Flask-Caching with Redis and a simple RQ worker for slow work.", ["Cache a view", "Enqueue a job", "Run a worker"]),
    M("flask-cli", "flask", "The Flask CLI and Shell", 12, "Advanced", "Custom flask commands, the shell context and one-off scripts.", ["Add a CLI command", "Expose models to flask shell", "Run a seed script"]),
    M("flask-migrations-advanced", "flask", "Migrations and Schema Changes", 14, "Advanced", "Expand/contract migrations, data migrations and zero-downtime habits.", ["Add a nullable column", "Backfill data", "Drop a column safely"]),
    M("flask-production", "flask", "Production: Gunicorn, Nginx and Docker", 16, "Advanced", "A release checklist: workers, reverse proxy, env vars and health checks.", ["Run gunicorn", "Terminate TLS at Nginx", "Health-check the app"]),
]

CONTENT = {}

CONTENT["flask-config-factory"] = [
    ("p", "A single <code>app.config[\"SECRET_KEY\"] = \"dev\"</code> does not survive contact with production. Config classes plus an application factory give you a test app, a dev app and a prod app from the same code."),
    ("h2", "Config classes"),
    ("code", "python", 'import os\n\nclass Config:\n    SECRET_KEY = os.environ["SECRET_KEY"]\n    SQLALCHEMY_TRACK_MODIFICATIONS = False\n    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///app.db")\n\nclass DevConfig(Config):\n    DEBUG = True\n\nclass TestConfig(Config):\n    TESTING = True\n    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"\n    WTF_CSRF_ENABLED = False\n\nclass ProdConfig(Config):\n    DEBUG = False'),
    ("h2", "The factory"),
    ("code", "python", 'def create_app(config_object=None):\n    app = Flask(__name__)\n    app.config.from_object(config_object or os.environ.get("FLASK_CONFIG", "myapp.config.DevConfig"))\n    db.init_app(app)\n    login_manager.init_app(app)\n    from .blog import bp as blog_bp\n    app.register_blueprint(blog_bp)\n    return app'),
    ("p", "Tests call <code>create_app(TestConfig)</code>. Gunicorn loads <code>wsgi:app</code> where <code>app = create_app(ProdConfig)</code>."),
    ("note", "from_prefixed_env", "Flask can also read <code>FLASK_SECRET_KEY</code> via <code>app.config.from_prefixed_env()</code>. Pick one scheme and stick to it."),
    ("exercise", "Split a hardcoded secret and database URI into <code>DevConfig</code> / <code>ProdConfig</code> and load them from the environment."),
]

CONTENT["flask-auth"] = [
    ("p", "<strong>Flask-Login</strong> remembers the user id in the session. You still hash passwords yourself (or with Werkzeug) and load the user from the database."),
    ("h2", "The user mixin"),
    ("code", "python", 'from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user\nfrom werkzeug.security import generate_password_hash, check_password_hash\n\nlogin_manager = LoginManager()\nlogin_manager.login_view = "auth.login"\n\nclass User(UserMixin, db.Model):\n    id = db.Column(db.Integer, primary_key=True)\n    email = db.Column(db.String(120), unique=True, nullable=False)\n    password_hash = db.Column(db.String(256), nullable=False)\n\n    def set_password(self, password):\n        self.password_hash = generate_password_hash(password)\n\n    def check_password(self, password):\n        return check_password_hash(self.password_hash, password)\n\n@login_manager.user_loader\ndef load_user(user_id):\n    return db.session.get(User, int(user_id))'),
    ("h2", "Login view"),
    ("code", "python", '@bp.route("/login", methods=["GET", "POST"])\ndef login():\n    if request.method == "POST":\n        user = User.query.filter_by(email=request.form["email"]).first()\n        if user and user.check_password(request.form["password"]):\n            login_user(user, remember=True)\n            return redirect(request.args.get("next") or url_for("blog.index"))\n        flash("Invalid email or password.")\n    return render_template("login.html")\n\n@bp.route("/logout")\ndef logout():\n    logout_user()\n    return redirect(url_for("blog.index"))\n\n@bp.route("/private")\n@login_required\ndef private():\n    return f"Hello {current_user.email}"'),
    ("note", "Timing", "Use the same flash message for unknown email and wrong password so you do not leak which accounts exist."),
    ("exercise", "Add register + login using <code>generate_password_hash</code> and protect a <code>/account</code> page with <code>@login_required</code>."),
]

CONTENT["flask-rest-json"] = [
    ("p", "Flask can serve a JSON API. You do the validation and status codes yourself (or with marshmallow / pydantic). FastAPI automates more of this; Flask stays explicit."),
    ("h2", "JSON views"),
    ("code", "python", 'from flask import Blueprint, jsonify, request, abort\n\napi = Blueprint("api", __name__, url_prefix="/api")\n\n@api.route("/tasks", methods=["GET"])\ndef list_tasks():\n    tasks = Task.query.order_by(Task.id).all()\n    return jsonify([{"id": t.id, "title": t.title, "done": t.done} for t in tasks])\n\n@api.route("/tasks", methods=["POST"])\ndef create_task():\n    data = request.get_json(silent=True) or {}\n    title = (data.get("title") or "").strip()\n    if not title:\n        return jsonify(error="title is required"), 400\n    t = Task(title=title)\n    db.session.add(t)\n    db.session.commit()\n    return jsonify(id=t.id, title=t.title, done=t.done), 201'),
    ("h2", "Validation with pydantic"),
    ("code", "python", 'from pydantic import BaseModel, ValidationError, Field\n\nclass TaskIn(BaseModel):\n    title: str = Field(min_length=1, max_length=100)\n    done: bool = False\n\n@api.route("/tasks", methods=["POST"])\ndef create_task():\n    try:\n        body = TaskIn.model_validate(request.get_json())\n    except ValidationError as e:\n        return jsonify(errors=e.errors()), 422\n    ...'),
    ("h2", "Error handler"),
    ("code", "python", '@api.errorhandler(404)\ndef not_found(e):\n    return jsonify(error="Not found"), 404'),
    ("note", "Blueprints", "Keep HTML and JSON on separate blueprints so error handlers can return the right shape."),
    ("exercise", "Add <code>PATCH /api/tasks/&lt;id&gt;</code> that flips <code>done</code> and returns 404 when the row is missing."),
]

CONTENT["flask-errors-logging"] = [
    ("p", "Users should see a clean error page. You should see a stack trace with a request id in the logs."),
    ("h2", "Handlers"),
    ("code", "python", 'import logging\nfrom flask import render_template, jsonify, g\n\nlog = logging.getLogger(__name__)\n\n@app.errorhandler(404)\ndef not_found(e):\n    if request.path.startswith("/api/"):\n        return jsonify(error="Not found"), 404\n    return render_template("404.html"), 404\n\n@app.errorhandler(500)\ndef server_error(e):\n    log.exception("unhandled error request_id=%s", g.get("request_id"))\n    if request.path.startswith("/api/"):\n        return jsonify(error="Internal Server Error"), 500\n    return render_template("500.html"), 500'),
    ("h2", "Request id middleware"),
    ("code", "python", 'import uuid\n\n@app.before_request\ndef stamp_id():\n    g.request_id = request.headers.get("X-Request-Id", uuid.uuid4().hex)\n\n@app.after_request\ndef set_id(response):\n    response.headers["X-Request-Id"] = g.request_id\n    return response'),
    ("p", "Configure logging once in the factory: structured JSON in production, pretty traces in development."),
    ("exercise", "Return JSON 404s under <code>/api/</code> and HTML 404s elsewhere, and include a request id header on every response."),
]

CONTENT["flask-uploads"] = [
    ("p", "Uploads are a common source of bugs and vulnerabilities. Cap size, allow-list extensions, and store files outside the repo with random names."),
    ("h2", "Saving a file"),
    ("code", "python", 'import uuid\nfrom pathlib import Path\nfrom werkzeug.utils import secure_filename\n\nALLOWED = {".png", ".jpg", ".jpeg", ".pdf"}\nMEDIA = Path(app.config["MEDIA_ROOT"])\n\n@app.route("/upload", methods=["POST"])\ndef upload():\n    f = request.files.get("file")\n    if not f or not f.filename:\n        abort(400)\n    ext = Path(f.filename).suffix.lower()\n    if ext not in ALLOWED:\n        abort(415)\n    name = f"{uuid.uuid4().hex}{ext}"\n    dest = MEDIA / name\n    f.save(dest)\n    return {"id": name}'),
    ("code", "python", 'app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024   # 5 MB'),
    ("h2", "Serving in development"),
    ("code", "python", 'from flask import send_from_directory\n\n@app.route("/media/<name>")\ndef media(name):\n    return send_from_directory(app.config["MEDIA_ROOT"], name)'),
    ("p", "In production, put media on object storage (S3) and serve via a CDN. App servers should be stateless."),
    ("note", "secure_filename", "It strips path segments (<code>../../etc/passwd</code>) but also mangled non-ASCII names. A generated uuid is safer as the stored name; keep the original as metadata."),
    ("exercise", "Accept an image upload, reject non-images, and store it under a random filename in <code>MEDIA_ROOT</code>."),
]

CONTENT["flask-testing"] = [
    ("p", "The Flask test client lets you call views without a running server. Combine it with a factory that uses an in-memory database."),
    ("h2", "Fixtures"),
    ("code", "python", 'import pytest\nfrom myapp import create_app\nfrom myapp.extensions import db\nfrom myapp.config import TestConfig\n\n@pytest.fixture\ndef app():\n    app = create_app(TestConfig)\n    with app.app_context():\n        db.create_all()\n        yield app\n        db.session.remove()\n        db.drop_all()\n\n@pytest.fixture\ndef client(app):\n    return app.test_client()'),
    ("h2", "JSON and auth"),
    ("code", "python", 'def test_create_task(client):\n    r = client.post("/api/tasks", json={"title": "write tests"})\n    assert r.status_code == 201\n    assert r.get_json()["title"] == "write tests"\n\ndef test_private_requires_login(client):\n    assert client.get("/account").status_code in (302, 401)\n\ndef test_account_ok(client, app):\n    with app.app_context():\n        u = User(email="ada@example.com")\n        u.set_password("secret-secret")\n        db.session.add(u)\n        db.session.commit()\n    client.post("/login", data={"email": "ada@example.com", "password": "secret-secret"})\n    assert client.get("/account").status_code == 200'),
    ("note", "json vs data", "<code>json=</code> sets the content type and dumps the body. <code>data=</code> is for form posts."),
    ("exercise", "Write tests for 201 on a valid POST, 400 on a missing title, and a 302 when hitting a login-required page anonymous."),
]

CONTENT["flask-security"] = [
    ("p", "Flask does not turn on as many protections as Django by default. You opt in: CSRF, secure cookies, XSS-safe templates (already on), and rate limits."),
    ("h2", "CSRF with Flask-WTF"),
    ("code", "python", 'from flask_wtf import CSRFProtect\ncsrf = CSRFProtect()\ncsrf.init_app(app)\n# In JSON APIs, send the X-CSRFToken header or exempt the blueprint:\n# csrf.exempt(api)'),
    ("code", "html", '<form method="post">{{ csrf_token() }} ... </form>'),
    ("h2", "Cookies"),
    ("code", "python", 'app.config.update(\n    SESSION_COOKIE_SECURE=True,\n    SESSION_COOKIE_HTTPONLY=True,\n    SESSION_COOKIE_SAMESITE="Lax",\n    REMEMBER_COOKIE_SECURE=True,\n)'),
    ("h2", "Rate limiting"),
    ("code", "python", 'from flask_limiter import Limiter\nfrom flask_limiter.util import get_remote_address\nlimiter = Limiter(get_remote_address, app=app, default_limits=["200 per hour"])\n\n@bp.route("/login", methods=["POST"])\n@limiter.limit("5 per minute")\ndef login():\n    ...'),
    ("note", "XSS", "Jinja auto-escapes. <code>|safe</code> is how XSS sneaks back in. Markdown and rich text need a sanitiser (bleach) before they are marked safe."),
    ("exercise", "Enable CSRF on HTML forms, set secure cookie flags, and rate-limit <code>/login</code> to 5 posts per minute."),
]

CONTENT["flask-caching-jobs"] = [
    ("p", "Two levers for slow work: cache the result, or do the work somewhere else."),
    ("h2", "Flask-Caching"),
    ("code", "python", 'from flask_caching import Cache\ncache = Cache(config={"CACHE_TYPE": "RedisCache", "CACHE_REDIS_URL": os.environ["REDIS_URL"]})\ncache.init_app(app)\n\n@app.route("/popular")\n@cache.cached(timeout=60)\ndef popular():\n    return jsonify(Post.query.order_by(Post.views.desc()).limit(10).all())'),
    ("p", "Invalidate on write: <code>cache.delete(\"view/popular\")</code> after a new post. The simple-cache backend is process-local and wrong for gunicorn."),
    ("h2", "RQ"),
    ("code", "python", '# pip install rq redis\nfrom redis import Redis\nfrom rq import Queue\nqueue = Queue(connection=Redis.from_url(os.environ["REDIS_URL"]))\n\ndef send_welcome(email):\n    ...\n\n@app.route("/signup", methods=["POST"])\ndef signup():\n    user = create_user(request.form["email"])\n    queue.enqueue(send_welcome, user.email)\n    return redirect(url_for("index"))'),
    ("code", "bash", "rq worker"),
    ("note", "Idempotency", "Workers retry. A welcome email job should be safe to run twice, or store a \"welcome_sent\" flag."),
    ("exercise", "Cache a list endpoint for 30 seconds and enqueue a function that writes a log line when a user signs up."),
]

CONTENT["flask-cli"] = [
    ("p", "The <code>flask</code> command is the right place for one-off admin tasks: seed data, create an admin, print stats."),
    ("h2", "A custom command"),
    ("code", "python", 'import click\nfrom flask.cli import with_appcontext\n\n@click.command("seed")\n@with_appcontext\ndef seed():\n    if User.query.filter_by(email="ada@example.com").first():\n        click.echo("already seeded")\n        return\n    u = User(email="ada@example.com")\n    u.set_password("change-me")\n    db.session.add(u)\n    db.session.commit()\n    click.echo("seeded ada")\n\ndef create_app():\n    app = Flask(__name__)\n    ...\n    app.cli.add_command(seed)\n    return app'),
    ("code", "bash", "flask --app myapp seed"),
    ("h2", "Shell context"),
    ("code", "python", '@app.shell_context_processor\ndef extras():\n    return {"db": db, "User": User, "Post": Post}\n# flask shell  ->  User.query.count()'),
    ("exercise", "Add a <code>flask users</code> command that prints every user's email."),
]

CONTENT["flask-migrations-advanced"] = [
    ("p", "Alembic (via Flask-Migrate) is how schema changes reach production. The unsafe habit is adding a non-null column with no default to a live table."),
    ("h2", "Expand, then contract"),
    ("ul", [
        "<strong>Expand</strong>: add a nullable column, deploy code that writes to both old and new, backfill.",
        "<strong>Migrate reads</strong>: deploy code that reads the new column.",
        "<strong>Contract</strong>: drop the old column in a later release.",
    ]),
    ("code", "bash", "flask db migrate -m \"add posts.excerpt nullable\"\n# review the generated file, then:\nflask db upgrade"),
    ("h2", "A data migration"),
    ("code", "python", 'def upgrade():\n    op.add_column("post", sa.Column("excerpt", sa.String(200), nullable=True))\n    conn = op.get_bind()\n    conn.execute(sa.text("UPDATE post SET excerpt = substr(body, 1, 160) WHERE excerpt IS NULL"))\n\ndef downgrade():\n    op.drop_column("post", "excerpt")'),
    ("note", "Review generated SQL", "Alembic guesses. It will not rename a column; it will drop and add, destroying data. Edit the script before you apply it."),
    ("exercise", "Write an expand migration that adds nullable <code>Post.published_at</code> and backfills it from <code>created</code>."),
]

CONTENT["flask-production"] = [
    ("p", "The development server is single-process and not hardened. Production is gunicorn, a reverse proxy, and config from the environment."),
    ("h2", "Gunicorn"),
    ("code", "bash", "gunicorn -w 4 -b 0.0.0.0:8000 --access-logfile - --timeout 30 wsgi:app"),
    ("code", "python", '# wsgi.py\nfrom myapp import create_app\nfrom myapp.config import ProdConfig\napp = create_app(ProdConfig)'),
    ("h2", "Docker"),
    ("code", "dockerfile", 'FROM python:3.12-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt\nCOPY . .\nENV FLASK_CONFIG=myapp.config.ProdConfig\nCMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "wsgi:app"]'),
    ("h2", "Release checklist"),
    ("ul", [
        "<code>DEBUG</code> false, strong <code>SECRET_KEY</code> from the environment.",
        "HTTPS at the proxy; <code>PREFERRED_URL_SCHEME = \"https\"</code> and <code>ProxyFix</code> if you are behind one.",
        "Migrate on release, then start workers.",
        "<code>/health</code> that checks the database for the load balancer.",
    ]),
    ("exercise", "Add <code>ProxyFix</code> for a single proxy hop and a <code>/health</code> JSON endpoint that runs <code>SELECT 1</code>."),
    ("solution", "python", 'from werkzeug.middleware.proxy_fix import ProxyFix\napp.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)\n\n@app.get("/health")\ndef health():\n    db.session.execute(db.text("SELECT 1"))\n    return {"status": "ok"}'),
]
