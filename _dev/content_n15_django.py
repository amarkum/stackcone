"""Django lessons 6-15."""
from content_js_sql import M

META = [
    M("django-auth-users", "django", "Users, Login and Permissions", 16, "Intermediate", "Use Django's auth system: login, logout, the User model and object permissions.", ["Log a user in", "Protect a view", "Check permissions"]),
    M("django-class-based-views", "django", "Class-Based Views", 16, "Intermediate", "ListView, DetailView, CreateView and mixins instead of long function views.", ["Write a ListView", "Use a CreateView", "Add a mixin"]),
    M("django-orm-advanced", "django", "The ORM in Depth", 17, "Intermediate", "select_related, aggregations, F expressions, transactions and indexes.", ["Kill N+1 queries", "Aggregate and annotate", "Wrap a transaction"]),
    M("django-middleware-signals", "django", "Middleware, Signals and Settings", 15, "Intermediate", "The request pipeline, decoupling with signals and splitting settings.", ["Write middleware", "Connect a signal", "Split settings modules"]),
    M("django-testing", "django", "Testing Django Apps", 16, "Intermediate", "TestCase, the test client, fixtures and asserting on the database.", ["Write a model test", "Post through the client", "Use a fixture"]),
    M("django-static-media", "django", "Static Files, Media and Caching", 15, "Intermediate", "collectstatic, user uploads, WhiteNoise and the cache framework.", ["Serve static assets", "Save an uploaded file", "Cache a queryset"]),
    M("django-drf-auth", "django", "DRF Auth, Permissions and Pagination", 16, "Advanced", "Token and session auth, permissions, filtering and pagination in DRF.", ["Protect a viewset", "Paginate a list", "Filter with query params"]),
    M("django-sessions-messages", "django", "Sessions, Messages and Email", 14, "Advanced", "Store data per visitor, flash messages and send mail.", ["Use the session", "Flash a message", "Send an email"]),
    M("django-security", "django", "Security Defaults", 15, "Advanced", "CSRF, XSS, SQL injection, HTTPS and the deployment checklist.", ["Explain CSRF", "Lock down HTTPS", "Run the deployment checks"]),
    M("django-deployment", "django", "Deployment with Gunicorn", 16, "Advanced", "Production settings, gunicorn, Nginx, collectstatic and migrations on release.", ["Split prod settings", "Run gunicorn", "Collect static files"]),
]

CONTENT = {}

CONTENT["django-auth-users"] = [
    ("p", "Django ships a complete auth system: a <code>User</code> model, password hashing, login views, groups and permissions. Use it instead of rolling your own."),
    ("h2", "The User model"),
    ("code", "python", 'from django.contrib.auth.models import User\n\nuser = User.objects.create_user(username="ada", email="ada@example.com", password="s3cret-long")\nuser.check_password("s3cret-long")     # True\nuser.is_staff                          # False unless you set it'),
    ("p", "Never set <code>user.password = \"...\"</code> directly. Always <code>create_user</code> / <code>set_password</code> so the value is hashed."),
    ("h2", "Login, logout, and login_required"),
    ("code", "python", '# urls.py\nfrom django.contrib.auth import views as auth_views\nurlpatterns = [\n    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),\n    path("logout/", auth_views.LogoutView.as_view(), name="logout"),\n]\n\n# views.py\nfrom django.contrib.auth.decorators import login_required\n\n@login_required\ndef dashboard(request):\n    return render(request, "dashboard.html", {"user": request.user})'),
    ("h2", "Permissions"),
    ("code", "python", 'from django.contrib.auth.decorators import permission_required\nfrom django.contrib.auth.mixins import UserPassesTestMixin\n\n@permission_required("blog.delete_post")\ndef delete_post(request, pk):\n    ...\n\nclass EditorRequired(UserPassesTestMixin):\n    def test_func(self):\n        return self.request.user.groups.filter(name="editors").exists()'),
    ("note", "Custom user", "If you need extra fields, set <code>AUTH_USER_MODEL</code> to your own model <em>before</em> the first migration. Changing it later is painful."),
    ("exercise", "Protect a <code>/profile</code> view with <code>@login_required</code> and show the logged-in username in the template."),
    ("solution", "python", '@login_required\ndef profile(request):\n    return render(request, "profile.html", {"name": request.user.get_username()})'),
]

CONTENT["django-class-based-views"] = [
    ("p", "Function views are explicit. Class-based views (CBVs) reuse the boring bits: fetch an object, paginate a list, validate a form, redirect on success."),
    ("h2", "List and detail"),
    ("code", "python", 'from django.views.generic import ListView, DetailView\nfrom .models import Post\n\nclass PostList(ListView):\n    model = Post\n    paginate_by = 20\n    queryset = Post.objects.filter(published=True).order_by("-created")\n    context_object_name = "posts"      # otherwise it is object_list\n\nclass PostDetail(DetailView):\n    model = Post\n    slug_field = "slug"'),
    ("h2", "Create, update, delete"),
    ("code", "python", 'from django.contrib.auth.mixins import LoginRequiredMixin\nfrom django.views.generic import CreateView, UpdateView, DeleteView\nfrom django.urls import reverse_lazy\n\nclass PostCreate(LoginRequiredMixin, CreateView):\n    model = Post\n    fields = ["title", "body"]\n    success_url = reverse_lazy("post-list")\n\n    def form_valid(self, form):\n        form.instance.author = self.request.user\n        return super().form_valid(form)'),
    ("h2", "When a function is clearer"),
    ("p", "If you override three methods to fight the CBV, write a function. Mixins shine when you reuse the same access rule across many views."),
    ("note", "as_view()", "URLconfs need <code>PostList.as_view()</code>, not the class itself."),
    ("exercise", "Replace a function that lists published posts with a <code>ListView</code> paginated by 10."),
]

CONTENT["django-orm-advanced"] = [
    ("p", "The ORM will happily issue a query per row if you let it. Production Django is mostly about asking for the right related data, aggregating in the database, and wrapping writes in transactions."),
    ("h2", "select_related and prefetch_related"),
    ("code", "python", '# ForeignKey / OneToOne: JOIN in the same query\nPost.objects.select_related("author").all()\n\n# ManyToMany / reverse FK: a second query, then stitch in Python\nPost.objects.prefetch_related("tags", "comment_set")'),
    ("p", "Looping over <code>post.author.name</code> without <code>select_related</code> is the classic N+1."),
    ("h2", "Aggregate, annotate, F"),
    ("code", "python", 'from django.db.models import Count, F, Q\n\nPost.objects.aggregate(n=Count("id"))\nPost.objects.annotate(n_comments=Count("comment")).filter(n_comments__gt=0)\nPost.objects.filter(Q(title__icontains="django") | Q(body__icontains="orm"))\nProduct.objects.update(price=F("price") * 11 / 10)   # 10% rise in SQL'),
    ("h2", "Transactions"),
    ("code", "python", 'from django.db import transaction\n\n@transaction.atomic\ndef transfer(from_id, to_id, amount):\n    a = Account.objects.select_for_update().get(id=from_id)\n    b = Account.objects.select_for_update().get(id=to_id)\n    a.balance -= amount\n    b.balance += amount\n    a.save()\n    b.save()'),
    ("h2", "Indexes"),
    ("code", "python", 'class Post(models.Model):\n    slug = models.SlugField(unique=True)\n    published = models.BooleanField(db_index=True)\n    class Meta:\n        indexes = [models.Index(fields=["author", "-created"])]'),
    ("note", "exists vs count", "<code>qs.exists()</code> is cheaper than <code>qs.count()</code> when you only need a yes/no, and cheaper still than <code>if qs:</code> which may evaluate the whole queryset."),
    ("exercise", "Write a queryset of posts with their authors that also annotates each post's comment count and excludes posts with zero comments."),
    ("solution", "python", 'Post.objects.select_related("author").annotate(n=Count("comment")).filter(n__gt=0)'),
]

CONTENT["django-middleware-signals"] = [
    ("p", "Every request passes through middleware on the way in and out. Signals let apps react to events (a user saved, a request finished) without importing each other."),
    ("h2", "A small middleware"),
    ("code", "python", '# app/middleware.py\nclass RequestIdMiddleware:\n    def __init__(self, get_response):\n        self.get_response = get_response\n\n    def __call__(self, request):\n        request.request_id = request.headers.get("X-Request-Id", "-")\n        response = self.get_response(request)\n        response["X-Request-Id"] = request.request_id\n        return response'),
    ("p", "Add the dotted path to <code>MIDDLEWARE</code>. Order matters: SecurityMiddleware and SessionMiddleware should stay near the top."),
    ("h2", "Signals"),
    ("code", "python", 'from django.db.models.signals import post_save\nfrom django.dispatch import receiver\nfrom django.contrib.auth.models import User\n\n@receiver(post_save, sender=User)\ndef create_profile(sender, instance, created, **kwargs):\n    if created:\n        Profile.objects.create(user=instance)'),
    ("p", "Register the module in <code>AppConfig.ready()</code> so the receiver is imported once."),
    ("h2", "Settings as a package"),
    ("code", "text", "config/settings/\n  __init__.py      # from .dev import *  (local default)\n  base.py\n  dev.py\n  prod.py"),
    ("code", "python", '# prod.py\nfrom .base import *\nDEBUG = False\nALLOWED_HOSTS = ["www.example.com"]\nSECURE_SSL_REDIRECT = True'),
    ("note", "Signals vs a service function", "If two apps in your project must stay in sync, a function call is easier to debug than a signal. Use signals for optional side effects (analytics, cache bust)."),
    ("exercise", "Write middleware that sets <code>request.is_htmx</code> to True when the <code>HX-Request</code> header is present."),
]

CONTENT["django-testing"] = [
    ("p", "Django's <code>TestCase</code> wraps each test in a transaction, gives you a test client, and creates a throwaway database."),
    ("h2", "Model and view tests"),
    ("code", "python", 'from django.test import TestCase\nfrom django.urls import reverse\nfrom .models import Post\n\nclass PostTests(TestCase):\n    def setUp(self):\n        self.post = Post.objects.create(title="Hello", body="Hi", published=True)\n\n    def test_str(self):\n        self.assertEqual(str(self.post), "Hello")\n\n    def test_list_shows_published(self):\n        res = self.client.get(reverse("post-list"))\n        self.assertContains(res, "Hello")\n        self.assertEqual(res.status_code, 200)\n\n    def test_create_requires_login(self):\n        res = self.client.post(reverse("post-create"), {"title": "x", "body": "y"})\n        self.assertEqual(res.status_code, 302)   # redirect to login'),
    ("h2", "The test client and a user"),
    ("code", "python", 'from django.contrib.auth.models import User\n\nself.user = User.objects.create_user("ada", password="pass-pass")\nself.client.login(username="ada", password="pass-pass")\nres = self.client.post(reverse("post-create"), {"title": "New", "body": "Body"})'),
    ("h2", "Fixtures vs factories"),
    ("p", "JSON fixtures are brittle. Prefer creating objects in <code>setUp</code> or using factory_boy. Mark tests that hit an external API with <code>@override_settings</code> and mock the call."),
    ("code", "bash", "python manage.py test\npython manage.py test blog.tests.test_views.PostTests.test_str"),
    ("note", "SimpleTestCase", "If a test does not need the database, use <code>SimpleTestCase</code> — it is faster."),
    ("exercise", "Write a test that creates a published and an unpublished post and asserts that the list page contains only the published title."),
]

CONTENT["django-static-media"] = [
    ("p", "Static files (CSS, JS, images you ship) and media files (user uploads) are configured differently, and the cache framework sits next to both."),
    ("h2", "Static files"),
    ("code", "python", '# settings\nSTATIC_URL = "static/"\nSTATIC_ROOT = BASE_DIR / "staticfiles"     # collectstatic target\nSTATICFILES_DIRS = [BASE_DIR / "static"]   # your source'),
    ("code", "html", '{% load static %}\n<link rel="stylesheet" href="{% static \'app.css\' %}">'),
    ("code", "bash", "python manage.py collectstatic"),
    ("p", "In production, <strong>WhiteNoise</strong> serves compressed, hashed files from Django without Nginx for small apps: <code>pip install whitenoise</code> and add the middleware."),
    ("h2", "Uploads"),
    ("code", "python", 'class Profile(models.Model):\n    avatar = models.ImageField(upload_to="avatars/")\n\n# settings\nMEDIA_URL = "/media/"\nMEDIA_ROOT = BASE_DIR / "media"'),
    ("p", "Never serve <code>MEDIA_ROOT</code> with WhiteNoise in production; put uploads on S3 (django-storages) so the app servers stay stateless."),
    ("h2", "Caching"),
    ("code", "python", 'from django.core.cache import cache\nfrom django.views.decorators.cache import cache_page\n\n@cache_page(60 * 5)\ndef popular(request):\n    ...\n\nposts = cache.get_or_set("home-posts", lambda: list(Post.objects.all()[:10]), 60)'),
    ("note", "LocMem vs Redis", "The default local-memory cache does not share across gunicorn workers. Use Redis (<code>django-redis</code>) as soon as you run more than one process."),
    ("exercise", "Add an <code>ImageField</code> to a model and a template that displays it with <code>{{ object.avatar.url }}</code>."),
]

CONTENT["django-drf-auth"] = [
    ("p", "Django REST framework's viewsets become production APIs when you add authentication, permissions, pagination and filters."),
    ("h2", "Authentication and permissions"),
    ("code", "python", '# settings.py\nREST_FRAMEWORK = {\n    "DEFAULT_AUTHENTICATION_CLASSES": [\n        "rest_framework.authentication.SessionAuthentication",\n        "rest_framework.authentication.TokenAuthentication",\n    ],\n    "DEFAULT_PERMISSION_CLASSES": [\n        "rest_framework.permissions.IsAuthenticatedOrReadOnly",\n    ],\n    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",\n    "PAGE_SIZE": 20,\n}'),
    ("code", "python", 'from rest_framework.permissions import IsAuthenticated, IsOwnerOrReadOnly\nfrom rest_framework.viewsets import ModelViewSet\n\nclass PostViewSet(ModelViewSet):\n    queryset = Post.objects.select_related("author")\n    serializer_class = PostSerializer\n    permission_classes = [IsAuthenticated]\n\n    def perform_create(self, serializer):\n        serializer.save(author=self.request.user)'),
    ("h2", "Filtering and search"),
    ("code", "python", 'from rest_framework.filters import SearchFilter, OrderingFilter\nfrom django_filters.rest_framework import DjangoFilterBackend\n\nclass PostViewSet(ModelViewSet):\n    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]\n    filterset_fields = ["published", "author"]\n    search_fields = ["title", "body"]\n    ordering_fields = ["created"]'),
    ("h2", "Throttling"),
    ("code", "python", '"DEFAULT_THROTTLE_RATES": {"anon": "20/min", "user": "100/min"}'),
    ("note", "Browsable API", "SessionAuthentication plus the browsable API is excellent for humans. Token or JWT is what a SPA or mobile app should send."),
    ("exercise", "Restrict <code>POST</code> to authenticated users while leaving <code>GET</code> public, and paginate lists by 10."),
]

CONTENT["django-sessions-messages"] = [
    ("p", "The session stores small bits of data per visitor. The messages framework is a flash queue on top of it. Email is how you leave the request/response cycle."),
    ("h2", "Sessions"),
    ("code", "python", 'def add_to_cart(request, sku):\n    cart = request.session.setdefault("cart", [])\n    cart.append(sku)\n    request.session.modified = True     # required when you mutate a list in place\n    return redirect("cart")'),
    ("p", "Do not store large objects or secrets in the session. The signed-cookie backend puts the whole payload on the client."),
    ("h2", "Messages"),
    ("code", "python", 'from django.contrib import messages\n\nmessages.success(request, "Post published.")\nmessages.error(request, "Could not save.")'),
    ("code", "html", '{% for message in messages %}\n  <p class="{{ message.tags }}">{{ message }}</p>\n{% endfor %}'),
    ("h2", "Sending email"),
    ("code", "python", 'from django.core.mail import send_mail\n\nsend_mail(\n    subject="Welcome",\n    message="Thanks for signing up.",\n    from_email="noreply@example.com",\n    recipient_list=[user.email],\n    fail_silently=False,\n)'),
    ("p", "In development, <code>EMAIL_BACKEND = \"django.core.mail.backends.console.EmailBackend\"</code> prints mail to the terminal. In production use SMTP or an API (Anymail)."),
    ("exercise", "After a successful form post, add a success message and redirect. Show the message in the base template."),
]

CONTENT["django-security"] = [
    ("p", "Django's defaults already block the usual attacks. Production is about leaving those defaults on and turning the HTTPS settings up."),
    ("h2", "What you get for free"),
    ("ul", [
        "<strong>CSRF</strong>: every POST form needs <code>{% csrf_token %}</code>. APIs that use cookies need the CSRF header too.",
        "<strong>XSS</strong>: templates auto-escape. Only use <code>|safe</code> on trusted HTML.",
        "<strong>SQL injection</strong>: the ORM parameterises queries. Never interpolate user input into <code>raw()</code>.",
        "<strong>Clickjacking</strong>: <code>X-Frame-Options</code> middleware.",
    ]),
    ("h2", "HTTPS and cookies"),
    ("code", "python", 'SECURE_SSL_REDIRECT = True\nSESSION_COOKIE_SECURE = True\nCSRF_COOKIE_SECURE = True\nSECURE_HSTS_SECONDS = 31536000\nSECURE_HSTS_INCLUDE_SUBDOMAINS = True\nSECURE_HSTS_PRELOAD = True'),
    ("h2", "The checklist"),
    ("code", "bash", "python manage.py check --deploy"),
    ("p", "Fix every warning before you ship. Keep <code>SECRET_KEY</code> and database passwords in the environment, not in git. <code>DEBUG = False</code> in production or you leak stack traces."),
    ("note", "Admin", "Put <code>/admin/</code> on a VPN or at a non-guessable path, force 2FA (django-otp), and never reuse the same password as a public account."),
    ("exercise", "Run <code>check --deploy</code> against your production settings module and list the flags you still need to turn on."),
]

CONTENT["django-deployment"] = [
    ("p", "A typical production stack is gunicorn workers behind Nginx (or a platform load balancer), with Postgres, Redis, and static files on a CDN or WhiteNoise."),
    ("h2", "WSGI entry"),
    ("code", "bash", "pip install gunicorn\ngunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 30"),
    ("code", "dockerfile", 'FROM python:3.12-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt\nCOPY . .\nRUN python manage.py collectstatic --noinput\nCMD ["gunicorn", "config.wsgi:application", "-b", "0.0.0.0:8000", "-w", "3"]'),
    ("h2", "Release steps"),
    ("ul", [
        "Set <code>DJANGO_SETTINGS_MODULE</code> to the prod module.",
        "Run <code>migrate</code> as a release command, before traffic hits new code that needs the schema.",
        "<code>collectstatic</code> into <code>STATIC_ROOT</code> (or WhiteNoise).",
        "Point <code>ALLOWED_HOSTS</code> and CSRF trusted origins at the real domain.",
    ]),
    ("h2", "What Nginx does"),
    ("p", "Terminate TLS, serve <code>/static/</code> and <code>/media/</code> directly, and reverse-proxy everything else to gunicorn. Health-check <code>/health/</code> so a bad deploy is taken out of the pool."),
    ("note", "ASGI", "If you need WebSockets or HTTP/2 push, switch to Daphne or Uvicorn with <code>config.asgi:application</code>. Ordinary request/response sites are fine on WSGI."),
    ("exercise", "Write a <code>GET /health/</code> view that returns 200 if the database connection works, and add it to <code>urls.py</code>."),
    ("solution", "python", 'from django.http import JsonResponse\nfrom django.db import connection\n\ndef health(request):\n    with connection.cursor() as c:\n        c.execute("SELECT 1")\n    return JsonResponse({"status": "ok"})'),
]
