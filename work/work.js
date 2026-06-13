(function () {
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

  function init(data) {
    var layout = document.getElementById('work-layout');
    if (!layout) return;

    var projects = data.projects || data;

    layout.innerHTML =
      '<div class="work-main" id="work-cases">' +
        projects.map(renderProject).join('') +
      '</div>';
  }

  fetch('projects.json')
    .then(function (r) { return r.json(); })
    .catch(function () { return { clients: [], projects: [] }; })
    .then(init);
})();
