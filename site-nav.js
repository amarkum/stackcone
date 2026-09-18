(function () {
  var CHEVRON =
    '<svg width="11" height="11" viewBox="0 0 13 13" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">' +
    '<path d="M3.25 5.25L6.5 8.5L9.75 5.25" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>';

  var NAV_ITEMS = [
    { href: "/", label: "Home" },
    { href: "/work/", label: "Portfolio" },
    { href: "/solutions/", label: "Solutions" },
    {
      id: "programming",
      label: "Programming",
      href: "/learn/programming/",
      children: [
        { href: "/learn/courses/python-hello-world/", label: "Python", matches: ["/learn/python", "/learn/courses/python-"] },
        { href: "/learn/courses/java-hello-world/", label: "Java", matches: ["/learn/java", "/learn/courses/java-"] },
        { href: "/learn/courses/js-hello-world/", label: "JavaScript", matches: ["/learn/javascript", "/learn/courses/js-"] },
        { href: "/learn/courses/html-introduction/", label: "HTML & CSS", matches: ["/learn/htmlcss", "/learn/courses/html-", "/learn/courses/css-"] },
        { href: "/learn/courses/ts-introduction/", label: "TypeScript", matches: ["/learn/typescript", "/learn/courses/ts-"] },
        { href: "/learn/courses/git-introduction/", label: "Git & CLI", matches: ["/learn/git", "/learn/courses/git-"] },
        { href: "/learn/courses/sql-introduction/", label: "SQL", matches: ["/learn/sql", "/learn/courses/sql-"] },
        { href: "/learn/programming/", label: "All Programming", separator: true }
      ]
    },
    {
      id: "ds-algo",
      label: "DS & Algo",
      href: "/learn/ds-algo/",
      children: [
        { href: "/learn/courses/ds-introduction/", label: "Data Structures", matches: ["/learn/data-structures", "/learn/courses/ds-"] },
        { href: "/learn/courses/algo-searching/", label: "Algorithms", matches: ["/learn/algorithms", "/learn/courses/algo-"] },
        { href: "/learn/courses/algo-sorting/", label: "Sorting" },
        { href: "/learn/courses/algo-recursion/", label: "Recursion" },
        { href: "/learn/courses/algo-dynamic-programming/", label: "Dynamic Programming" },
        { href: "/learn/ds-algo/", label: "All DS & Algo", separator: true }
      ]
    },
    {
      id: "frameworks",
      label: "Frameworks",
      href: "/learn/frameworks/",
      children: [
        { href: "/learn/courses/react-introduction/", label: "React", matches: ["/learn/react", "/learn/courses/react-"] },
        { href: "/learn/courses/django-introduction/", label: "Django", matches: ["/learn/django", "/learn/courses/django-"] },
        { href: "/learn/courses/fastapi-introduction/", label: "FastAPI", matches: ["/learn/fastapi", "/learn/courses/fastapi-"] },
        { href: "/learn/courses/express-introduction/", label: "Express", matches: ["/learn/express", "/learn/courses/express-"] },
        { label: "LangChain", soon: true },
        { label: "Next.js", soon: true },
        { href: "/learn/frameworks/", label: "All Frameworks", separator: true }
      ]
    },
    { href: "/blog/", label: "Blog" },
    { href: "/about/", label: "About" },
    { href: "/contact/", label: "Contact" }
  ];

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

  function renderPanelChild(item) {
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
      '<div class="nav-dd-panel" data-name="' + esc(item.id) + '" role="menu">' +
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

  nav.innerHTML = NAV_ITEMS.map(renderItem).join("");

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

  document.dispatchEvent(new CustomEvent("site-nav-ready", { detail: { nav: nav } }));
})();
