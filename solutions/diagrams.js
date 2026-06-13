/* Fullscreen controls + explicit Mermaid render for solution diagrams */
(function () {
  var LIGHTBOX_ID = "diagram-lightbox";
  var ZOOM_STEP = 1.2;
  var MIN_SCALE = 0.15;
  var MAX_SCALE = 5;
  function lucideIcon(paths) {
    return (
      "<svg width=\"16\" height=\"16\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\" aria-hidden=\"true\">" +
      paths +
      "</svg>"
    );
  }

  var ICONS = {
    zoomIn: lucideIcon(
      "<circle cx=\"11\" cy=\"11\" r=\"8\"/>" +
      "<line x1=\"21\" y1=\"21\" x2=\"16.65\" y2=\"16.65\"/>" +
      "<line x1=\"11\" y1=\"8\" x2=\"11\" y2=\"14\"/>" +
      "<line x1=\"8\" y1=\"11\" x2=\"14\" y2=\"11\"/>"
    ),
    zoomOut: lucideIcon(
      "<circle cx=\"11\" cy=\"11\" r=\"8\"/>" +
      "<line x1=\"21\" y1=\"21\" x2=\"16.65\" y2=\"16.65\"/>" +
      "<line x1=\"8\" y1=\"11\" x2=\"14\" y2=\"11\"/>"
    ),
    fit: lucideIcon(
      "<path d=\"M8 3H5a2 2 0 0 0-2 2v3\"/>" +
      "<path d=\"M21 8V5a2 2 0 0 0-2-2h-3\"/>" +
      "<path d=\"M3 16v3a2 2 0 0 0 2 2h3\"/>" +
      "<path d=\"M16 21h3a2 2 0 0 0 2-2v-3\"/>"
    ),
    pan: lucideIcon(
      "<path d=\"M18 11V6a2 2 0 0 0-2-2a2 2 0 0 0-2 2\"/>" +
      "<path d=\"M14 10V4a2 2 0 0 0-2-2a2 2 0 0 0-2 2v2\"/>" +
      "<path d=\"M10 10.5V6a2 2 0 0 0-2-2a2 2 0 0 0-2 2v8\"/>" +
      "<path d=\"M18 8a2 2 0 1 1 4 0v6a8 8 0 0 1-8 8h-2c-2.8 0-4.5-.86-5.99-2.34l-3.6-3.6a2 2 0 0 1 2.83-2.82L7 15\"/>"
    ),
    close: lucideIcon(
      "<path d=\"M18 6 6 18\"/>" +
      "<path d=\"m6 6 12 12\"/>"
    )
  };

  function getMermaid() {
    var api = window.mermaid;
    if (!api) return null;
    if (api.default && typeof api.default.initialize === "function") return api.default;
    return api;
  }

  function findDiagramNodes() {
    return Array.from(
      document.querySelectorAll(
        ".diagram-wrap .mermaid-pending, .diagram-wrap pre.mermaid, .diagram-wrap .mermaid"
      )
    );
  }

  function parseRenderResult(result) {
    if (typeof result === "string") return { svg: result, bindFunctions: null };
    if (result && result.svg) return result;
    return { svg: "", bindFunctions: null };
  }

  window.StackconeMermaidConfig = {
    startOnLoad: false,
    securityLevel: "loose",
    theme: "base",
    themeVariables: {
      fontFamily: "DM Sans, system-ui, sans-serif",
      fontSize: "12px",
      mainBkg: "#ffffff",
      background: "#ffffff",
      primaryColor: "#f8fafc",
      primaryTextColor: "#0a0a0a",
      primaryBorderColor: "#d4d4d4",
      lineColor: "#525252",
      actorBkg: "#f8fafc",
      actorTextColor: "#0a0a0a",
      actorLineColor: "#525252",
      signalColor: "#525252",
      signalTextColor: "#0a0a0a",
      labelBoxBkgColor: "#fafafa",
      labelBoxBorderColor: "#d4d4d4",
      labelTextColor: "#0a0a0a"
    },
    flowchart: {
      useMaxWidth: false,
      curve: "basis",
      padding: 20,
      htmlLabels: true,
      nodeSpacing: 48,
      rankSpacing: 52,
      wrappingWidth: 220
    },
    sequence: {
      useMaxWidth: false,
      actorMargin: 40,
      messageMargin: 32,
      boxMargin: 10,
      wrap: true
    }
  };

  function ensureLightbox() {
    if (document.getElementById(LIGHTBOX_ID)) return;

    var lb = document.createElement("div");
    lb.id = LIGHTBOX_ID;
    lb.className = "diagram-lightbox";
    lb.hidden = true;
    lb.innerHTML =
      "<div class=\"diagram-lightbox-backdrop\" data-diagram-close></div>" +
      "<div class=\"diagram-lightbox-panel\" role=\"dialog\" aria-modal=\"true\" aria-labelledby=\"diagram-lightbox-title\">" +
        "<div class=\"diagram-lightbox-header\">" +
          "<h3 id=\"diagram-lightbox-title\" class=\"diagram-lightbox-title\"></h3>" +
          "<div class=\"diagram-lightbox-tools\">" +
            "<button type=\"button\" class=\"diagram-tool-btn\" data-diagram-zoom-out aria-label=\"Zoom out\" title=\"Zoom out (−)\">" + ICONS.zoomOut + "</button>" +
            "<button type=\"button\" class=\"diagram-tool-btn\" data-diagram-zoom-in aria-label=\"Zoom in\" title=\"Zoom in (+)\">" + ICONS.zoomIn + "</button>" +
            "<button type=\"button\" class=\"diagram-tool-btn\" data-diagram-fit aria-label=\"Fit to screen\" title=\"Fit to screen (0)\">" + ICONS.fit + "</button>" +
            "<button type=\"button\" class=\"diagram-tool-btn diagram-tool-btn--pan is-active\" data-diagram-pan aria-label=\"Pan mode\" title=\"Drag to pan\" aria-pressed=\"true\">" + ICONS.pan + "</button>" +
          "</div>" +
          "<button type=\"button\" class=\"diagram-lightbox-close\" data-diagram-close aria-label=\"Close (Esc)\" title=\"Close (Esc)\">" + ICONS.close + "</button>" +
        "</div>" +
        "<div class=\"diagram-lightbox-stage\" data-diagram-stage>" +
          "<div class=\"diagram-lightbox-canvas\" data-diagram-canvas></div>" +
        "</div>" +
      "</div>";
    document.body.appendChild(lb);

    lb.querySelectorAll("[data-diagram-close]").forEach(function (el) {
      el.addEventListener("click", closeLightbox);
    });

    lb.querySelector("[data-diagram-zoom-in]").addEventListener("click", function () {
      zoomLightbox(ZOOM_STEP);
    });
    lb.querySelector("[data-diagram-zoom-out]").addEventListener("click", function () {
      zoomLightbox(1 / ZOOM_STEP);
    });
    lb.querySelector("[data-diagram-fit]").addEventListener("click", fitLightboxToScreen);
    lb.querySelector("[data-diagram-pan]").addEventListener("click", togglePanMode);

    var stage = lb.querySelector("[data-diagram-stage]");
    stage.addEventListener("mousedown", onPanStart);
    stage.addEventListener("touchstart", onPanStart, { passive: false });

    document.addEventListener("mousemove", onPanMove);
    document.addEventListener("mouseup", onPanEnd);
    document.addEventListener("touchmove", onPanMove, { passive: false });
    document.addEventListener("touchend", onPanEnd);
    document.addEventListener("keydown", onLightboxKeydown);
  }

  function onLightboxKeydown(e) {
    var lb = document.getElementById(LIGHTBOX_ID);
    if (!lb || lb.hidden) return;
    if (e.key === "Escape") closeLightbox();
    if (e.key === "+" || e.key === "=") zoomLightbox(ZOOM_STEP);
    if (e.key === "-") zoomLightbox(1 / ZOOM_STEP);
    if (e.key === "0") fitLightboxToScreen();
  }

  function getLightboxEls() {
    var lb = document.getElementById(LIGHTBOX_ID);
    if (!lb) return null;
    return {
      lb: lb,
      stage: lb.querySelector("[data-diagram-stage]"),
      canvas: lb.querySelector("[data-diagram-canvas]"),
      panBtn: lb.querySelector("[data-diagram-pan]")
    };
  }

  function applyLightboxTransform() {
    if (!lightboxState) return;
    lightboxState.canvas.style.transform =
      "translate(" + lightboxState.x + "px, " + lightboxState.y + "px) scale(" + lightboxState.scale + ")";
  }

  function getSvgDimensions(svg) {
    svg.removeAttribute("style");
    var bbox = svg.getBBox();
    var w = bbox.width;
    var h = bbox.height;
    if (!w || !h) {
      var rect = svg.getBoundingClientRect();
      w = rect.width;
      h = rect.height;
    }
    return { w: w, h: h };
  }

  function fitLightboxToScreen() {
    var els = getLightboxEls();
    if (!els || !lightboxState) return;

    var svg = els.canvas.querySelector("svg");
    if (!svg) return;

    var dims = getSvgDimensions(svg);
    if (!dims.w || !dims.h) return;

    var pad = 40;
    var vw = els.stage.clientWidth - pad;
    var vh = els.stage.clientHeight - pad;
    if (!vw || !vh) return;

    var scale = Math.min(vw / dims.w, vh / dims.h);
    lightboxState.baseW = dims.w;
    lightboxState.baseH = dims.h;
    lightboxState.scale = Math.max(MIN_SCALE, Math.min(scale, MAX_SCALE));
    lightboxState.x = (els.stage.clientWidth - dims.w * lightboxState.scale) / 2;
    lightboxState.y = (els.stage.clientHeight - dims.h * lightboxState.scale) / 2;
    applyLightboxTransform();
  }

  function zoomLightbox(factor) {
    var els = getLightboxEls();
    if (!els || !lightboxState) return;

    var cx = els.stage.clientWidth / 2;
    var cy = els.stage.clientHeight / 2;
    var px = (cx - lightboxState.x) / lightboxState.scale;
    var py = (cy - lightboxState.y) / lightboxState.scale;

    lightboxState.scale = Math.max(MIN_SCALE, Math.min(MAX_SCALE, lightboxState.scale * factor));
    lightboxState.x = cx - px * lightboxState.scale;
    lightboxState.y = cy - py * lightboxState.scale;
    applyLightboxTransform();
  }

  function togglePanMode() {
    var els = getLightboxEls();
    if (!els || !lightboxState) return;

    lightboxState.panActive = !lightboxState.panActive;
    els.panBtn.classList.toggle("is-active", lightboxState.panActive);
    els.panBtn.setAttribute("aria-pressed", lightboxState.panActive ? "true" : "false");
    els.stage.classList.toggle("is-pan-enabled", lightboxState.panActive);
  }

  function onPanStart(e) {
    if (!lightboxState || !lightboxState.panActive) return;
    if (e.type === "mousedown" && e.button !== 0) return;

    var point = e.touches ? e.touches[0] : e;
    lightboxState.dragging = true;
    lightboxState.startX = point.clientX;
    lightboxState.startY = point.clientY;
    lightboxState.startPanX = lightboxState.x;
    lightboxState.startPanY = lightboxState.y;

    var els = getLightboxEls();
    if (els) els.stage.classList.add("is-dragging");

    if (e.type === "touchstart") e.preventDefault();
  }

  function onPanMove(e) {
    if (!lightboxState || !lightboxState.dragging) return;

    var point = e.touches ? e.touches[0] : e;
    lightboxState.x = lightboxState.startPanX + (point.clientX - lightboxState.startX);
    lightboxState.y = lightboxState.startPanY + (point.clientY - lightboxState.startY);
    applyLightboxTransform();

    if (e.type === "touchmove") e.preventDefault();
  }

  function onPanEnd() {
    if (!lightboxState) return;
    lightboxState.dragging = false;
    var els = getLightboxEls();
    if (els) els.stage.classList.remove("is-dragging");
  }

  function closeLightbox() {
    var lb = document.getElementById(LIGHTBOX_ID);
    if (!lb) return;
    lb.hidden = true;
    var canvas = lb.querySelector("[data-diagram-canvas]");
    if (canvas) canvas.innerHTML = "";
    lightboxState = null;
    document.body.style.overflow = "";
  }

  function openLightbox(title, mermaidEl) {
    ensureLightbox();
    var els = getLightboxEls();
    if (!els) return;

    els.lb.querySelector(".diagram-lightbox-title").textContent = title || "Diagram";
    els.canvas.innerHTML = "";
    els.canvas.appendChild(mermaidEl.cloneNode(true));

    lightboxState = {
      canvas: els.canvas,
      scale: 1,
      x: 0,
      y: 0,
      baseW: 0,
      baseH: 0,
      panActive: true,
      dragging: false
    };

    els.panBtn.classList.add("is-active");
    els.panBtn.setAttribute("aria-pressed", "true");
    els.stage.classList.add("is-pan-enabled");
    els.canvas.style.transformOrigin = "0 0";

    els.lb.hidden = false;
    document.body.style.overflow = "hidden";

    requestAnimationFrame(function () {
      requestAnimationFrame(fitLightboxToScreen);
    });
  }

  function showDiagramError(wrap, message) {
    var body = wrap.querySelector(".diagram-body");
    if (!body) return;
    body.innerHTML = "<p class=\"diagram-error\">Could not render diagram. " + message + "</p>";
  }

  function fitDiagramBody(body) {
    var mermaidEl = body.querySelector(".mermaid-pending.is-rendered");
    if (!mermaidEl) return;

    var svg = mermaidEl.querySelector("svg");
    if (!svg) return;

    mermaidEl.style.width = "";
    mermaidEl.style.height = "";
    mermaidEl.style.margin = "0 auto";
    mermaidEl.style.maxWidth = "100%";

    svg.style.width = "100%";
    svg.style.height = "auto";
    svg.style.maxWidth = "100%";
    svg.style.overflow = "visible";
  }

  function fitAllDiagrams() {
    document.querySelectorAll(".diagram-wrap .diagram-body").forEach(fitDiagramBody);
  }

  var MAXIMIZE_ICON = lucideIcon(
    "<path d=\"m15 15 6 6\"/>" +
    "<path d=\"m15 9 6-6\"/>" +
    "<path d=\"M21 16v5h-5\"/>" +
    "<path d=\"M21 8V3h-5\"/>" +
    "<path d=\"M3 16v5h5\"/>" +
    "<path d=\"m3 21 6-6\"/>" +
    "<path d=\"M3 8V3h5\"/>" +
    "<path d=\"M9 9 3 3\"/>"
  );

  function openDiagramLightbox(wrap) {
    var title =
      wrap.getAttribute("data-diagram-title") ||
      (wrap.querySelector(".diagram-caption") && wrap.querySelector(".diagram-caption").textContent.trim()) ||
      "Diagram";
    var mermaidEl = wrap.querySelector(".mermaid-pending.is-rendered");
    if (mermaidEl && mermaidEl.querySelector("svg")) {
      openLightbox(title, mermaidEl);
    }
  }

  function wireMaximizeButton(wrap) {
    var btn = wrap.querySelector(".diagram-maximize");
    if (!btn) {
      btn = document.createElement("button");
      btn.type = "button";
      btn.className = "diagram-maximize";
      btn.setAttribute("aria-label", "View diagram fullscreen");
      btn.title = "Fullscreen";
      btn.innerHTML = MAXIMIZE_ICON;
      wrap.insertBefore(btn, wrap.firstChild);
    } else if (!btn.innerHTML.trim()) {
      btn.innerHTML = MAXIMIZE_ICON;
    }

    if (btn.dataset.diagramWired === "true") return;
    btn.dataset.diagramWired = "true";
    btn.addEventListener("click", function () {
      openDiagramLightbox(wrap);
    });
  }

  function initDiagramUI() {
    document.querySelectorAll(".diagram-wrap").forEach(wireMaximizeButton);
    requestAnimationFrame(function () {
      fitAllDiagrams();
      requestAnimationFrame(fitAllDiagrams);
    });
    if (!window.__stackconeDiagramResizeBound) {
      window.__stackconeDiagramResizeBound = true;
      window.addEventListener("resize", fitAllDiagrams);
    }
  }

  function renderOneDiagram(node, index) {
    var definition = (node.getAttribute("data-definition") || node.textContent || "").trim();
    if (!definition) return Promise.resolve();

    node.setAttribute("data-definition", definition);

    var api = getMermaid();
    var renderId = "stackcone-mmd-" + index + "-" + String(Date.now()).slice(-6);

    return api.render(renderId, definition).then(function (result) {
      var parsed = parseRenderResult(result);
      if (!parsed.svg) throw new Error("Mermaid returned empty SVG");

      node.innerHTML = parsed.svg;
      node.classList.add("is-rendered");
      node.removeAttribute("data-definition");

      var wrap = node.closest(".diagram-wrap");
      if (wrap) wrap.classList.add("is-diagram-rendered");

      if (parsed.bindFunctions) parsed.bindFunctions(node);
    });
  }

  function renderMermaidDiagrams() {
    var nodes = findDiagramNodes();
    if (!nodes.length) return Promise.resolve();

    var pending = nodes.filter(function (node) {
      return !node.classList.contains("is-rendered") && !node.querySelector("svg");
    });

    if (!pending.length) {
      initDiagramUI();
      return Promise.resolve();
    }

    var api = getMermaid();
    if (!api) {
      pending.forEach(function (node) {
        var wrap = node.closest(".diagram-wrap");
        if (wrap) showDiagramError(wrap, "Mermaid library failed to load.");
      });
      return Promise.reject(new Error("Mermaid not loaded"));
    }

    api.initialize(window.StackconeMermaidConfig);

    return Promise.all(
      pending.map(function (node, index) {
        return renderOneDiagram(node, index).catch(function (err) {
          console.error("Mermaid render failed:", err);
          var wrap = node.closest(".diagram-wrap");
          if (wrap) showDiagramError(wrap, err && err.message ? err.message : "Parse error");
          throw err;
        });
      })
    ).then(function () {
      initDiagramUI();
      document.dispatchEvent(new CustomEvent("stackcone:mermaid-rendered"));
    });
  }

  window.StackconeDiagrams = {
    render: renderMermaidDiagrams,
    initUI: initDiagramUI
  };

  document.addEventListener("stackcone:mermaid-rendered", initDiagramUI);

  var booted = false;
  var rendering = false;

  function boot() {
    if (booted || rendering) return;
    rendering = true;

    renderMermaidDiagrams()
      .then(function () {
        var rendered = document.querySelector(".diagram-wrap .mermaid-pending.is-rendered svg");
        booted = rendered || !findDiagramNodes().length;
      })
      .catch(function () {
        booted = false;
      })
      .finally(function () {
        rendering = false;
      });
  }

  function scheduleBoot() {
    document.querySelectorAll(".diagram-wrap").forEach(wireMaximizeButton);
    boot();
    window.addEventListener("load", boot, { once: true });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", scheduleBoot);
  } else {
    scheduleBoot();
  }
})();
