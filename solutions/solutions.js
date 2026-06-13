(function () {
  var categoryFilter = "all";
  var yearFilter = "all";
  var searchQuery = "";

  function escapeHtml(s) {
    var d = document.createElement("div");
    d.textContent = s;
    return d.innerHTML;
  }

  function renderSolution(s) {
    var tags = (s.tags || [])
      .map(function (t) {
        return "<span class=\"tag\">" + escapeHtml(t) + "</span>";
      })
      .join("");

    var searchParts = [s.title, s.description, s.category];
    if (s.client) searchParts.push(s.client);
    if (s.tags) searchParts = searchParts.concat(s.tags);
    var searchText = searchParts.join(" ").toLowerCase();

    var clientLine = s.client
      ? "<div class=\"solution-client\">" + escapeHtml(s.client) + "</div>"
      : "";

    return (
      "<a class=\"post-card solution-card\" href=\"" + escapeHtml(s.href) + "\"" +
        " data-category=\"" + escapeHtml(s.category) + "\"" +
        " data-year=\"" + escapeHtml(s.date.slice(0, 4)) + "\"" +
        " data-tags=\"" + escapeHtml((s.tags || []).join(",")) + "\"" +
        " data-search=\"" + escapeHtml(searchText) + "\">" +
        "<div class=\"post-meta\">By " + escapeHtml(s.author || "Amar Kumar") + "</div>" +
        clientLine +
        "<h2>" + escapeHtml(s.title) + "</h2>" +
        "<p>" + escapeHtml(s.description) + "</p>" +
        "<div class=\"tags\">" + tags + "</div>" +
      "</a>"
    );
  }

  function applyFilters() {
    var cards = document.querySelectorAll(".solution-card");
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

    var empty = document.getElementById("solutions-empty");
    if (empty) empty.classList.toggle("is-hidden", visible > 0);
  }

  function buildCategoryFilter(items) {
    var categories = ["all"];
    items.forEach(function (s) {
      if (categories.indexOf(s.category) < 0) categories.push(s.category);
    });
    categories.sort(function (a, b) {
      if (a === "all") return -1;
      if (b === "all") return 1;
      return a.localeCompare(b);
    });

    var el = document.getElementById("solutions-topic-select");
    if (!el) return;

    el.innerHTML = categories
      .map(function (cat) {
        var label = cat === "all" ? "All topics" : cat;
        return "<option value=\"" + escapeHtml(cat) + "\">" + escapeHtml(label) + "</option>";
      })
      .join("");
  }

  function buildDateFilter(items) {
    var years = items
      .map(function (s) {
        return s.date.slice(0, 4);
      })
      .filter(function (y, i, arr) {
        return arr.indexOf(y) === i;
      })
      .sort(function (a, b) {
        return b.localeCompare(a);
      });

    var el = document.getElementById("solutions-date-select");
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
    var searchEl = document.getElementById("solutions-search");
    var topicEl = document.getElementById("solutions-topic-select");
    var dateEl = document.getElementById("solutions-date-select");

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

  function init(items) {
    var list = document.getElementById("solutions-list");
    if (!list) return;

    if (!items.length) {
      list.innerHTML = "<p class=\"blog-empty\">No solution briefs yet. Paste a problem statement in Cursor to generate one.</p>";
      return;
    }

    list.innerHTML = items.map(renderSolution).join("");
    buildCategoryFilter(items);
    buildDateFilter(items);
    bindFilters();
    applyFilters();
  }

  fetch("./solutions.json")
    .then(function (res) {
      if (!res.ok) throw new Error("Failed to load solutions");
      return res.json();
    })
    .then(function (data) {
      init(data.solutions || []);
    })
    .catch(function () {
      var list = document.getElementById("solutions-list");
      if (list) {
        list.innerHTML = "<p class=\"blog-error\">Could not load solutions. Please refresh the page.</p>";
      }
    });
})();
