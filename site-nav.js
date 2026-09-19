(function () {
  var CHEVRON =
    '<svg width="11" height="11" viewBox="0 0 13 13" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">' +
    '<path d="M3.25 5.25L6.5 8.5L9.75 5.25" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>';

  var NAV_ITEMS = [
    { href: "/work/", label: "Portfolio" },
    { href: "/solutions/", label: "Solutions" },
    {
      id: "programming",
      label: "Programming",
      href: "/learn/programming/",
      children: [
        { href: "/learn/programming/python/hello-world/", label: "Python", matches: ["/learn/programming/python"] },
        { href: "/learn/programming/java/hello-world/", label: "Java", matches: ["/learn/programming/java"] },
        { href: "/learn/programming/javascript/hello-world/", label: "JavaScript", matches: ["/learn/programming/javascript"] },
        { href: "/learn/programming/htmlcss/introduction/", label: "HTML & CSS", matches: ["/learn/programming/htmlcss"] },
        { href: "/learn/programming/typescript/introduction/", label: "TypeScript", matches: ["/learn/programming/typescript"] },
        { href: "/learn/programming/git/introduction/", label: "Git & CLI", matches: ["/learn/programming/git"] },
        { href: "/learn/programming/docker/introduction/", label: "Docker", matches: ["/learn/programming/docker"] },
        { href: "/learn/programming/pandas/introduction/", label: "Pandas", matches: ["/learn/programming/pandas"] },
        { href: "/learn/programming/sql/introduction/", label: "SQL", matches: ["/learn/programming/sql"] },
        { href: "/learn/programming/", label: "All Programming", separator: true }
      ]
    },
    {
      id: "ds-algo",
      label: "DS & Algo",
      href: "/learn/ds-algo/",
      children: [
        { href: "/learn/ds-algo/data-structures/introduction/", label: "Data Structures", matches: ["/learn/ds-algo/data-structures"] },
        { href: "/learn/ds-algo/algorithms/searching/", label: "Algorithms", matches: ["/learn/ds-algo/algorithms"] },
        { href: "/learn/ds-algo/sysdesign/fundamentals/", label: "System Design", matches: ["/learn/ds-algo/sysdesign"] },
        { href: "/learn/ds-algo/", label: "All DS & Algo", separator: true }
      ]
    },
    {
      id: "frameworks",
      label: "Frameworks",
      href: "/learn/frameworks/",
      children: [
        { href: "/learn/frameworks/react/introduction/", label: "React", matches: ["/learn/frameworks/react"] },
        { href: "/learn/frameworks/django/introduction/", label: "Django", matches: ["/learn/frameworks/django"] },
        { href: "/learn/frameworks/flask/introduction/", label: "Flask", matches: ["/learn/frameworks/flask"] },
        { href: "/learn/frameworks/fastapi/introduction/", label: "FastAPI", matches: ["/learn/frameworks/fastapi"] },
        { href: "/learn/frameworks/express/introduction/", label: "Express", matches: ["/learn/frameworks/express"] },
        { href: "/learn/frameworks/spring/introduction/", label: "Spring Boot", matches: ["/learn/frameworks/spring"] },
        { href: "/learn/frameworks/nextjs/introduction/", label: "Next.js", matches: ["/learn/frameworks/nextjs"] },
        { href: "/learn/frameworks/langchain/introduction/", label: "LangChain", matches: ["/learn/frameworks/langchain"] },
        { href: "/learn/frameworks/", label: "All Frameworks", separator: true }
      ]
    },
    {
      id: "ai",
      label: "AI",
      href: "/learn/ai/",
      children: [
        { href: "/learn/ai/artificial-intelligence/what-is-an-llm/", label: "AI (Artificial Intelligence)", matches: ["/learn/ai/artificial-intelligence"] },
        { href: "/learn/ai/", label: "All AI", separator: true }
      ]
    },
    { href: "/blog/", label: "Blog" },
    { href: "/about/", label: "About" },
    { href: "/contact/", label: "Contact" }
  ];

  // Merge Programming / DS & Algo / Frameworks into a single nested "Learn" menu
  (function () {
    var ids = ["programming", "ds-algo", "frameworks", "ai"];
    var subs = [];
    var at = -1;
    NAV_ITEMS = NAV_ITEMS.filter(function (it, i) {
      if (ids.indexOf(it.id) === -1) return true;
      if (at < 0) at = i;
      subs.push({ sub: true, label: it.label, href: it.href, children: it.children });
      return false;
    });
    NAV_ITEMS.splice(at, 0, { id: "learn", label: "Learn", href: "/learn/", children: subs });
  })();

  function esc(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/"/g, "&quot;");
  }

  function renderPanelItem(item) {
    var sep = item.separator ? '<div class="nav-dd-sep" role="separator"></div>' : "";
    if (item.soon) {
      return (
        sep +
        '<span class="nav-dd-item nav-dd-item--soon" role="menuitem" aria-disabled="true">' +
        esc(item.label) +
        '<em>Soon</em></span>'
      );
    }
    var matches = item.matches
      ? ' data-matches="' + esc(item.matches.join("|")) + '"'
      : "";
    var prefix = item.prefix ? ' data-match="' + esc(item.prefix) + '"' : "";
    var also = item.also ? ' data-also="' + esc(item.also) + '"' : "";
    return (
      sep +
      '<a class="nav-dd-item" href="' + esc(item.href) + '"' + prefix + also + matches + ' role="menuitem">' +
      esc(item.label) +
      "</a>"
    );
  }

  function renderPanelGroup(group) {
    return (
      '<div class="nav-dd-group">' +
      '<p class="nav-dd-group-label">' + esc(group.label) + "</p>" +
      group.items.map(renderPanelItem).join("") +
      "</div>"
    );
  }

  function renderSub(item) {
    return (
      '<div class="nav-dd-sub">' +
      '<a class="nav-dd-item nav-dd-item--sub" href="' + esc(item.href) + '" aria-haspopup="true" role="menuitem">' +
      esc(item.label) + '<span class="nav-sub-chevron">' + CHEVRON + "</span></a>" +
      '<div class="nav-dd-flyout" role="menu">' +
      item.children.map(renderPanelItem).join("") +
      "</div></div>"
    );
  }

  function renderPanelChild(item) {
    if (item.sub) return renderSub(item);
    if (item.items) return renderPanelGroup(item);
    return renderPanelItem(item);
  }

  function renderDropdown(item) {
    var rootHref = item.href
      ? ' data-root-href="' + esc(item.href) + '"'
      : "";
    return (
      '<div class="nav-dd-wrap" data-target="' + esc(item.id) + '"' + rootHref + ">" +
      '<button type="button" class="nav-link nav-link--dd" aria-haspopup="true" aria-expanded="false">' +
      esc(item.label) +
      '<span class="nav-link-chevron">' + CHEVRON + "</span>" +
      "</button>" +
      '<div class="nav-dd-panel' + (item.id === "learn" ? " nav-dd-panel--nested" : "") + '" data-name="' + esc(item.id) + '" role="menu">' +
      item.children.map(renderPanelChild).join("") +
      "</div></div>"
    );
  }

  function renderItem(item) {
    if (item.children) return renderDropdown(item);
    return '<a class="nav-link" href="' + esc(item.href) + '">' + esc(item.label) + "</a>";
  }

  function pathMatches(path, patterns) {
    for (var i = 0; i < patterns.length; i++) {
      var p = patterns[i];
      if (path === p || path.indexOf(p) === 0) return true;
    }
    return false;
  }

  var nav = document.getElementById("main-nav");
  if (!nav) return;

  nav.innerHTML = NAV_ITEMS.map(renderItem).join("") +
    '<a class="nav-cta" href="https://www.upwork.com/agencies/2022687811186513260/" target="_blank" rel="noopener noreferrer">Hire on Upwork</a>';

  var path = window.location.pathname.replace(/\/index\.html$/, "/").replace(/\/$/, "") || "/";

  nav.querySelectorAll("a.nav-link, a.nav-dd-item").forEach(function (link) {
    var raw = link.getAttribute("href");
    if (!raw || raw.charAt(0) === "#") return;

    var hashIndex = raw.indexOf("#");
    var hash = hashIndex >= 0 ? raw.slice(hashIndex) : "";
    var href = (hashIndex >= 0 ? raw.slice(0, hashIndex) : raw).replace(/\/$/, "") || "/";
    var matchPrefix = link.getAttribute("data-match");
    var alsoPath = link.getAttribute("data-also");
    var matchesAttr = link.getAttribute("data-matches");
    var isDropdownItem = link.classList.contains("nav-dd-item");
    var isActive = false;

    if (matchesAttr && pathMatches(path, matchesAttr.split("|"))) {
      isActive = true;
    } else if (matchPrefix && path.indexOf(matchPrefix) === 0) {
      isActive = true;
    } else if (alsoPath && (path === alsoPath || path.indexOf(alsoPath + "/") === 0)) {
      isActive = true;
    } else if (hash) {
      isActive = href === path && window.location.hash === hash;
    } else if (isDropdownItem) {
      isActive = href === path && !window.location.hash;
    } else {
      isActive = href === path || (href !== "/" && path.indexOf(href + "/") === 0);
    }

    if (isActive) {
      link.setAttribute("aria-current", "page");
    } else {
      link.removeAttribute("aria-current");
    }
  });

  // Highlight parent dropdown when any of its courses/pages are active
  nav.querySelectorAll(".nav-dd-wrap").forEach(function (wrap) {
    var hasActiveChild = wrap.querySelector('.nav-dd-item[aria-current="page"]');
    var root = wrap.getAttribute("data-root-href");
    var rootPath = root ? root.replace(/\/$/, "") : "";
    var onRoot =
      rootPath &&
      (path === rootPath || path.indexOf(rootPath + "/") === 0);
    if (hasActiveChild || onRoot) {
      var btn = wrap.querySelector(".nav-link--dd");
      if (btn) btn.setAttribute("aria-current", "page");
    }
  });

  // Paint the avatar from last visit before Firebase loads, so it does not pop in late.
  if (!document.querySelector('link[href*="auth.css"]')) {
    var css = document.createElement("link");
    css.rel = "stylesheet";
    css.href = "/assets/auth.css?v=36";
    document.head.appendChild(css);
  }
  (function paintCachedAccount() {
    var snap = null;
    var known = false;
    try {
      var raw = localStorage.getItem("sc.auth.snapshot.v1");
      if (raw !== null) {
        known = true;
        snap = JSON.parse(raw);
      }
    } catch (e) { /* private mode */ }
    if (!known) return;
    var host = document.querySelector("[data-account]") || document.querySelector(".header-inner");
    if (!host) return;
    var box = document.getElementById("sc-account");
    if (!box) {
      box = document.createElement("div");
      box.id = "sc-account";
      box.className = "sc-account";
      host.appendChild(box);
    }
    function esc(s) {
      return String(s).replace(/[&<>"']/g, function (c) {
        return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
      });
    }
    var next = encodeURIComponent(location.pathname + location.search);
    if (!snap) {
      box.setAttribute("data-uid", "");
      box.innerHTML = '<a class="sc-account-login" href="/login/?next=' + next + '">Log in</a>';
      return;
    }
    var src = (snap.displayName || snap.email || "?").trim();
    var parts = src.split(/[\s@._-]+/).filter(Boolean);
    var initials = ((parts[0] || "?")[0] + (parts[1] ? parts[1][0] : "")).toUpperCase();
    var label = snap.displayName || snap.email || "";
    box.setAttribute("data-uid", snap.uid || "");
    box.innerHTML =
      '<button type="button" class="sc-avatar" aria-haspopup="true" aria-expanded="false" title="' + esc(label) + '">' + esc(initials) + "</button>" +
      '<div class="sc-account-menu" hidden>' +
      '<p class="sc-account-who"><strong>' + esc(snap.displayName || "Learner") + "</strong><span>" + esc(snap.email || "") + "</span></p>" +
      '<a href="/learn/">My courses</a>' +
      '<button type="button" data-logout>Log out</button>' +
      "</div>";
  })();

  // Log in / avatar in the header on every page: load the auth module once.
  // The module URL matches the lesson pages and /login/, so it only ever runs one instance.
  if (!document.querySelector('script[src*="learn-auth.js"]')) {
    var auth = document.createElement("script");
    auth.type = "module";
    auth.src = "/assets/learn-auth.js?v=5";
    document.head.appendChild(auth);
  }

  // Lesson search box in the header on Learn pages.
  if (/^\/learn(\/|$)/.test(location.pathname) && !document.querySelector('script[src*="learn-search.js"]')) {
    var search = document.createElement("script");
    search.src = "/assets/learn-search.js?v=3";
    search.defer = true;
    document.head.appendChild(search);
  }

  // "Listen" (read aloud) control on lessons, blog posts and solution write-ups.
  var readable = document.querySelector(".learn-lesson") ||
    (/^\/(blog\/posts|solutions)\/[^/]+/.test(location.pathname) && document.querySelector("article.blog-article h1"));
  if (readable && !document.querySelector('script[src*="learn-tts.js"]')) {
    var tts = document.createElement("script");
    tts.src = "/assets/learn-tts.js?v=3";
    tts.defer = true;
    document.head.appendChild(tts);
  }

  document.dispatchEvent(new CustomEvent("site-nav-ready", { detail: { nav: nav } }));
})();
