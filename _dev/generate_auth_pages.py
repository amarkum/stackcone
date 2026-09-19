#!/usr/bin/env python3
"""Generate /login/ and /signup/ (static pages; Firebase Auth runs in the browser)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PAGES = {
    "login": {
        "title": "Log in",
        "heading": "Welcome back",
        "lede": "Log in to pick up your courses where you left off, on any device.",
        "switch": 'New to stackcone? <a href="/signup/" data-keep-next>Create an account</a>',
    },
    "signup": {
        "title": "Sign up",
        "heading": "Create your account",
        "lede": "Free. Save your lesson progress and continue on any device.",
        "switch": 'Already have an account? <a href="/login/" data-keep-next>Log in</a>',
    },
}

# Google creates the account on first sign-in, so both pages share one button.
GOOGLE_BUTTON = """      <button type="button" class="auth-google" data-google>
        <svg viewBox="0 0 48 48" width="20" height="20" aria-hidden="true"><path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/><path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/><path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/><path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/></svg>
        <span>Continue with Google</span>
      </button>
      <p class="auth-msg" data-msg role="status" aria-live="polite"></p>
"""

SCRIPT = """
  <script type="module">
    import { signInWithGoogle, friendlyError } from "/assets/learn-auth.js";
    const btn = document.querySelector("[data-google]");
    const msg = document.querySelector("[data-msg]");
    // Only follow same-site paths so ?next= cannot bounce users to another origin.
    const raw = new URLSearchParams(location.search).get("next") || "/learn/";
    const next = raw.startsWith("/") && !raw.startsWith("//") ? raw : "/learn/";
    document.querySelectorAll("[data-keep-next]").forEach(a => {
      a.href += "?next=" + encodeURIComponent(next);
    });

    btn.addEventListener("click", async () => {
      btn.disabled = true;
      msg.textContent = "";
      msg.className = "auth-msg";
      try {
        await signInWithGoogle();
        location.href = next;
      } catch (err) {
        msg.textContent = friendlyError(err);
        msg.className = "auth-msg is-error";
        btn.disabled = false;
      }
    });

    document.addEventListener("sc:auth", (e) => {
      if (e.detail.user && !btn.disabled) location.replace(next);   // already signed in
    });
  </script>"""


def page(key: str, p: dict) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="robots" content="noindex, follow">
  <title>{p["title"]} | stackcone</title>
  <meta name="description" content="{p["lede"]}">
  <link rel="canonical" href="https://stackcone.com/{key}/">
  <link rel="icon" type="image/png" href="/favicon/dark-favicon.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/styles.css?v=2">
  <link rel="stylesheet" href="/assets/auth.css?v=2">
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-B29M3GX6QM"></script>
  <script src="/assets/analytics.js" defer></script>
</head>
<body class="auth-page" data-auth="{key}">
  <header class="header">
    <div class="nav-overlay" id="nav-overlay" aria-hidden="true"></div>
    <div class="header-inner">
      <a href="/" class="logo-link"><img src="/logo/stackcone.png" alt="stackcone" class="logo" width="280" height="60"></a>
      <button type="button" class="nav-toggle" aria-label="Open menu" aria-expanded="false" aria-controls="main-nav">
        <span class="nav-toggle-bar"></span><span class="nav-toggle-bar"></span><span class="nav-toggle-bar"></span>
      </button>
      <nav class="nav" id="main-nav" aria-label="Main navigation"></nav>
    </div>
  </header>

  <main class="auth-main">
    <section class="auth-card">
      <h1>{p["heading"]}</h1>
      <p class="auth-lede">{p["lede"]}</p>
{GOOGLE_BUTTON}      <p class="auth-switch">{p["switch"]}</p>
    </section>
  </main>

  <script src="/site-nav.js" defer></script>
  <script src="/script.js?v=2" defer></script>{SCRIPT}
</body>
</html>
"""


def main() -> None:
    for key, p in PAGES.items():
        out = ROOT / key / "index.html"
        out.parent.mkdir(exist_ok=True)
        out.write_text(page(key, p), encoding="utf-8")
    print("Generated /login/ and /signup/")


if __name__ == "__main__":
    main()
