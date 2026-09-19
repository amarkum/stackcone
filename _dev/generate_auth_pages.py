#!/usr/bin/env python3
"""Generate /login/ and /signup/ (static pages; Firebase Auth runs in the browser)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PAGES = {
    "login": {
        "title": "Log in",
        "heading": "Welcome back",
        "lede": "Log in to continue.",
        "pitch": "Good to see you again.",
        "sub": "Your progress, your account, on every device.",
        "submit": "Log in",
        "fields": """
          <label class="auth-field"><span>Email</span>
            <input type="email" name="email" autocomplete="email" required placeholder="you@example.com"></label>
          <label class="auth-field"><span class="auth-field-row">Password <button type="button" class="auth-link" data-reset>Forgot password?</button></span>
            <span class="auth-pass"><input type="password" name="password" autocomplete="current-password" required><button type="button" class="auth-eye" data-eye aria-label="Show password">Show</button></span></label>""",
        "switch": 'New here? <a href="/signup/" data-keep-next>Create an account</a>',
    },
    "signup": {
        "title": "Sign up",
        "heading": "Create your account",
        "lede": "Free, for everyone. No experience needed.",
        "pitch": "Everyone is welcome here.",
        "sub": "Students, career changers, engineers and teams. Learn at your own pace, in your own way.",
        "submit": "Create account",
        "fields": """
          <label class="auth-field"><span>Full name</span>
            <input type="text" name="name" autocomplete="name" required maxlength="60" placeholder="Ada Lovelace"></label>
          <label class="auth-field"><span>Email</span>
            <input type="email" name="email" autocomplete="email" required placeholder="you@example.com"></label>
          <label class="auth-field"><span>Password</span>
            <span class="auth-pass"><input type="password" name="password" autocomplete="new-password" required minlength="8"><button type="button" class="auth-eye" data-eye aria-label="Show password">Show</button></span>
            <span class="auth-strength" data-strength aria-live="polite"><i></i><i></i><i></i><i></i><b data-strength-text>At least 8 characters</b></span></label>""",
        "switch": 'Already have an account? <a href="/login/" data-keep-next>Log in</a>',
    },
}

# Google creates the account on first sign-in, so both pages share this button.
GOOGLE_BUTTON = """      <button type="button" class="auth-google" data-google>
        <svg viewBox="0 0 48 48" width="20" height="20" aria-hidden="true"><path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/><path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/><path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/><path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/></svg>
        <span data-label>Continue with Google</span>
      </button>
      <p class="auth-or"><span>or</span></p>
"""

SCRIPT = """
  <script type="module">
    import { signInWithGoogle, signUp, logIn, resetPassword, friendlyError } from "/assets/learn-auth.js?v=4";
    const mode = document.body.dataset.auth;
    const google = document.querySelector("[data-google]");
    const gLabel = google.querySelector("[data-label]");
    const form = document.querySelector("[data-form]");
    const submit = form.querySelector("[type=submit]");
    const msg = document.querySelector("[data-msg]");
    // Only follow same-site paths so ?next= cannot bounce users to another origin.
    const raw = new URLSearchParams(location.search).get("next") || "/learn/";
    const next = raw.startsWith("/") && !raw.startsWith("//") ? raw : "/learn/";
    document.querySelectorAll("[data-keep-next]").forEach(a => {
      a.href += "?next=" + encodeURIComponent(next);
    });

    let busy = false;
    const say = (text, ok) => { msg.textContent = text; msg.className = "auth-msg" + (text ? (ok ? " is-ok" : " is-error") : ""); };
    const setBusy = (on) => {
      busy = on;
      google.disabled = submit.disabled = on;
      submit.classList.toggle("is-busy", on);
    };

    google.addEventListener("click", async () => {
      setBusy(true);
      gLabel.textContent = "Opening Google…";
      say("");
      try {
        await signInWithGoogle();
        location.href = next;
      } catch (err) {
        say(friendlyError(err));
        setBusy(false);
        gLabel.textContent = "Continue with Google";
      }
    });

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const d = new FormData(form);
      setBusy(true);
      say("");
      try {
        if (mode === "signup") await signUp(d.get("name").trim(), d.get("email").trim(), d.get("password"));
        else await logIn(d.get("email").trim(), d.get("password"));
        location.href = next;
      } catch (err) {
        say(friendlyError(err));
        setBusy(false);
      }
    });

    const meter = document.querySelector("[data-strength]");
    if (meter) {
      const pw = form.password, text = meter.querySelector("[data-strength-text]");
      const words = ["At least 8 characters", "Too short", "Fair", "Good", "Strong"];
      pw.addEventListener("input", () => {
        const v = pw.value;
        let score = 0;
        if (v.length >= 8) score++;
        if (v.length >= 12) score++;
        if (/[a-z]/.test(v) && /[A-Z]/.test(v)) score++;
        if (/\\d/.test(v) && /[^A-Za-z0-9]/.test(v)) score++;
        const level = !v ? 0 : v.length < 8 ? 1 : Math.max(2, score + 1 > 4 ? 4 : score + 1);
        meter.dataset.level = String(level);
        text.textContent = words[level];
      });
    }

    document.querySelectorAll("[data-eye]").forEach(eye => eye.addEventListener("click", () => {
      const input = eye.previousElementSibling;
      const show = input.type === "password";
      input.type = show ? "text" : "password";
      eye.textContent = show ? "Hide" : "Show";
      eye.setAttribute("aria-label", show ? "Hide password" : "Show password");
    }));

    const reset = document.querySelector("[data-reset]");
    if (reset) reset.addEventListener("click", async () => {
      const email = form.email.value.trim();
      if (!email) { form.email.focus(); return say("Enter your email first, then click Forgot password."); }
      try { await resetPassword(email); say("Check your inbox for a reset link.", true); }
      catch (err) { say(friendlyError(err)); }
    });

    document.addEventListener("sc:auth", (e) => {
      if (e.detail.user && !busy) location.replace(next);   // already signed in
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
  <link rel="stylesheet" href="/assets/auth.css?v=17">
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-B29M3GX6QM"></script>
  <script src="/assets/analytics.js" defer></script>
</head>
<body class="auth-page" data-auth="{key}">
  <div class="auth-split">
    <aside class="auth-side" aria-label="About stackcone">
      <a href="/" class="auth-side-logo" aria-label="stackcone home"><img src="/logo/stackcone.png" alt="stackcone" width="140" height="30"></a>
      <div class="auth-side-body">
        <p class="auth-pitch">{p["pitch"]}</p>
        <p class="auth-sub">{p["sub"]}</p>
        <ul class="auth-tiles">
          <li><span class="auth-tile-icon">{ICON_LEARN}</span><span><strong>Learn</strong>Free lessons, from your first line of code.</span></li>
          <li><span class="auth-tile-icon">{ICON_READ}</span><span><strong>Read</strong>Plain-language guides on AI and software.</span></li>
          <li><span class="auth-tile-icon">{ICON_BUILD}</span><span><strong>Build</strong>Work with our team on your product.</span></li>
        </ul>
      </div>
      <p class="auth-trust">{ICON_LOCK} Only your name and email. No spam, ever.</p>
    </aside>

    <main class="auth-pane">
      <div class="auth-pane-top">
        <a href="/" class="auth-mobile-logo" aria-label="stackcone home"><img src="/logo/stackcone.png" alt="stackcone" width="120" height="26"></a>
        <a href="/" class="auth-back">Back to site</a>
        <span class="auth-alt">{p["switch"]}</span>
      </div>
      <section class="auth-card">
        <h1>{p["heading"]}</h1>
        <p class="auth-lede">{p["lede"]}</p>
{GOOGLE_BUTTON}        <form class="auth-form" data-form>{p["fields"]}
          <button type="submit" class="auth-submit">{p["submit"]}</button>
        </form>
        <p class="auth-msg" data-msg role="status" aria-live="polite"></p>
        <p class="auth-fine">By continuing you agree to our <a href="/privacy/">Privacy Policy</a>.</p>
      </section>
    </main>
  </div>
{SCRIPT}
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
