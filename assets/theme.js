/* Light / dark theme.
   Loaded synchronously in <head> so the saved theme is applied before first paint.
   Choice is stored in localStorage; with no choice the OS preference is used. */
(function () {
  var KEY = "sc-theme";
  var root = document.documentElement;
  var media = window.matchMedia ? window.matchMedia("(prefers-color-scheme: dark)") : null;

  function saved() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }

  function current() {
    var s = saved();
    if (s === "light" || s === "dark") return s;
    return media && media.matches ? "dark" : "light";
  }

  function apply(theme) {
    root.setAttribute("data-theme", theme);
    root.style.colorScheme = theme;
    document.querySelectorAll(".theme-toggle").forEach(function (btn) {
      var next = theme === "dark" ? "light" : "dark";
      btn.setAttribute("aria-label", "Switch to " + next + " theme");
      btn.setAttribute("title", "Switch to " + next + " theme");
      btn.setAttribute("aria-pressed", theme === "dark" ? "true" : "false");
    });
  }

  apply(current());

  // Follow the OS setting until the visitor picks a theme themselves.
  if (media) {
    var onChange = function () { if (!saved()) apply(current()); };
    if (media.addEventListener) media.addEventListener("change", onChange);
    else if (media.addListener) media.addListener(onChange);
  }

  var ICONS =
    '<svg class="theme-icon theme-icon--moon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>' +
    '<svg class="theme-icon theme-icon--sun" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>';

  function toggle() {
    var next = current() === "dark" ? "light" : "dark";
    try { localStorage.setItem(KEY, next); } catch (e) {}
    apply(next);
  }

  function mount() {
    if (document.querySelector(".theme-toggle")) return;
    // Site header on normal pages; full auth layout on /login/ and /signup/
    // so the control can sit at the true right edge of the viewport.
    var host = document.querySelector(".header-inner") || document.querySelector(".auth-split") || document.querySelector(".auth-pane");
    if (!host) return;
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "theme-toggle";
    btn.innerHTML = ICONS;
    btn.addEventListener("click", toggle);
    var menuBtn = host.querySelector(".nav-toggle");
    host.insertBefore(btn, menuBtn || null);
    apply(current());
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", mount);
  else mount();

  window.stackconeTheme = { get: current, toggle: toggle };
})();
