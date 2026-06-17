(function () {
  var NAV_ITEMS = [
    { href: "/", label: "Home" },
    { href: "/work/", label: "Portfolio" },
    { href: "/solutions/", label: "Solutions" },
    { href: "/blog/", label: "Blog" },
    { href: "/about/", label: "About" },
    { href: "/contact/", label: "Contact" }
  ];

  var nav = document.getElementById("main-nav");
  if (!nav) return;

  if (!nav.querySelector("a")) {
    nav.innerHTML = NAV_ITEMS.map(function (item) {
      return '<a href="' + item.href + '">' + item.label + "</a>";
    }).join("");
  }

  var path = window.location.pathname.replace(/\/index\.html$/, "/").replace(/\/$/, "") || "/";

  nav.querySelectorAll("a[href]").forEach(function (link) {
    var href = link.getAttribute("href").replace(/\/$/, "") || "/";
    var isActive =
      href === path ||
      (href !== "/" && path.indexOf(href) === 0);
    if (isActive) {
      link.setAttribute("aria-current", "page");
    } else {
      link.removeAttribute("aria-current");
    }
  });
})();
