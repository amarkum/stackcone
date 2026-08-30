(function () {
  var form = document.getElementById("not-found-search-form");
  var input = document.getElementById("not-found-search");
  var results = document.getElementById("not-found-results");
  if (!form || !input || !results) return;

  var posts = null;

  function escapeHtml(s) {
    var d = document.createElement("div");
    d.textContent = s;
    return d.innerHTML;
  }

  function renderMatches(items) {
    if (!items.length) {
      results.innerHTML = "<p class=\"not-found-results-empty\">No matching guides. Try <a href=\"/blog/\">browse all posts</a>.</p>";
      results.hidden = false;
      return;
    }
    var html = "<ul class=\"not-found-results-list\">";
    items.slice(0, 6).forEach(function (p) {
      var url = "/blog/posts/" + p.id + "/";
      html +=
        "<li><a href=\"" + escapeHtml(url) + "\">" +
        "<span class=\"not-found-results-title\">" + escapeHtml(p.title) + "</span>" +
        "<span class=\"not-found-results-desc\">" + escapeHtml(p.description) + "</span>" +
        "</a></li>";
    });
    html += "</ul>";
    results.innerHTML = html;
    results.hidden = false;
  }

  function search(query) {
    if (!posts) return;
    var q = query.trim().toLowerCase();
    if (!q) {
      results.hidden = true;
      results.innerHTML = "";
      return;
    }
    var matches = posts.filter(function (p) {
      var hay = (p.title + " " + p.description + " " + p.category + " " + (p.tags || []).join(" ")).toLowerCase();
      return hay.indexOf(q) >= 0;
    });
    renderMatches(matches);
  }

  fetch("/blog/posts.json")
    .then(function (r) { return r.json(); })
    .then(function (data) {
      posts = data.posts || [];
      var params = new URLSearchParams(window.location.search);
      var q = params.get("q");
      if (q) {
        input.value = q;
        search(q);
      }
    })
    .catch(function () {});

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    search(input.value);
  });

  var debounce;
  input.addEventListener("input", function () {
    clearTimeout(debounce);
    debounce = setTimeout(function () {
      search(input.value);
    }, 200);
  });
})();
