(function () {
  function escapeHtml(s) {
    var d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
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

  function renderPhases(p) {
    if (!p.phases) return '';
    var labels = p.phases.labels;
    var values = p.phases.values;
    return (
      '<div class="phase-timeline">' +
        '<h4>Implementation phases</h4>' +
        '<div class="phase-bars">' +
          labels.map(function (label, i) {
            return (
              '<div class="phase-row">' +
                '<span class="phase-label">' + escapeHtml(label) + '</span>' +
                '<div class="phase-track"><div class="phase-fill" style="width:' + values[i] + '%"></div></div>' +
                '<span class="phase-pct">' + values[i] + '%</span>' +
              '</div>'
            );
          }).join('') +
        '</div>' +
      '</div>'
    );
  }

  function renderProject(p) {
    var clientBadge = p.client
      ? '<span class="case-client-badge">' + escapeHtml(p.client) + '</span>'
      : '';
    var upworkLine = p.upwork && typeof p.upwork === 'string'
      ? '<p class="case-upwork">' + escapeHtml(p.upwork) + '</p>'
      : '';
    var archHtml = p.architecture
      ? '<div class="arch-diagram">' + ArchDiagram.render(p.id, p.architecture) + '</div>'
      : '';

    return (
      '<article class="case-study" id="' + escapeHtml(p.id) + '" data-client="' + escapeHtml(p.client || '') + '">' +
        '<div class="case-header">' +
          '<div class="case-meta">' +
            '<span class="case-tag">' + escapeHtml(p.domain) + '</span>' +
            clientBadge +
          '</div>' +
          '<h2>' + escapeHtml(p.title) + '</h2>' +
          upworkLine +
          '<p class="case-lead">' + escapeHtml(p.lead) + '</p>' +
          renderLinks(p) +
        '</div>' +
        archHtml +
        '<div class="case-grid">' +
          '<div class="case-block"><h3>Requirements</h3><ul>' + listItems(p.requirements) + '</ul></div>' +
          '<div class="case-block"><h3>Implementation</h3><ul>' + listItems(p.implementation) + '</ul></div>' +
        '</div>' +
        '<p class="case-outcome"><strong>Outcome:</strong> ' + escapeHtml(p.outcome) + '</p>' +
        renderPhases(p) +
      '</article>'
    );
  }

  function uniqueClients(projects) {
    var seen = {};
    var list = [];
    projects.forEach(function (p) {
      if (p.client && !seen[p.client]) {
        seen[p.client] = true;
        list.push(p.client);
      }
    });
    return list;
  }

  function renderClientFilter(clients) {
    return (
      '<div class="work-clients">' +
        '<p class="work-clients-label">Clients</p>' +
        '<div class="work-clients-list">' +
          '<button type="button" class="client-pill is-active" data-client="all">All projects</button>' +
          clients.map(function (c) {
            return '<button type="button" class="client-pill" data-client="' + escapeHtml(c) + '">' + escapeHtml(c) + '</button>';
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

  function init(projects) {
    var layout = document.getElementById('work-layout');
    if (!layout) return;

    var clients = uniqueClients(projects);
    layout.innerHTML =
      renderClientFilter(clients) +
      '<div class="work-split">' +
        renderSidebar(projects) +
        '<div class="work-main" id="work-cases">' +
          projects.map(renderProject).join('') +
        '</div>' +
      '</div>';

    document.querySelectorAll('.arch-diagram').forEach(function (el) {
      ArchDiagram.bind(el);
    });
    bindClientFilter();
  }

  fetch('projects.json')
    .then(function (r) { return r.json(); })
    .catch(function () { return []; })
    .then(init);
})();
