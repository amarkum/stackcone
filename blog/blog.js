(function () {
  var categoryFilter = "all";
  var yearFilter = "all";

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

    return (
      "<a class=\"post-card\" href=\"" + escapeHtml(p.href) + "\" data-category=\"" + escapeHtml(p.category) + "\" data-year=\"" + escapeHtml(p.date.slice(0, 4)) + "\" data-tags=\"" + escapeHtml(p.tags.join(",")) + "\">" +
        "<div class=\"post-meta\">" + escapeHtml(p.dateLabel) + " · Published by " + escapeHtml(p.author) + "</div>" +
        "<h2>" + escapeHtml(p.title) + "</h2>" +
        "<p>" + escapeHtml(p.description) + "</p>" +
        "<div class=\"tags\">" + tags + "</div>" +
      "</a>"
    );
  }

  function applyFilters() {
    var cards = document.querySelectorAll(".post-card");
    var visible = 0;

    cards.forEach(function (card) {
      var cat = card.getAttribute("data-category");
      var year = card.getAttribute("data-year");
      var tags = (card.getAttribute("data-tags") || "").split(",");
      var catMatch =
        categoryFilter === "all" ||
        cat === categoryFilter ||
        tags.indexOf(categoryFilter) >= 0;
      var yearMatch = yearFilter === "all" || year === yearFilter;
      var show = catMatch && yearMatch;
      card.classList.toggle("is-hidden", !show);
      if (show) visible += 1;
    });

    var empty = document.getElementById("blog-empty");
    if (empty) empty.classList.toggle("is-hidden", visible > 0);
  }

  function setActivePill(group, value) {
    document.querySelectorAll(".blog-filter-pill[data-filter=\"" + group + "\"]").forEach(function (btn) {
      btn.classList.toggle("is-active", btn.getAttribute("data-value") === value);
    });
  }

  function buildCategoryFilters(posts) {
    var topics = ["all"];
    posts.forEach(function (p) {
      if (topics.indexOf(p.category) < 0) topics.push(p.category);
      p.tags.forEach(function (t) {
        if (topics.indexOf(t) < 0) topics.push(t);
      });
    });

    var el = document.getElementById("blog-category-filters");
    if (!el) return;

    el.innerHTML = topics
      .map(function (topic) {
        var label = topic === "all" ? "All topics" : topic;
        var active = topic === "all" ? " is-active" : "";
        return (
          "<button type=\"button\" class=\"blog-filter-pill" + active + "\" data-filter=\"category\" data-value=\"" + escapeHtml(topic) + "\">" +
            escapeHtml(label) +
          "</button>"
        );
      })
      .join("");
  }

  function buildDateFilters(posts) {
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

    var el = document.getElementById("blog-date-filters");
    if (!el) return;

    var buttons = [
      "<button type=\"button\" class=\"blog-filter-pill is-active\" data-filter=\"year\" data-value=\"all\">All time</button>"
    ];

    years.forEach(function (year) {
      buttons.push(
        "<button type=\"button\" class=\"blog-filter-pill\" data-filter=\"year\" data-value=\"" + escapeHtml(year) + "\">" + escapeHtml(year) + "</button>"
      );
    });

    el.innerHTML = buttons.join("");
  }

  function bindFilters() {
    document.querySelectorAll(".blog-filter-pill").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var group = btn.getAttribute("data-filter");
        var value = btn.getAttribute("data-value");
        if (group === "category") {
          categoryFilter = value;
          setActivePill("category", value);
        } else if (group === "year") {
          yearFilter = value;
          setActivePill("year", value);
        }
        applyFilters();
      });
    });
  }

  function renderFeatured(posts) {
    var featured = posts.filter(function (p) {
      return p.featured;
    });
    var block = document.getElementById("blog-featured-block");
    var el = document.getElementById("blog-featured");
    if (!el || !block) return;

    if (!featured.length) {
      block.classList.add("is-hidden");
      return;
    }

    block.classList.remove("is-hidden");
    el.innerHTML = featured
      .map(function (p) {
        return (
          "<a class=\"blog-featured-link\" href=\"" + escapeHtml(p.href) + "\">" +
            "<span class=\"blog-featured-title\">" + escapeHtml(p.title) + "</span>" +
            "<span class=\"blog-featured-meta\">" + escapeHtml(p.dateLabel) + "</span>" +
          "</a>"
        );
      })
      .join("");
  }

  function init(posts) {
    var list = document.getElementById("blog-posts");
    if (!list) return;

    list.innerHTML = posts.map(renderPost).join("");
    buildCategoryFilters(posts);
    buildDateFilters(posts);
    renderFeatured(posts);
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
