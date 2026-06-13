(function () {
  var NAV_ITEMS = [
    { href: "/", label: "Home" },
    { href: "/work/", label: "Portfolio" },
    { href: "/blog/", label: "Blog" },
    { href: "/contact/", label: "Contact" }
  ];

  var nav = document.getElementById("main-nav");
  if (!nav) return;

  nav.innerHTML = NAV_ITEMS.map(function (item) {
    return '<a href="' + item.href + '">' + item.label + "</a>";
  }).join("");
})();
