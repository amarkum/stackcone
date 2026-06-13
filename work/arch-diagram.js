(function (global) {
  var GREEN = '#14a800';
  var GREY = '#9aaa97';
  var BOX_W = 108;
  var BOX_H = 44;
  var GAP = 28;
  var PAD = 12;

  function strokeForType(type) {
    if (type === 'source' || type === 'consumer') return GREY;
    if (type === 'optional') return GREY;
    return GREEN;
  }

  function dashForType(type) {
    return type === 'optional' ? ' stroke-dasharray="4 3"' : '';
  }

  function arrow(x1, y1, x2, y2) {
    var midY = y1;
    return (
      '<line x1="' + x1 + '" y1="' + midY + '" x2="' + (x2 - 8) + '" y2="' + midY + '" stroke="#5e6d55" stroke-width="1.5"/>' +
      '<polygon points="' + x2 + ',' + midY + ' ' + (x2 - 8) + ',' + (midY - 4) + ' ' + (x2 - 8) + ',' + (midY + 4) + '" fill="#5e6d55"/>'
    );
  }

  function box(node, x, y, projectId, index) {
    var cx = x + BOX_W / 2;
    var cy = y + BOX_H / 2;
    var stroke = strokeForType(node.type);
    var title = node.title.length > 14 ? node.title.slice(0, 13) + '…' : node.title;
    var sub = node.subtitle || '';
    return (
      '<g class="arch-node' + (node.type === 'optional' ? ' arch-node--optional' : '') + '" tabindex="0" role="button" data-project="' + projectId + '" data-index="' + index + '" data-detail="' + escapeAttr(node.detail || node.title) + '">' +
        '<rect x="' + x + '" y="' + y + '" width="' + BOX_W + '" height="' + BOX_H + '" rx="6" fill="#fff" stroke="' + stroke + '" stroke-width="2"' + dashForType(node.type) + '/>' +
        '<text x="' + cx + '" y="' + (cy - 5) + '" text-anchor="middle" font-size="9" font-weight="600" fill="#001e00">' + escapeHtml(title) + '</text>' +
        (sub ? '<text x="' + cx + '" y="' + (cy + 9) + '" text-anchor="middle" font-size="8" fill="#5e6d55">' + escapeHtml(sub) + '</text>' : '') +
      '</g>'
    );
  }

  function escapeHtml(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');
  }

  function escapeAttr(s) {
    return escapeHtml(s);
  }

  function renderDiagram(projectId, architecture) {
    var nodes = architecture.nodes || [];
    if (!nodes.length) return '';

    var totalW = PAD * 2 + nodes.length * BOX_W + (nodes.length - 1) * GAP;
    var h = BOX_H + PAD * 2 + (architecture.orchestration ? 36 : 0);
    var y = PAD + 8;
    var cy = y + BOX_H / 2;
    var parts = [];
    var x = PAD;

    parts.push('<svg class="arch-svg" viewBox="0 0 ' + totalW + ' ' + h + '" xmlns="http://www.w3.org/2000/svg" aria-label="Architecture diagram">');

    for (var i = 0; i < nodes.length; i++) {
      if (i > 0) {
        var prevX = PAD + (i - 1) * (BOX_W + GAP) + BOX_W;
        var nextX = PAD + i * (BOX_W + GAP);
        parts.push(arrow(prevX + 3, cy, nextX - 3, cy));
      }
      parts.push(box(nodes[i], x, y, projectId, i));
      x += BOX_W + GAP;
    }

    if (architecture.orchestration) {
      var barY = y + BOX_H + 14;
      var barX = PAD;
      var barW = totalW - PAD * 2;
      parts.push('<line x1="' + barX + '" y1="' + barY + '" x2="' + (barX + barW) + '" y2="' + barY + '" stroke="#9aaa97" stroke-width="1" stroke-dasharray="4 3"/>');
      parts.push('<text x="' + (barX + barW / 2) + '" y="' + (barY + 14) + '" text-anchor="middle" font-size="8" fill="#5e6d55">' + escapeHtml(architecture.orchestration) + '</text>');
    }

    parts.push('</svg>');
    if (architecture.stack) {
      parts.push('<p class="arch-stack">Stack: ' + escapeHtml(architecture.stack) + '</p>');
    }
    parts.push('<p class="arch-detail" id="arch-detail-' + projectId + '" aria-live="polite">Click a node to see what it does.</p>');
    return parts.join('');
  }

  function bindInteractivity(root) {
    var first = root.querySelector('.arch-node');
    root.querySelectorAll('.arch-node').forEach(function (node) {
      function activate() {
        var projectId = node.getAttribute('data-project');
        var detail = node.getAttribute('data-detail');
        var panel = document.getElementById('arch-detail-' + projectId);
        var wrap = node.closest('.arch-diagram');
        if (wrap) {
          wrap.querySelectorAll('.arch-node').forEach(function (n) { n.classList.remove('is-active'); });
        }
        node.classList.add('is-active');
        if (panel && detail) panel.textContent = detail;
      }
      node.addEventListener('click', activate);
      node.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); activate(); }
      });
    });
    if (first) first.click();
  }

  global.ArchDiagram = {
    render: renderDiagram,
    bind: bindInteractivity
  };
})(window);
