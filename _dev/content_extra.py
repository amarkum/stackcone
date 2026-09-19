"""Aggregates the per-course EXTRA teaching material (slug -> intro / more / recap)."""
from content_extra_python import EXTRA as _PY
from content_extra_js import EXTRA as _JS
from content_extra_sql import EXTRA as _SQL
from content_extra_git import EXTRA as _GIT
from content_extra_java import EXTRA as _JAVA
from content_extra_web import EXTRA as _WEB

EXTRA = {**_PY, **_JS, **_SQL, **_GIT, **_JAVA, **_WEB}
