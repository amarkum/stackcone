/* stackcone Learn — "Search lessons…" box, in the category nav (catalog) or breadcrumb (lessons).
   Loaded by site-nav.js. Searches learn/courses.json in the browser; no server. */
(function () {
  "use strict";

  var inner = document.querySelector(".learn-main-inner");
  if (!inner || document.querySelector(".sc-search")) return;

  var ICON =
    '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" ' +
    'stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>';

  var box = document.createElement("div");
  box.className = "sc-search";
  box.setAttribute("role", "search");
  box.innerHTML =
    ICON +
    '<input type="search" placeholder="Search lessons…" aria-label="Search lessons" autocomplete="off" ' +
    'role="combobox" aria-expanded="false" aria-controls="sc-search-results" aria-autocomplete="list">' +
    '<ul class="sc-search-results" id="sc-search-results" role="listbox" hidden></ul>';

  // Sit on the right of the breadcrumb line; catalog pages have none, so use the top of the page.
  var CATS = [
    { href: "/learn/programming/", label: "Programming" },
    { href: "/learn/ds-algo/", label: "DS & Algo" },
    { href: "/learn/ai/", label: "AI" },
    { href: "/learn/frameworks/", label: "Frameworks" }
  ];

  function categoryNav() {
    var existing = inner.querySelector(".learn-cat-nav");
    if (existing) return existing;
    if (!inner.classList.contains("learn-catalog")) return null;
    var path = location.pathname.replace(/\/index\.html$/, "/");
    if (path.charAt(path.length - 1) !== "/") path += "/";
    var nav = document.createElement("nav");
    nav.className = "learn-cat-nav";
    nav.setAttribute("aria-label", "Learn categories");
    nav.innerHTML = CATS.map(function (c) {
      var on = path === c.href || path.indexOf(c.href) === 0;
      return '<a href="' + c.href + '"' + (on ? ' aria-current="page"' : "") + ">" + c.label + "</a>";
    }).join("");
    inner.insertBefore(nav, inner.firstChild);
    return nav;
  }

  var lead = categoryNav() || inner.querySelector(".learn-breadcrumb");
  if (lead) {
    var row = document.createElement("div");
    row.className = "learn-toolbar";
    lead.parentNode.insertBefore(row, lead);
    row.appendChild(lead);
    row.appendChild(box);
  } else {
    var bar = document.createElement("div");
    bar.className = "learn-toolbar learn-toolbar--end";
    bar.appendChild(box);
    inner.insertBefore(bar, inner.firstChild);
  }

  var input = box.querySelector("input");
  var list = box.querySelector("ul");
  var lessons = null;
  var active = -1;

  function load() {
    if (lessons) return Promise.resolve(lessons);
    return fetch("/learn/courses.json")
      .then(function (r) { return r.json(); })
      .then(function (d) {
        lessons = (d.courses || []).map(function (c) {
          return {
            title: c.title,
            track: c.trackLabel,
            level: c.level,
            url: new URL(c.href, location.origin + "/learn/").pathname,
            text: (c.title + " " + c.trackLabel + " " + (c.description || "")).toLowerCase(),
          };
        });
        return lessons;
      })
      .catch(function () { lessons = []; return lessons; });
  }

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function close() {
    list.hidden = true;
    input.setAttribute("aria-expanded", "false");
    active = -1;
  }

  function show(items, q) {
    if (!q) return close();
    active = -1;
    list.innerHTML = items.length
      ? items.map(function (l, i) {
          return '<li role="option" id="sc-sr-' + i + '"><a href="' + esc(l.url) + '"><strong>' + esc(l.title) +
            "</strong><span>" + esc(l.track) + " · " + esc(l.level) + "</span></a></li>";
        }).join("")
      : '<li class="sc-search-empty">No lessons match “' + esc(q) + "”</li>";
    list.hidden = false;
    input.setAttribute("aria-expanded", "true");
  }

  function search() {
    var q = input.value.trim().toLowerCase();
    load().then(function (all) {
      if (input.value.trim().toLowerCase() !== q) return; // a newer keystroke won
      var words = q.split(/\s+/).filter(Boolean);
      var hits = all.filter(function (l) {
        return words.every(function (w) { return l.text.indexOf(w) !== -1; });
      });
      // Title matches first.
      hits.sort(function (a, b) {
        return (b.title.toLowerCase().indexOf(q) === 0) - (a.title.toLowerCase().indexOf(q) === 0);
      });
      show(hits.slice(0, 8), q);
    });
  }

  function move(step) {
    var links = list.querySelectorAll("a");
    if (!links.length) return;
    active = (active + step + links.length) % links.length;
    links.forEach(function (a, i) { a.classList.toggle("is-active", i === active); });
    input.setAttribute("aria-activedescendant", "sc-sr-" + active);
  }

  input.addEventListener("input", search);
  input.addEventListener("focus", function () { load(); if (input.value.trim()) search(); });
  input.addEventListener("keydown", function (e) {
    if (e.key === "ArrowDown") { e.preventDefault(); move(1); }
    else if (e.key === "ArrowUp") { e.preventDefault(); move(-1); }
    else if (e.key === "Enter") {
      var links = list.querySelectorAll("a");
      var target = links[active >= 0 ? active : 0];
      if (target) { e.preventDefault(); location.href = target.getAttribute("href"); }
    } else if (e.key === "Escape") { close(); input.blur(); }
  });
  document.addEventListener("click", function (e) { if (!box.contains(e.target)) close(); });
})();
