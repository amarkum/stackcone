(function () {
  var archColors = ['#2563eb', '#7c3aed', '#db2777', '#ea580c', '#16a34a', '#0891b2'];
  var phaseColors = ['#93c5fd', '#60a5fa', '#2563eb', '#1d4ed8', '#1e3a8a'];

  Chart.defaults.font.family = "'DM Sans', system-ui, sans-serif";
  Chart.defaults.color = '#6b6b6b';
  Chart.defaults.plugins.legend.display = false;

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

  function renderProject(p) {
    var clientLine = p.client
      ? '<p class="case-client">Client: <a href="' + escapeHtml(p.clientUrl || '#') + '" rel="noopener noreferrer" target="_blank">' + escapeHtml(p.client) + '</a></p>'
      : '';
    return (
      '<article class="case-study" id="' + escapeHtml(p.id) + '">' +
        '<div class="case-header">' +
          '<div class="case-meta"><span class="case-tag">' + escapeHtml(p.domain) + '</span></div>' +
          '<h2>' + escapeHtml(p.title) + '</h2>' +
          clientLine +
          '<p class="case-lead">' + escapeHtml(p.lead) + '</p>' +
          renderLinks(p) +
        '</div>' +
        '<div class="case-grid">' +
          '<div class="case-block"><h3>Requirements</h3><ul>' + listItems(p.requirements) + '</ul></div>' +
          '<div class="case-block"><h3>Implementation</h3><ul>' + listItems(p.implementation) + '</ul></div>' +
        '</div>' +
        '<p class="case-outcome"><strong>Outcome:</strong> ' + escapeHtml(p.outcome) + '</p>' +
        '<div class="case-charts">' +
          '<div class="chart-panel">' +
            '<h4>Architecture flow</h4>' +
            '<canvas id="arch-' + escapeHtml(p.id) + '" aria-label="Architecture diagram for ' + escapeHtml(p.title) + '"></canvas>' +
            '<p class="chart-caption">Data and control flow across system layers (relative weight)</p>' +
          '</div>' +
          '<div class="chart-panel">' +
            '<h4>Implementation phases</h4>' +
            '<canvas id="phase-' + escapeHtml(p.id) + '" aria-label="Implementation phases for ' + escapeHtml(p.title) + '"></canvas>' +
            '<p class="chart-caption">Effort split: requirements through handover</p>' +
          '</div>' +
        '</div>' +
      '</article>'
    );
  }

  function renderNav(projects) {
    return projects.map(function (p) {
      return '<a href="#' + escapeHtml(p.id) + '">' + escapeHtml(p.title.split(' — ')[0]) + '</a>';
    }).join('');
  }

  function createArchChart(canvasId, project) {
    var el = document.getElementById(canvasId);
    if (!el) return;
    new Chart(el, {
      type: 'bar',
      data: {
        labels: project.arch.labels,
        datasets: [{
          label: 'Layer weight',
          data: project.arch.values,
          backgroundColor: project.arch.labels.map(function (_, i) {
            return archColors[i % archColors.length];
          }),
          borderRadius: 4
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: true,
        scales: {
          x: {
            beginAtZero: true,
            max: 35,
            grid: { color: '#ebebeb' },
            ticks: { display: false }
          },
          y: {
            grid: { display: false },
            ticks: { font: { size: 11 } }
          }
        },
        plugins: {
          tooltip: {
            callbacks: {
              label: function (ctx) {
                return ctx.label + ': layer ' + (ctx.raw + 1);
              }
            }
          }
        }
      }
    });
  }

  function createPhaseChart(canvasId, project) {
    var el = document.getElementById(canvasId);
    if (!el) return;
    new Chart(el, {
      type: 'doughnut',
      data: {
        labels: project.phases.labels,
        datasets: [{
          data: project.phases.values,
          backgroundColor: phaseColors,
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        cutout: '55%',
        plugins: {
          legend: {
            display: true,
            position: 'bottom',
            labels: { boxWidth: 10, font: { size: 10 }, padding: 8 }
          },
          tooltip: {
            callbacks: {
              label: function (ctx) {
                return ctx.label + ': ' + ctx.raw + '%';
              }
            }
          }
        }
      }
    });
  }

  function init(projects) {
    var nav = document.getElementById('work-nav');
    var cases = document.getElementById('work-cases');
    if (!nav || !cases) return;

    nav.innerHTML = renderNav(projects);
    cases.innerHTML = projects.map(renderProject).join('');

    projects.forEach(function (p) {
      createArchChart('arch-' + p.id, p);
      createPhaseChart('phase-' + p.id, p);
    });
  }

  fetch('projects.json')
    .then(function (r) { return r.json(); })
    .catch(function () { return []; })
    .then(init);
})();
