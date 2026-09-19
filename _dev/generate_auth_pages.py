#!/usr/bin/env python3
"""Generate /login/ and /signup/ (static pages; Firebase Auth runs in the browser)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PAGES = {
    "login": {
        "title": "Log in",
        "heading": "Welcome back",
        "lede": "Log in to your stackcone account.",
        "switch": 'New to stackcone? <a href="/signup/" data-keep-next>Create a free account</a>',
    },
    "signup": {
        "title": "Sign up",
        "heading": "Create your account",
        "lede": "Free, and takes one click.",
        "switch": 'Already have an account? <a href="/login/" data-keep-next>Log in</a>',
    },
}

# Google creates the account on first sign-in, so both pages share one button.
GOOGLE_BUTTON = """      <button type="button" class="auth-google" data-google>
        <svg viewBox="0 0 48 48" width="20" height="20" aria-hidden="true"><path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/><path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/><path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/><path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/></svg>
        <span data-label>Continue with Google</span></span>
      </button>
      <p class="auth-msg" data-msg role="status" aria-live="polite"></p>
"""

SCRIPT = """
  <script type="module">
    import { signInWithGoogle, friendlyError } from "/assets/learn-auth.js";
    const btn = document.querySelector("[data-google]");
    const msg = document.querySelector("[data-msg]");
    const label = btn.querySelector("[data-label]");
    // Only follow same-site paths so ?next= cannot bounce users to another origin.
    const raw = new URLSearchParams(location.search).get("next") || "/learn/";
    const next = raw.startsWith("/") && !raw.startsWith("//") ? raw : "/learn/";
    document.querySelectorAll("[data-keep-next]").forEach(a => {
      a.href += "?next=" + encodeURIComponent(next);
    });

    btn.addEventListener("click", async () => {
      btn.disabled = true;
      btn.classList.add("is-busy");
      label.textContent = "Opening Google…";
      msg.textContent = "";
      msg.className = "auth-msg";
      try {
        await signInWithGoogle();
        location.href = next;
      } catch (err) {
        msg.textContent = friendlyError(err);
        msg.className = "auth-msg is-error";
        btn.disabled = false;
        btn.classList.remove("is-busy");
        label.textContent = "Continue with Google";
      }
    });

    document.addEventListener("sc:auth", (e) => {
      if (e.detail.user && !btn.disabled) location.replace(next);   // already signed in
    });
  </script>"""


def _icon(path: str) -> str:
    return (f'<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" fill="none" stroke="currentColor" '
            f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{path}</svg>')


ICON_LEARN = _icon('<path d="M2 9l10-5 10 5-10 5z"/><path d="M6 11v5c0 1.5 3 3 6 3s6-1.5 6-3v-5"/>')
ICON_READ = _icon('<path d="M4 5a2 2 0 012-2h13v16H6a2 2 0 00-2 2z"/><path d="M4 19V5M9 8h6M9 12h6"/>')
ICON_BUILD = _icon('<path d="M8 6l-6 6 6 6M16 6l6 6-6 6M14 4l-4 16"/>')
ICON_LOCK = _icon('<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 018 0v4"/>')


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
  <link rel="stylesheet" href="/assets/auth.css?v=4">
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
    <div class="auth-shell">
      <section class="auth-brand" aria-label="About stackcone">
        <img src="/logo/stackcone.png" alt="" class="auth-brand-logo" width="140" height="30">
        <p class="auth-pitch">One account for everything on stackcone.</p>
        <p class="auth-sub">Whether you are here to learn, to read, or to build something with us, you are welcome.</p>
        <ul class="auth-tiles">
          <li><span class="auth-tile-icon">{ICON_LEARN}</span><span><strong>Learn</strong>Free lessons with code you can run. Your progress follows you.</span></li>
          <li><span class="auth-tile-icon">{ICON_READ}</span><span><strong>Read</strong>Practical guides on AI, cloud and software engineering.</span></li>
          <li><span class="auth-tile-icon">{ICON_BUILD}</span><span><strong>Build</strong>Work with our team on AI and software products.</span></li>
        </ul>
        <p class="auth-trust">{ICON_LOCK} We only use your name and email. No spam, no posting.</p>
      </section>
      <section class="auth-card">
        <h1>{p["heading"]}</h1>
        <p class="auth-lede">{p["lede"]}</p>
{GOOGLE_BUTTON}        <p class="auth-fine">By continuing you agree to our <a href="/privacy/">Privacy Policy</a>.</p>
        <p class="auth-switch">{p["switch"]}</p>
      </section>
    </div>
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
