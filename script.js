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
  var perPage = 6;
  var currentPage = 1;

  function renderCard(t) {
    var article = document.createElement('article');
    article.className = 'testimonial-card';
    article.innerHTML =
      '<span class="testimonial-quote" aria-hidden="true">"</span>' +
      '<span class="testimonial-quote testimonial-quote--end" aria-hidden="true">"</span>' +
      '<div class="testimonial-avatar" aria-hidden="true">' + (t.initial || 'C') + '</div>' +
      '<cite class="testimonial-name">' + escapeHtml(t.client) + '</cite>' +
      '<p class="testimonial-text">' + escapeHtml(t.review) + '</p>' +
      '<div class="testimonial-stars" aria-hidden="true">★★★★★</div>';
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

  fetch(assetPrefix() + 'data/testimonials.json')
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

