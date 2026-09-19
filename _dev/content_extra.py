"""Aggregates the per-course EXTRA teaching material (slug -> intro / more / recap)."""
from content_extra_python import EXTRA as _PY
from content_extra_js import EXTRA as _JS
from content_extra_sql import EXTRA as _SQL

EXTRA = {**_PY, **_JS, **_SQL}
