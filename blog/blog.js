(function () {
  var PAGE_SIZE = 3;
  var categoryFilter = "all";
  var yearFilter = "all";
  var searchQuery = "";
  var currentPage = 1;

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
        "<div class=\"post-meta\">By " + escapeHtml(p.author) + "</div>" +
        "<h2>" + escapeHtml(p.title) + "</h2>" +
        "<p>" + escapeHtml(p.description) + "</p>" +
        "<div class=\"tags\">" + tags + "</div>" +
      "</a>"
    );
  }

  function cardMatchesFilter(card) {
    var cat = card.getAttribute("data-category");
    var year = card.getAttribute("data-year");
    var searchText = card.getAttribute("data-search") || "";
    var query = searchQuery.trim().toLowerCase();
    var catMatch = categoryFilter === "all" || cat === categoryFilter;
    var yearMatch = yearFilter === "all" || year === yearFilter;
    var searchMatch = !query || searchText.indexOf(query) >= 0;
    return catMatch && yearMatch && searchMatch;
  }

  function renderPagination(totalItems, totalPages) {
    var nav = document.getElementById("blog-pagination");
    if (!nav) return;

    if (totalItems <= PAGE_SIZE) {
      nav.classList.add("is-hidden");
      nav.innerHTML = "";
      return;
    }

    nav.classList.remove("is-hidden");
    var parts = [];

    parts.push(
      "<button type=\"button\" class=\"list-pagination-btn\"" +
        (currentPage <= 1 ? " disabled" : "") +
        " data-page=\"" + (currentPage - 1) + "\" aria-label=\"Previous page\">" +
        "← Prev</button>"
    );

    for (var page = 1; page <= totalPages; page += 1) {
      var active = page === currentPage ? " is-active" : "";
      parts.push(
        "<button type=\"button\" class=\"list-pagination-btn" + active + "\"" +
          " data-page=\"" + page + "\"" +
          (page === currentPage ? " aria-current=\"page\"" : "") +
          ">" + page + "</button>"
      );
    }

    parts.push(
      "<button type=\"button\" class=\"list-pagination-btn\"" +
        (currentPage >= totalPages ? " disabled" : "") +
        " data-page=\"" + (currentPage + 1) + "\" aria-label=\"Next page\">" +
        "Next →</button>"
    );

    nav.innerHTML = parts.join("");
  }

  function applyFilters() {
    var cards = Array.prototype.slice.call(document.querySelectorAll(".post-card"));
    var matched = cards.filter(cardMatchesFilter);
    var totalPages = Math.max(1, Math.ceil(matched.length / PAGE_SIZE));

    if (currentPage > totalPages) currentPage = totalPages;
    if (currentPage < 1) currentPage = 1;

    cards.forEach(function (card) {
      card.classList.add("is-hidden");
    });

    matched.forEach(function (card, index) {
      var page = Math.floor(index / PAGE_SIZE) + 1;
      if (page === currentPage) {
        card.classList.remove("is-hidden");
      }
    });

    var empty = document.getElementById("blog-empty");
    if (empty) empty.classList.toggle("is-hidden", matched.length > 0);

    renderPagination(matched.length, totalPages);
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
    var paginationEl = document.getElementById("blog-pagination");

    if (searchEl) {
      searchEl.addEventListener("input", function () {
        searchQuery = searchEl.value;
        currentPage = 1;
        applyFilters();
      });
    }

    if (topicEl) {
      topicEl.addEventListener("change", function () {
        categoryFilter = topicEl.value;
        currentPage = 1;
        applyFilters();
      });
    }

    if (dateEl) {
      dateEl.addEventListener("change", function () {
        yearFilter = dateEl.value;
        currentPage = 1;
        applyFilters();
      });
    }

    if (paginationEl) {
      paginationEl.addEventListener("click", function (event) {
        var btn = event.target.closest("[data-page]");
        if (!btn || btn.disabled) return;
        var page = parseInt(btn.getAttribute("data-page"), 10);
        if (!page || page === currentPage) return;
        currentPage = page;
        applyFilters();
        var list = document.getElementById("blog-posts");
        if (list) list.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    }
  }

  function postsFromDom() {
    var cards = document.querySelectorAll("#blog-posts .post-card");
    return Array.prototype.map.call(cards, function (card) {
      var year = card.getAttribute("data-year") || "2026";
      return {
        title: card.querySelector("h2") ? card.querySelector("h2").textContent : "",
        description: card.querySelector("p") ? card.querySelector("p").textContent : "",
        href: card.getAttribute("href") || "",
        category: card.getAttribute("data-category") || "",
        date: year + "-01-01",
        author: "Amar Kumar",
        tags: (card.getAttribute("data-tags") || "").split(",").filter(Boolean)
      };
    });
  }

  function init(posts, list) {
    if (!list) return;

    var hasStaticCards = list.querySelectorAll(".post-card").length > 0;
    if (!hasStaticCards) {
      if (!posts.length) {
        list.innerHTML = "<p class=\"blog-empty\">No blog posts yet.</p>";
        return;
      }
      list.innerHTML = posts.map(renderPost).join("");
    }

    var source = hasStaticCards ? postsFromDom() : posts;
    buildCategoryFilter(source);
    buildDateFilter(source);
    bindFilters();
    applyFilters();
  }

  var list = document.getElementById("blog-posts");
  if (list && list.querySelectorAll(".post-card").length > 0) {
    init([], list);
  } else {
    fetch("./posts.json")
      .then(function (res) {
        if (!res.ok) throw new Error("Failed to load posts");
        return res.json();
      })
      .then(function (data) {
        init(data.posts || [], list);
      })
      .catch(function () {
        if (list) {
          list.innerHTML = "<p class=\"blog-error\">Could not load blog posts. Please refresh the page.</p>";
        }
      });
  }
})();
