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

  function renderTechnologies(p) {
    if (!p.technologies || !p.technologies.length) return '';
    return (
      '<div class="case-tech">' +
        '<h3>Technologies used</h3>' +
        '<div class="case-tech-tags">' +
          p.technologies.map(function (tech) {
            return '<span class="case-tech-tag">' + escapeHtml(tech) + '</span>';
          }).join('') +
        '</div>' +
      '</div>'
    );
  }

  function renderClientRow(p) {
    if (!p.client) return '';

    var logos = '';
    if (p.employerLogo) {
      logos += '<img class="case-client-logo" src="' + escapeHtml(logoPath(p.employerLogo)) + '" alt="" width="80" height="28">';
    }
    if (p.endClientLogo) {
      logos += '<img class="case-client-logo" src="' + escapeHtml(logoPath(p.endClientLogo)) + '" alt="" width="80" height="28">';
    }

    var names;
    if (p.endClient && p.endClient !== p.client) {
      names =
        '<span class="case-client-names">' +
          '<strong>' + escapeHtml(p.client) + '</strong>' +
          ' <span class="case-client-sep">·</span> Worked with ' +
          '<strong>' + escapeHtml(p.endClient) + '</strong>' +
        '</span>';
    } else {
      names = '<span class="case-client-names"><strong>' + escapeHtml(p.client) + '</strong></span>';
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
        (logos ? '<div class="case-client-logos">' + logos + '</div>' : '') +
        names +
        meta +
      '</div>'
    );
  }

  function renderProject(p) {
    return (
      '<article class="case-study" id="' + escapeHtml(p.id) + '" data-client="' + escapeHtml(p.client || '') + '">' +
        '<div class="case-header">' +
          '<div class="case-meta">' +
            '<span class="case-tag">' + escapeHtml(p.domain) + '</span>' +
          '</div>' +
          renderClientRow(p) +
          '<h2>' + escapeHtml(p.title) + '</h2>' +
          '<p class="case-lead">' + escapeHtml(p.lead) + '</p>' +
          renderLinks(p) +
        '</div>' +
        '<div class="case-about">' +
          '<h3>About this project</h3>' +
          '<ul>' + listItems(p.implementation) + '</ul>' +
        '</div>' +
        renderTechnologies(p) +
        '<p class="case-outcome"><strong>Outcome:</strong> ' + escapeHtml(p.outcome) + '</p>' +
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
        '<p class="work-clients-label">Clients &amp; employers</p>' +
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

  function renderSidebar(projects) {
    return (
      '<aside class="work-sidebar" aria-label="Project list">' +
        '<p class="work-sidebar-label">Projects</p>' +
        '<nav class="work-sidebar-nav">' +
          projects.map(function (p) {
            var name = p.title.split(' — ')[0];
            return '<a href="#' + escapeHtml(p.id) + '">' + escapeHtml(name) + '</a>';
          }).join('') +
        '</nav>' +
      '</aside>'
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
      '<div class="work-split">' +
        renderSidebar(projects) +
        '<div class="work-main" id="work-cases">' +
          projects.map(renderProject).join('') +
        '</div>' +
      '</div>';

    bindClientFilter();
  }

  fetch('projects.json')
    .then(function (r) { return r.json(); })
    .catch(function () { return { clients: [], projects: [] }; })
    .then(init);
})();
