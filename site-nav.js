(function () {
  var CHEVRON =
    '<svg width="11" height="11" viewBox="0 0 13 13" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">' +
    '<path d="M3.25 5.25L6.5 8.5L9.75 5.25" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>';

  var NAV_ITEMS = [
    { href: "/", label: "Home" },
    { href: "/work/", label: "Portfolio" },
    { href: "/solutions/", label: "Solutions" },
    {
      id: "learn",
      label: "Learn",
      children: [
        {
          label: "Programming",
          items: [
            { href: "/learn/python/", label: "Python", prefix: "/learn/courses/python-", also: "/learn/python" },
            { href: "/learn/java/", label: "Java", prefix: "/learn/courses/java-", also: "/learn/java" }
          ]
        },
        {
          label: "DS & Algo",
          items: [
            { href: "/learn/data-structures/", label: "Data Structures", prefix: "/learn/courses/ds-", also: "/learn/data-structures" },
            { label: "Algorithms", soon: true },
            { label: "Sorting", soon: true },
            { label: "Searching", soon: true },
            { label: "Recursion", soon: true },
            { label: "Dynamic Programming", soon: true }
          ]
        },
        {
          label: "Frameworks",
          items: [
            { label: "LangChain", soon: true },
            { label: "React", soon: true },
            { label: "Next.js", soon: true },
            { label: "FastAPI", soon: true },
            { label: "Django", soon: true },
            { label: "Express", soon: true }
          ]
        },
        { href: "/learn/", label: "Browse all courses", separator: true }
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
    var prefix = item.prefix ? ' data-match="' + esc(item.prefix) + '"' : "";
    var also = item.also ? ' data-also="' + esc(item.also) + '"' : "";
    return (
      sep +
      '<a class="nav-dd-item" href="' + esc(item.href) + '"' + prefix + also + ' role="menuitem">' +
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
    return (
      '<div class="nav-dd-wrap" data-target="' + esc(item.id) + '">' +
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
    var isDropdownItem = link.classList.contains("nav-dd-item");
    var isActive = false;

    if (matchPrefix && path.indexOf(matchPrefix) === 0) {
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

  if (path.indexOf("/learn") === 0) {
    var learnBtn = nav.querySelector('.nav-dd-wrap[data-target="learn"] .nav-link--dd');
    if (learnBtn) learnBtn.setAttribute("aria-current", "page");
  }

  document.dispatchEvent(new CustomEvent("site-nav-ready", { detail: { nav: nav } }));
})();
