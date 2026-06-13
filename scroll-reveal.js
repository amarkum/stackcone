(function () {
  if (!document.body.classList.contains("landing-page")) return;

  var prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var header = document.querySelector(".header");
  var hero = document.querySelector(".hero");

  var staggerSelectors = [
    ".section-title",
    ".section-intro",
    ".stack-tabs",
    ".about-lead",
    ".about-body",
    ".about-services",
    ".about-stats",
    ".approach-item",
    ".stack-category",
    ".faq-item",
    ".google-profile-logo",
    ".google-profile-inner",
    ".testimonials-grid",
    ".testimonials-pagination"
  ].join(", ");

  var sections = document.querySelectorAll("main > section:not(.hero)");

  sections.forEach(function (section) {
    var delay = 0;
    section.querySelectorAll(staggerSelectors).forEach(function (el) {
      el.classList.add("reveal-child");
      el.style.setProperty("--reveal-delay", delay * 0.07 + "s");
      delay += 1;
    });
  });

  function revealSection(section) {
    section.querySelectorAll(".reveal-child").forEach(function (child) {
      child.classList.add("is-visible");
    });
  }

  if (!prefersReducedMotion) {
    var revealObserver = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          revealSection(entry.target);
          revealObserver.unobserve(entry.target);
        });
      },
      { threshold: 0.1, rootMargin: "0px 0px -5% 0px" }
    );

    sections.forEach(function (section) {
      revealObserver.observe(section);
    });

    if (hero) {
      var ticking = false;
      window.addEventListener(
        "scroll",
        function () {
          if (ticking) return;
          ticking = true;
          requestAnimationFrame(function () {
            var scrollY = window.scrollY;
            var limit = window.innerHeight;
            if (scrollY < limit) {
              hero.style.transform = "translate3d(0, " + scrollY * 0.22 + "px, 0)";
            } else {
              hero.style.transform = "";
            }
            ticking = false;
          });
        },
        { passive: true }
      );
    }
  } else {
    sections.forEach(revealSection);
  }

  if (header) {
    var onScroll = function () {
      header.classList.toggle("is-scrolled", window.scrollY > 8);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  window.revealLandingCards = function (container) {
    if (prefersReducedMotion || !container) return;
    container.querySelectorAll(".testimonial-card").forEach(function (card, i) {
      card.classList.add("reveal-child");
      card.style.setProperty("--reveal-delay", i * 0.06 + "s");
      requestAnimationFrame(function () {
        card.classList.add("is-visible");
      });
    });
  };
})();
