(function () {
  var categoryFilter = "all";
  var yearFilter = "all";
  var searchQuery = "";

  function escapeHtml(s) {
    var d = document.createElement("div");
    d.textContent = s;
    return d.innerHTML;
  }

  function renderPost(p) {
    var tags = p.tags
      .map(function (t) {
        return "<span class=\"tag\">" + escapeHtml(t) + "</span>";
      })
      .join("");

    var searchText = (
      p.title + " " + p.description + " " + p.category + " " + p.tags.join(" ")
    ).toLowerCase();

    return (
      "<a class=\"post-card\" href=\"" + escapeHtml(p.href) + "\"" +
        " data-category=\"" + escapeHtml(p.category) + "\"" +
        " data-year=\"" + escapeHtml(p.date.slice(0, 4)) + "\"" +
        " data-tags=\"" + escapeHtml(p.tags.join(",")) + "\"" +
        " data-search=\"" + escapeHtml(searchText) + "\">" +
        "<div class=\"post-meta\">me</div>" +
        "<h2>" + escapeHtml(p.title) + "</h2>" +
        "<p>" + escapeHtml(p.description) + "</p>" +
        "<div class=\"tags\">" + tags + "</div>" +
      "</a>"
    );
  }

  function applyFilters() {
    var cards = document.querySelectorAll(".post-card");
    var visible = 0;
    var query = searchQuery.trim().toLowerCase();

    cards.forEach(function (card) {
      var cat = card.getAttribute("data-category");
      var year = card.getAttribute("data-year");
      var searchText = card.getAttribute("data-search") || "";
      var catMatch = categoryFilter === "all" || cat === categoryFilter;
      var yearMatch = yearFilter === "all" || year === yearFilter;
      var searchMatch = !query || searchText.indexOf(query) >= 0;
      var show = catMatch && yearMatch && searchMatch;
      card.classList.toggle("is-hidden", !show);
      if (show) visible += 1;
    });

    var empty = document.getElementById("blog-empty");
    if (empty) empty.classList.toggle("is-hidden", visible > 0);
  }

  function buildCategoryFilter(posts) {
    var categories = ["all"];
    posts.forEach(function (p) {
      if (categories.indexOf(p.category) < 0) categories.push(p.category);
    });
    categories.sort(function (a, b) {
      if (a === "all") return -1;
      if (b === "all") return 1;
      return a.localeCompare(b);
    });

    var el = document.getElementById("blog-topic-select");
    if (!el) return;

    el.innerHTML = categories
      .map(function (cat) {
        var label = cat === "all" ? "All topics" : cat;
        return "<option value=\"" + escapeHtml(cat) + "\">" + escapeHtml(label) + "</option>";
      })
      .join("");
  }

  function buildDateFilter(posts) {
    var years = posts
      .map(function (p) {
        return p.date.slice(0, 4);
      })
      .filter(function (y, i, arr) {
        return arr.indexOf(y) === i;
      })
      .sort(function (a, b) {
        return b.localeCompare(a);
      });

    var el = document.getElementById("blog-date-select");
    if (!el) return;

    var options = ["<option value=\"all\">All time</option>"];
    years.forEach(function (year) {
      options.push(
        "<option value=\"" + escapeHtml(year) + "\">" + escapeHtml(year) + "</option>"
      );
    });
    el.innerHTML = options.join("");
  }

  function bindFilters() {
    var searchEl = document.getElementById("blog-search");
    var topicEl = document.getElementById("blog-topic-select");
    var dateEl = document.getElementById("blog-date-select");

    if (searchEl) {
      searchEl.addEventListener("input", function () {
        searchQuery = searchEl.value;
        applyFilters();
      });
    }

    if (topicEl) {
      topicEl.addEventListener("change", function () {
        categoryFilter = topicEl.value;
        applyFilters();
      });
    }

    if (dateEl) {
      dateEl.addEventListener("change", function () {
        yearFilter = dateEl.value;
        applyFilters();
      });
    }
  }

  function init(posts) {
    var list = document.getElementById("blog-posts");
    if (!list) return;

    list.innerHTML = posts.map(renderPost).join("");
    buildCategoryFilter(posts);
    buildDateFilter(posts);
    bindFilters();
    applyFilters();
  }

  fetch("./posts.json")
    .then(function (res) {
      if (!res.ok) throw new Error("Failed to load posts");
      return res.json();
    })
    .then(function (data) {
      init(data.posts || []);
    })
    .catch(function () {
      var list = document.getElementById("blog-posts");
      if (list) {
        list.innerHTML = "<p class=\"blog-error\">Could not load blog posts. Please refresh the page.</p>";
      }
    });
})();
