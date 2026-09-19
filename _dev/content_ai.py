"""AI: One Course. Aggregates the lesson modules, in course order."""
from content_ai_1 import META as _M1, CONTENT as _C1
from content_ai_2 import META as _M2, CONTENT as _C2
from content_ai_3 import META as _M3, CONTENT as _C3
from content_ai_4 import META as _M4, CONTENT as _C4

META = [*_M1, *_M2, *_M3, *_M4]
CONTENT = {**_C1, **_C2, **_C3, **_C4}
