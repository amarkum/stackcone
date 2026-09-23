// Mobile menu toggle (hamburger, overlay, close button)
var header = document.querySelector('.header');
var navToggle = document.querySelector('.nav-toggle');
var navOverlay = document.getElementById('nav-overlay');

function closeMenu() {
  if (header && header.classList.contains('is-menu-open')) {
    header.classList.remove('is-menu-open');
    if (navToggle) {
      navToggle.setAttribute('aria-expanded', 'false');
      navToggle.setAttribute('aria-label', 'Open menu');
    }
  }
}

if (navToggle && header) {
  navToggle.addEventListener('click', function () {
    var isOpen = header.classList.toggle('is-menu-open');
    navToggle.setAttribute('aria-expanded', isOpen);
    navToggle.setAttribute('aria-label', isOpen ? 'Close menu' : 'Open menu');
  });
}

if (navOverlay) navOverlay.addEventListener('click', closeMenu);

// Nav dropdowns — hover on desktop, accordion on mobile drawer
function initNavDropdowns() {
  var nav = document.getElementById('main-nav');
  if (!nav) return;

  var wraps = nav.querySelectorAll('.nav-dd-wrap');
  var openWrap = null; // the one dropdown allowed to be open at a time

  function setWrapOpen(wrap, trigger, open) {
    clearTimeout(wrap._ddCloseTimer);
    wrap.classList.toggle('is-open', open);
    trigger.setAttribute('aria-expanded', open ? 'true' : 'false');
    openWrap = open ? wrap : (openWrap === wrap ? null : openWrap);
  }

  wraps.forEach(function (wrap) {
    if (wrap.dataset.ddBound) return;
    wrap.dataset.ddBound = "1";
    var trigger = wrap.querySelector('.nav-link--dd');
    if (!trigger) return;

    wrap.addEventListener('mouseenter', function () {
      if (window.innerWidth <= 992) return;
      // Close whatever else is open right now instead of leaving it to its
      // own delayed timer — that let two panels show at once while the
      // mouse moved from one trigger straight to the next.
      if (openWrap && openWrap !== wrap) {
        setWrapOpen(openWrap, openWrap.querySelector('.nav-link--dd'), false);
      }
      setWrapOpen(wrap, trigger, true);
    });

    wrap.addEventListener('mouseleave', function () {
      if (window.innerWidth <= 992) return;
      wrap._ddCloseTimer = setTimeout(function () {
        setWrapOpen(wrap, trigger, false);
      }, 180);
    });

    trigger.addEventListener('click', function (e) {
      if (window.innerWidth > 992) return;
      e.preventDefault();
      e.stopPropagation();
      var isOpen = wrap.classList.toggle('is-open');
      wraps.forEach(function (other) {
        if (other !== wrap) other.classList.remove('is-open');
      });
      trigger.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      openWrap = isOpen ? wrap : null;
    });
  });
}

// Nested Learn submenus: on mobile a tap toggles the section open/closed (accordion);
// the section's own page stays reachable via the "All ..." row inside it.
function initNavSubmenus() {
  var links = document.querySelectorAll('#main-nav .nav-dd-item--sub');
  var openSub = null; // the one submenu allowed to be open at a time (they all live in one panel)

  function setSubOpen(sub, link, open) {
    clearTimeout(sub._subCloseTimer);
    sub.classList.toggle('is-open', open);
    link.setAttribute('aria-expanded', open ? 'true' : 'false');
    openSub = open ? sub : (openSub === sub ? null : openSub);
  }

  links.forEach(function (link) {
    if (link.dataset.subBound) return;
    link.dataset.subBound = '1';
    link.setAttribute('aria-expanded', 'false');
    var sub = link.parentElement;

    sub.addEventListener('mouseenter', function () {
      if (window.innerWidth <= 992) return;
      // Same fix as the top-level dropdowns: close the previously hovered
      // submenu right away instead of letting its own timer linger.
      if (openSub && openSub !== sub) {
        setSubOpen(openSub, openSub.querySelector('.nav-dd-item--sub'), false);
      }
      setSubOpen(sub, link, true);
    });

    sub.addEventListener('mouseleave', function () {
      if (window.innerWidth <= 992) return;
      sub._subCloseTimer = setTimeout(function () {
        setSubOpen(sub, link, false);
      }, 160);
    });

    link.addEventListener('click', function (e) {
      if (window.innerWidth > 992) return;
      e.preventDefault();
      var willOpen = !sub.classList.contains('is-open');
      links.forEach(function (other) {
        other.parentElement.classList.remove('is-open');
        other.setAttribute('aria-expanded', 'false');
      });
      openSub = willOpen ? sub : null;
      if (willOpen) {
        sub.classList.add('is-open');
        link.setAttribute('aria-expanded', 'true');
      }
    });
  });
}

function initNav() {
  initNavDropdowns();
  initNavSubmenus();
}

// site-nav.js may already have rendered the nav before this file loads, so run now if so
document.addEventListener('site-nav-ready', initNav);
if (document.getElementById('main-nav') && document.getElementById('main-nav').innerHTML.trim()) {
  initNav();
}

// Smooth scroll for same-page anchors only
document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
  anchor.addEventListener('click', function (e) {
    var href = this.getAttribute('href');
    if (href === '#') return;
    var target = document.querySelector(href);
    if (!target) return;
    e.preventDefault();
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    closeMenu();
  });
});

// Testimonials: load from data/testimonials.json, render with pagination
var testimonialsFallback = [
  {client:"Alvascience Srl",initial:"A",review:"Would definitely hire again and recommend—ability to understand requirements and a talented individual."},
  {client:"AppLand Inc",initial:"A",review:"Very knowledgeable and professional—would recommend hiring."},
  {client:"Benjamin Hargrave",initial:"B",review:"Top performer—will be working with them long term."},
  {client:"CrossroadsCX",initial:"C",review:"Very talented and great to work with."},
  {client:"Diana Fernandez",initial:"D",review:"Fantastic work, thanks!"},
  {client:"Finer Technologies, Inc.",initial:"F",review:"Perfect!!"}
];

function initTestimonials(testimonials) {
  var grid = document.getElementById('testimonials-grid');
  var paginationEl = document.getElementById('testimonials-pagination');
  if (!grid || !paginationEl) return;
  if (!testimonials || !testimonials.length) testimonials = testimonialsFallback;
  // Reviews from clients with a logo come first; order is otherwise unchanged.
  testimonials = testimonials
    .map(function (t, i) { return { t: t, i: i }; })
    .sort(function (a, b) { return (b.t.logo ? 1 : 0) - (a.t.logo ? 1 : 0) || a.i - b.i; })
    .map(function (x) { return x.t; });
  var perPage = 6;
  var currentPage = 1;

  function renderCard(t) {
    var article = document.createElement('article');
    article.className = 'testimonial-card';
    article.innerHTML =
      '<div class="testimonial-stars" aria-hidden="true">★★★★★</div>' +
      '<p class="testimonial-text">' + escapeHtml(t.review) + '</p>' +
      '<footer class="testimonial-footer">' +
        (t.logo
          ? '<div class="testimonial-avatar testimonial-avatar--logo"><img src="' + escapeHtml(t.logo) + '" alt="' + escapeHtml(t.client) + ' logo" width="40" height="40" loading="lazy"></div>'
          : '<div class="testimonial-avatar" aria-hidden="true">' + escapeHtml(t.initial || 'C') + '</div>') +
        '<div class="testimonial-who">' +
          '<cite class="testimonial-name">' + escapeHtml(t.client) + '</cite>' +
          '<span class="testimonial-source">Verified on Upwork</span>' +
        '</div>' +
      '</footer>';
    return article;
  }

  function escapeHtml(s) {
    var d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  function renderPage() {
    var start = (currentPage - 1) * perPage;
    var slice = testimonials.slice(start, start + perPage);
    grid.innerHTML = '';
    slice.forEach(function (t) {
      grid.appendChild(renderCard(t));
    });
    if (typeof window.revealLandingCards === 'function') {
      window.revealLandingCards(grid);
    }
    renderPagination();
  }

  function renderPagination() {
    var total = testimonials.length;
    var totalPages = Math.ceil(total / perPage) || 1;
    paginationEl.innerHTML = '';
    if (totalPages <= 1) return;

    function addBtn(label, page, isNum) {
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.textContent = label;
      if (isNum) {
        btn.setAttribute('data-page', page);
        if (page === currentPage) btn.classList.add('active');
      }
      btn.addEventListener('click', function () {
        if (this.disabled) return;
        var p = this.getAttribute('data-page');
        if (p) currentPage = parseInt(p, 10);
        else if (label === 'Prev') currentPage = Math.max(1, currentPage - 1);
        else if (label === 'Next') currentPage = Math.min(totalPages, currentPage + 1);
        renderPage();
      });
      if (label === 'Prev') btn.disabled = currentPage <= 1;
      if (label === 'Next') btn.disabled = currentPage >= totalPages;
      paginationEl.appendChild(btn);
    }

    addBtn('Prev');
    var maxButtons = 7;
    var from = Math.max(1, currentPage - 2);
    var to = Math.min(totalPages, from + maxButtons - 1);
    if (to - from < maxButtons - 1) from = Math.max(1, to - maxButtons + 1);
    if (from > 1) {
      addBtn('1', 1, true);
      if (from > 2) {
        var ell = document.createElement('span');
        ell.className = 'pagination-ellipsis';
        ell.textContent = '…';
        paginationEl.appendChild(ell);
      }
    }
    for (var i = from; i <= to; i++) addBtn(String(i), i, true);
    if (to < totalPages) {
      if (to < totalPages - 1) {
        var ell2 = document.createElement('span');
        ell2.className = 'pagination-ellipsis';
        ell2.textContent = '…';
        paginationEl.appendChild(ell2);
      }
      addBtn(String(totalPages), totalPages, true);
    }
    addBtn('Next');
  }

  renderPage();
}

function assetPrefix() {
  var segments = window.location.pathname.replace(/\/$/, '').split('/').filter(Boolean);
  if (segments.length && segments[segments.length - 1].indexOf('.') !== -1) segments.pop();
  return segments.length ? '../'.repeat(segments.length) : '';
}

function loadTestimonials() {
  var grid = document.getElementById('testimonials-grid');
  var paginationEl = document.getElementById('testimonials-pagination');
  if (!grid || !paginationEl) return;

  var staticCount = grid.querySelectorAll('.testimonial-card').length;

  fetch(assetPrefix() + 'data/testimonials.json?v=3')
    .then(function (r) { return r.json(); })
    .then(function (data) {
      var list = Array.isArray(data) ? data : testimonialsFallback;
      if (list.length > staticCount) {
        initTestimonials(list);
      }
    })
    .catch(function () {
      if (staticCount === 0) {
        initTestimonials(testimonialsFallback);
      }
    });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', loadTestimonials);
} else {
  loadTestimonials();
}

// Monaco Editor for syntax-highlighted code blocks (blog, learn, solutions)
(function loadMonacoCode() {
  // Keep in step with the ?v= on learn pages (`/assets/monaco-code.js`).
  var MONACO_ASSET_VERSION = '21';

  function boot() {
    if (window.__stackconeMonacoBooted || window.initMonacoCodeBlocks) {
      if (typeof window.initMonacoCodeBlocks === 'function' && !window.__stackconeMonacoBooted) {
        window.initMonacoCodeBlocks();
      }
      return;
    }

    var hasCode = false;
    document.querySelectorAll('pre > code').forEach(function (code) {
      var pre = code.parentElement;
      if (!pre || pre.classList.contains('mermaid')) return;
      if (pre.closest('.mermaid, .diagram-wrap')) return;
      hasCode = true;
    });
    if (!hasCode) return;

    if (!document.querySelector('link[href*="monaco-code.css"]')) {
      var css = document.createElement('link');
      css.rel = 'stylesheet';
      css.href = '/assets/monaco-code.css?v=' + MONACO_ASSET_VERSION;
      document.head.appendChild(css);
    }
    if (!document.querySelector('script[src*="monaco-code.js"]')) {
      var script = document.createElement('script');
      script.src = '/assets/monaco-code.js?v=' + MONACO_ASSET_VERSION;
      script.defer = true;
      document.body.appendChild(script);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot, { once: true });
  } else {
    boot();
  }
})();

