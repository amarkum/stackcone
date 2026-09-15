(function () {
  var NAV_ITEMS = [
    { href: "/", label: "Home" },
    { href: "/work/", label: "Portfolio" },
    { href: "/solutions/", label: "Solutions" },
    {
      label: "Learn",
      href: "/learn/",
      children: [
        {
          label: "Coding",
          children: [
            { href: "/learn/#track-python", label: "Python" },
            { href: "/learn/#track-java", label: "Java" }
          ]
        },
        { href: "/learn/#track-data-structures", label: "Data Structures" },
        { href: "/learn/", label: "Browse all courses" }
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

  function renderLeaf(item) {
    return '<a href="' + esc(item.href) + '" role="menuitem">' + esc(item.label) + "</a>";
  }

  function renderMenuChild(item) {
    if (item.children) {
      return (
        '<div class="nav-dropdown-nested">' +
        '<button type="button" class="nav-dropdown-nested-trigger" aria-expanded="false" aria-haspopup="true">' +
        esc(item.label) +
        '<span class="nav-dropdown-chevron" aria-hidden="true"></span></button>' +
        '<div class="nav-dropdown-nested-panel" role="menu">' +
        item.children.map(renderLeaf).join("") +
        "</div></div>"
      );
    }
    return renderLeaf(item);
  }

  function renderItem(item) {
    if (item.children) {
      return (
        '<div class="nav-item nav-item--has-dropdown">' +
        '<a href="' + esc(item.href) + '" class="nav-dropdown-trigger" aria-haspopup="true">' +
        esc(item.label) +
        '<span class="nav-dropdown-chevron" aria-hidden="true"></span></a>' +
        '<div class="nav-dropdown" role="menu">' +
        item.children.map(renderMenuChild).join("") +
        "</div></div>"
      );
    }
    return '<a href="' + esc(item.href) + '">' + esc(item.label) + "</a>";
  }

  var nav = document.getElementById("main-nav");
  if (!nav) return;

  nav.innerHTML = NAV_ITEMS.map(renderItem).join("");

  var path = window.location.pathname.replace(/\/index\.html$/, "/").replace(/\/$/, "") || "/";

  nav.querySelectorAll("a[href]").forEach(function (link) {
    var raw = link.getAttribute("href");
    var href = raw.replace(/#.*$/, "").replace(/\/$/, "") || "/";
    var isActive = href === path || (href !== "/" && path.indexOf(href) === 0);
    if (isActive) {
      link.setAttribute("aria-current", "page");
    } else {
      link.removeAttribute("aria-current");
    }
  });

  if (path.indexOf("/learn") === 0) {
    var learnTrigger = nav.querySelector('.nav-dropdown-trigger[href="/learn/"]');
    if (learnTrigger) {
      learnTrigger.setAttribute("aria-current", "page");
    }
  }

  document.dispatchEvent(new CustomEvent("site-nav-ready", { detail: { nav: nav } }));
})();
