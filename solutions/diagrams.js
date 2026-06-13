(function () {
  var LIGHTBOX_ID = "diagram-lightbox";
  var MERMAID_SELECTOR = ".diagram-wrap pre.mermaid";
  var ZOOM_STEP = 1.2;
  var MIN_SCALE = 0.15;
  var MAX_SCALE = 5;
  var ICONS = {
    zoomIn:
      "<svg width=\"16\" height=\"16\" viewBox=\"0 0 16 16\" fill=\"none\" aria-hidden=\"true\">" +
        "<circle cx=\"7\" cy=\"7\" r=\"4.5\" stroke=\"currentColor\" stroke-width=\"1.5\"/>" +
        "<path d=\"M10 10l3.5 3.5\" stroke=\"currentColor\" stroke-width=\"1.5\" stroke-linecap=\"round\"/>" +
        "<path d=\"M7 5v4M5 7h4\" stroke=\"currentColor\" stroke-width=\"1.5\" stroke-linecap=\"round\"/>" +
      "</svg>",
    zoomOut:
      "<svg width=\"16\" height=\"16\" viewBox=\"0 0 16 16\" fill=\"none\" aria-hidden=\"true\">" +
        "<circle cx=\"7\" cy=\"7\" r=\"4.5\" stroke=\"currentColor\" stroke-width=\"1.5\"/>" +
        "<path d=\"M10 10l3.5 3.5\" stroke=\"currentColor\" stroke-width=\"1.5\" stroke-linecap=\"round\"/>" +
        "<path d=\"M5 7h4\" stroke=\"currentColor\" stroke-width=\"1.5\" stroke-linecap=\"round\"/>" +
      "</svg>",
    fit:
      "<svg width=\"16\" height=\"16\" viewBox=\"0 0 16 16\" fill=\"none\" aria-hidden=\"true\">" +
        "<path d=\"M2 5V2h3M14 5V2h-3M2 11v3h3M14 11v3h-3\" stroke=\"currentColor\" stroke-width=\"1.5\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/>" +
        "<path d=\"M5 2h6v6H5zM5 8h6v6H5z\" stroke=\"currentColor\" stroke-width=\"1.25\"/>" +
      "</svg>",
    pan:
      "<svg width=\"16\" height=\"16\" viewBox=\"0 0 16 16\" fill=\"none\" aria-hidden=\"true\">" +
        "<path d=\"M4 8.5V5.5a1.5 1.5 0 1 1 3 0V10M8 7V4.5a1.5 1.5 0 1 1 3 0V10M4 10v1.5a1.5 1.5 0 0 0 3 0V10\" stroke=\"currentColor\" stroke-width=\"1.25\" stroke-linecap=\"round\"/>" +
      "</svg>",
    close:
      "<svg width=\"16\" height=\"16\" viewBox=\"0 0 16 16\" fill=\"none\" aria-hidden=\"true\">" +
        "<path d=\"M4 4l8 8M12 4l-8 8\" stroke=\"currentColor\" stroke-width=\"1.5\" stroke-linecap=\"round\"/>" +
      "</svg>"
  };

  var lightboxState = null;
  var mermaidReady = false;

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
    var mermaidEl = body.querySelector("pre.mermaid");
    if (!mermaidEl) return;

    var svg = mermaidEl.querySelector("svg");
    if (!svg) return;

    svg.style.width = "";
    svg.style.height = "";
    svg.style.maxWidth = "";
    mermaidEl.style.width = "";
    mermaidEl.style.height = "";
    mermaidEl.style.margin = "0 auto";

    var maxW = body.clientWidth;
    var naturalW = svg.getBoundingClientRect().width;
    var naturalH = svg.getBoundingClientRect().height;

    if (!naturalW || !naturalH) {
      var dims = getSvgDimensions(svg);
      naturalW = dims.w;
      naturalH = dims.h;
    }

    if (naturalW > maxW && naturalW > 0) {
      var scale = maxW / naturalW;
      svg.style.width = Math.floor(naturalW * scale) + "px";
      svg.style.height = Math.floor(naturalH * scale) + "px";
    } else {
      svg.style.width = "auto";
      svg.style.height = "auto";
      svg.style.maxWidth = "100%";
    }
  }

  function fitAllDiagrams() {
    document.querySelectorAll(".diagram-wrap .diagram-body").forEach(fitDiagramBody);
  }

  function addMaximizeButton(wrap) {
    if (wrap.querySelector(".diagram-maximize")) return;

    var title =
      wrap.getAttribute("data-diagram-title") ||
      (wrap.querySelector(".diagram-caption") && wrap.querySelector(".diagram-caption").textContent.trim()) ||
      "Diagram";

    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "diagram-maximize";
    btn.setAttribute("aria-label", "View diagram fullscreen");
    btn.title = "Fullscreen";
    btn.innerHTML =
      "<svg width=\"16\" height=\"16\" viewBox=\"0 0 16 16\" fill=\"none\" aria-hidden=\"true\">" +
        "<path d=\"M9 2h5v5M7 14H2V9M14 2l-6 6M2 14l6-6\" stroke=\"currentColor\" stroke-width=\"1.5\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/>" +
      "</svg>";

    btn.addEventListener("click", function () {
      var mermaidEl = wrap.querySelector("pre.mermaid");
      if (mermaidEl && mermaidEl.querySelector("svg")) {
        openLightbox(title, mermaidEl);
      }
    });

    wrap.insertBefore(btn, wrap.firstChild);
  }

  function initMermaid() {
    if (!window.mermaid) return false;

    mermaid.initialize({
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
        padding: 16,
        htmlLabels: false,
        nodeSpacing: 32,
        rankSpacing: 40
      },
      sequence: {
        useMaxWidth: false,
        actorMargin: 40,
        messageMargin: 32,
        boxMargin: 10,
        wrap: true
      }
    });

    return true;
  }

  function renderDiagrams() {
    var nodes = Array.from(document.querySelectorAll(MERMAID_SELECTOR)).filter(function (node) {
      return !node.querySelector("svg") && !node.hasAttribute("data-processed");
    });

    if (!nodes.length) {
      fitAllDiagrams();
      return;
    }

    if (!initMermaid()) {
      nodes.forEach(function (node) {
        var wrap = node.closest(".diagram-wrap");
        if (wrap) showDiagramError(wrap, "Mermaid library failed to load.");
      });
      return;
    }

    document.querySelectorAll(".diagram-wrap").forEach(addMaximizeButton);

    mermaid
      .run({ nodes: nodes })
      .then(function () {
        nodes.forEach(function (node) {
          node.classList.add("is-rendered");
        });
        requestAnimationFrame(function () {
          fitAllDiagrams();
          requestAnimationFrame(fitAllDiagrams);
        });
        window.addEventListener("resize", fitAllDiagrams);
        mermaidReady = true;
      })
      .catch(function (err) {
        console.error("Mermaid render failed:", err);
        nodes.forEach(function (node) {
          var wrap = node.closest(".diagram-wrap");
          if (wrap) showDiagramError(wrap, String(err && err.message ? err.message : "Parse error"));
        });
      });
  }

  function boot() {
    renderDiagrams();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
