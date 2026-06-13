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

  function normalizeClients(data) {
    if (data.clients && data.clients.length && typeof data.clients[0] === 'object') {
      return data.clients;
    }
    return (data.clients || []).map(function (name) {
      return { name: name, logo: null };
    });
  }

  function renderClientFilter(clients) {
    return (
      '<div class="work-clients">' +
        '<p class="work-clients-label">Clients</p>' +
        '<div class="work-clients-list">' +
          '<button type="button" class="client-pill is-active" data-client="all">All projects</button>' +
          clients.map(function (c) {
            var logoHtml = c.logo
              ? '<img src="' + escapeHtml(logoPath(c.logo)) + '" alt="" width="56" height="20" class="client-pill-logo">'
              : '';
            return (
              '<button type="button" class="client-pill' + (c.logo ? ' client-pill--has-logo' : '') + '" data-client="' + escapeHtml(c.name) + '">' +
                logoHtml +
                '<span>' + escapeHtml(c.name) + '</span>' +
              '</button>'
            );
          }).join('') +
        '</div>' +
      '</div>'
    );
  }

  function bindClientFilter() {
    var pills = document.querySelectorAll('.client-pill');
    var studies = document.querySelectorAll('.case-study');
    pills.forEach(function (pill) {
      pill.addEventListener('click', function () {
        var client = pill.getAttribute('data-client');
        pills.forEach(function (p) { p.classList.remove('is-active'); });
        pill.classList.add('is-active');
        studies.forEach(function (study) {
          var match = client === 'all' || study.getAttribute('data-client') === client;
          study.classList.toggle('is-hidden', !match);
        });
      });
    });
  }

  function init(data) {
    var layout = document.getElementById('work-layout');
    if (!layout) return;

    var projects = data.projects || data;
    var clients = normalizeClients(data);

    layout.innerHTML =
      renderClientFilter(clients) +
      '<div class="work-main" id="work-cases">' +
        projects.map(renderProject).join('') +
      '</div>';

    bindClientFilter();
  }

  fetch('projects.json')
    .then(function (r) { return r.json(); })
    .catch(function () { return { clients: [], projects: [] }; })
    .then(init);
})();
