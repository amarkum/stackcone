(function () {
  var PER_PAGE = 3;
  var currentPage = 0;
  var allProjects = [];

  var PROJECT_ORDER = [
    'cabinetsense',
    'internal-copilot',
    'ai-invoice-bot',
    'llm-training-review',
    'gcp-dataflow-bq',
    'rest-api-partners',
    'aadhya-self-drive',
    'rag-knowledge-base',
    'hadoop-gcp-migration',
    'ml-feature-pipeline',
    'pipeline-dashboard',
    'elk-stack',
    'portfolio-accounting',
    'investment-bank-desktop',
    'clinical-etl',
    'data-governance'
  ];

  function escapeHtml(s) {
    var d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  function logoPath(filename) {
    if (!filename) return '';
    return '../assets/clients/' + filename;
  }

  function listItems(items) {
    return items.map(function (item) {
      return '<li>' + escapeHtml(item) + '</li>';
    }).join('');
  }

  function sortProjects(projects) {
    var byId = {};
    projects.forEach(function (p) {
      byId[p.id] = p;
    });
    var ordered = PROJECT_ORDER.filter(function (id) {
      return byId[id];
    });
    projects.forEach(function (p) {
      if (ordered.indexOf(p.id) < 0) ordered.push(p.id);
    });
    return ordered.map(function (id) {
      return byId[id];
    });
  }

  function renderLinks(p) {
    if (!p.links || !p.links.length) return '';
    return (
      '<div class="case-links">' +
        p.links.map(function (link) {
          return '<a href="' + escapeHtml(link.url) + '" rel="noopener noreferrer" target="_blank">' + escapeHtml(link.label) + '</a>';
        }).join('') +
      '</div>'
    );
  }

  function renderTechStack(p) {
    var hasTags = p.technologies && p.technologies.length;
    var hasDomain = p.domain;
    if (!hasTags && !hasDomain) return '';

    var summary = hasDomain
      ? '<p class="case-tech-summary">' + escapeHtml(p.domain) + '</p>'
      : '';

    var tags = hasTags
      ? '<div class="case-tech-tags">' +
          p.technologies.map(function (tech) {
            return '<span class="case-tech-tag">' + escapeHtml(tech) + '</span>';
          }).join('') +
        '</div>'
      : '';

    return (
      '<div class="case-tech">' +
        '<h3>Tech stack</h3>' +
        summary +
        tags +
      '</div>'
    );
  }

  function renderClientRow(p) {
    if (!p.client) return '';

    var logos = '';
    if (p.endClientLogo) {
      logos =
        '<div class="case-client-logos">' +
          '<img class="case-client-logo" src="' + escapeHtml(logoPath(p.endClientLogo)) + '" alt="" width="80" height="28">' +
        '</div>';
    }

    var names;
    if (p.endClient && p.endClient !== p.client) {
      names =
        '<span class="case-client-names">' +
          'Employed at ' + escapeHtml(p.client) +
          ' <span class="case-client-sep">·</span> Client: ' +
          '<strong>' + escapeHtml(p.endClient) + '</strong>' +
        '</span>';
    } else if (p.employer) {
      names = '<span class="case-client-names">Employed at <strong>' + escapeHtml(p.client) + '</strong></span>';
    } else {
      names = '<span class="case-client-names">Client: <strong>' + escapeHtml(p.client) + '</strong></span>';
    }

    var meta = '';
    if (p.role || p.period) {
      meta =
        '<p class="case-role">' +
          (p.role ? escapeHtml(p.role) : '') +
          (p.role && p.period ? ' · ' : '') +
          (p.period ? escapeHtml(p.period) : '') +
        '</p>';
    }

    return (
      '<div class="case-client-row">' +
        logos +
        names +
        meta +
      '</div>'
    );
  }

  function renderBrief(p) {
    if (!p.brief) return '';
    var label = p.briefType === 'requirement' ? 'Requirement' : 'Problem';
    return (
      '<div class="case-brief">' +
        '<h3>' + escapeHtml(label) + '</h3>' +
        '<p>' + escapeHtml(p.brief) + '</p>' +
      '</div>'
    );
  }

  function renderProject(p) {
    return (
      '<article class="case-study" id="' + escapeHtml(p.id) + '" data-client="' + escapeHtml(p.client || '') + '">' +
        '<div class="case-header">' +
          renderClientRow(p) +
          '<h2>' + escapeHtml(p.title) + '</h2>' +
          renderLinks(p) +
        '</div>' +
        renderBrief(p) +
        '<div class="case-about">' +
          '<h3>What we built</h3>' +
          '<ul>' + listItems(p.implementation) + '</ul>' +
        '</div>' +
        renderTechStack(p) +
      '</article>'
    );
  }

  function totalPages() {
    return Math.max(1, Math.ceil(allProjects.length / PER_PAGE));
  }

  function renderPage() {
    var casesEl = document.getElementById('work-cases');
    if (!casesEl) return;

    var start = currentPage * PER_PAGE;
    var pageProjects = allProjects.slice(start, start + PER_PAGE);
    casesEl.innerHTML = pageProjects.map(renderProject).join('');
    renderPagination();

    var layout = document.getElementById('work-layout');
    if (layout && currentPage > 0) {
      layout.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  function renderPagination() {
    var el = document.getElementById('work-pagination');
    if (!el) return;

    var total = totalPages();
    if (total <= 1) {
      el.innerHTML = '';
      el.hidden = true;
      return;
    }

    el.hidden = false;
    var html = '';

    html += '<button type="button" data-page="prev"' + (currentPage === 0 ? ' disabled' : '') + '>Previous</button>';

    for (var i = 0; i < total; i += 1) {
      var active = i === currentPage ? ' class="active"' : '';
      html += '<button type="button" data-page="' + i + '"' + active + '>' + (i + 1) + '</button>';
    }

    html += '<button type="button" data-page="next"' + (currentPage >= total - 1 ? ' disabled' : '') + '>Next</button>';

    el.innerHTML = html;

    el.querySelectorAll('button[data-page]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var action = btn.getAttribute('data-page');
        if (action === 'prev' && currentPage > 0) {
          currentPage -= 1;
          renderPage();
        } else if (action === 'next' && currentPage < total - 1) {
          currentPage += 1;
          renderPage();
        } else if (action !== 'prev' && action !== 'next') {
          currentPage = parseInt(action, 10);
          renderPage();
        }
      });
    });
  }

  function init(data) {
    var layout = document.getElementById('work-layout');
    if (!layout) return;

    allProjects = sortProjects(data.projects || data);
    currentPage = 0;

    layout.innerHTML =
      '<div class="work-main">' +
        '<div id="work-cases" class="work-cases"></div>' +
        '<nav class="work-pagination" id="work-pagination" aria-label="Case study pagination"></nav>' +
      '</div>';

    renderPage();
  }

  fetch('projects.json')
    .then(function (r) { return r.json(); })
    .catch(function () { return { clients: [], projects: [] }; })
    .then(init);
})();
