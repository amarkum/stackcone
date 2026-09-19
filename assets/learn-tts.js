/* Read lessons, blog posts and solution write-ups aloud with the browser's built-in
   speech synthesis (free, no API). Adds a Listen control under the title area;
   code, output, charts and page chrome are skipped. */
(function () {
  if (!("speechSynthesis" in window) || !("SpeechSynthesisUtterance" in window)) return;

  var synth = window.speechSynthesis;
  var RATES = [1, 1.25, 1.5, 0.85];
  var BLOCKS = "h1, .learn-summary, h2, h3, h4, p, li, blockquote, figcaption, td, th";
  var SKIP =
    "pre, code, .learn-code-wrap, .learn-output, .learn-progress, .learn-top-nav, nav, " +
    ".learn-facts, .learn-prereq, .learn-upnext, .learn-solution, .learn-complete, " +
    "[data-auth-note], .diagram-wrap, .learn-eyebrow, .sc-tts, script, style, " +
    ".meta, .blog-cta, .chart-wrap, .blog-widget, .blog-toc, .toc, canvas, svg";

  var article, bar, playBtn, rateBtn, stopBtn, voiceSel;
  var queue = [];
  var index = 0;
  var rateIndex = 0;
  var state = "idle"; // idle | playing | paused
  var current = null;
  var gen = 0; // bumped on every cancel so callbacks from dropped utterances are ignored

  function readRate() {
    try {
      var i = RATES.indexOf(parseFloat(localStorage.getItem("sc-tts-rate")));
      if (i >= 0) rateIndex = i;
    } catch (e) {}
  }

  // Default voice: Microsoft's natural voices first (Edge / Windows), then other
  // well-known female voices, then whatever the device offers. Browsers do not expose
  // a voice's gender, so this goes by name.
  var PREFERRED = [
    /microsoft (aria|jenny|ava|emma|michelle|sonia|libby|natasha|neerja).*natural/i,
    /microsoft (aria|jenny|ava|emma|michelle|sonia|libby|natasha|neerja)/i,
    /microsoft .*natural/i,
    /microsoft (zira|hazel|susan|heera|catherine)/i,
    /google uk english female/i,
    /google us english/i,
    /^samantha\b/i,
    /^(karen|moira|tessa|serena|fiona|veena)\b/i
  ];

  function englishVoices() {
    var voices = synth.getVoices();
    var lang = (document.documentElement.lang || "en").toLowerCase().slice(0, 2);
    var same = voices.filter(function (v) { return v.lang.toLowerCase().indexOf(lang) === 0; });
    return same.length ? same : voices;
  }

  function savedVoiceName() {
    try { return localStorage.getItem("sc-tts-voice") || ""; } catch (e) { return ""; }
  }

  function pickVoice() {
    var pool = englishVoices();
    var saved = savedVoiceName();
    if (saved) {
      var chosen = pool.find(function (v) { return v.name === saved; });
      if (chosen) return chosen;
    }
    for (var i = 0; i < PREFERRED.length; i++) {
      var hit = pool.find(function (v) { return PREFERRED[i].test(v.name); });
      if (hit) return hit;
    }
    return pool.find(function (v) { return v.default; }) || pool[0] || null;
  }

  // Novelty voices shipped with macOS make a poor reading voice; keep them out of the menu.
  var NOVELTY = /^(albert|bad news|bahh|bells|boing|bubbles|cellos|good news|jester|organ|superstar|trinoids|whisper|wobble|zarvox|junior|ralph|fred|kathy|grandma|grandpa|rocko|eddy|reed)\b/i;

  // "Microsoft Aria Online (Natural) - English (United States)" -> "Aria (Natural)",
  // "Flo (English (United Kingdom))" -> "Flo".
  function voiceLabel(v) {
    var natural = /natural|neural/i.test(v.name);
    var name = v.name
      .replace(/^(Microsoft|Google|Apple)\s+/i, "")
      .replace(/\s*-\s*English.*$/i, "")
      .replace(/\s*\((English|Natural|Enhanced|Premium)[^)]*\)+/gi, "")
      .replace(/\s+Online\b/i, "")
      .trim();
    return natural ? name + " (Natural)" : name;
  }

  // One entry per label; US English wins over other accents with the same name.
  function langRank(v) {
    var l = v.lang.toLowerCase();
    return l === "en-us" ? 0 : l === "en-gb" ? 1 : 2;
  }

  function fillVoices() {
    if (!voiceSel) return;
    var byLabel = {};
    englishVoices().forEach(function (v) {
      if (NOVELTY.test(v.name) || !/^en/i.test(v.lang)) return;
      var key = voiceLabel(v);
      if (!byLabel[key] || langRank(v) < langRank(byLabel[key])) byLabel[key] = v;
    });
    var labels = Object.keys(byLabel).sort(function (x, y) {
      // Natural voices first, then alphabetical.
      var nx = /\(Natural\)$/.test(x) ? 0 : 1, ny = /\(Natural\)$/.test(y) ? 0 : 1;
      return nx - ny || x.localeCompare(y);
    });
    if (!labels.length) { voiceSel.hidden = true; return; }
    var current = pickVoice();
    var currentLabel = current ? voiceLabel(current) : "";
    voiceSel.innerHTML = "";
    labels.forEach(function (label) {
      var o = document.createElement("option");
      o.value = byLabel[label].name;
      o.textContent = label;
      if (label === currentLabel) o.selected = true;
      voiceSel.appendChild(o);
    });
    voiceSel.hidden = false;
  }


  function collect() {
    var out = [];
    article.querySelectorAll(BLOCKS).forEach(function (el) {
      if (el.closest(SKIP)) return;
      // Outermost block only, so a paragraph inside a list item is not read twice.
      var parent = el.parentElement && el.parentElement.closest(BLOCKS);
      if (parent && article.contains(parent) && !parent.closest(SKIP)) return;
      var text = (el.innerText || "").replace(/\s+/g, " ").trim();
      if (!text) return;
      // Long blocks are split into sentences: some browsers stop speaking after ~15s.
      var parts = text.match(/[^.!?]+[.!?]+["')\]]*\s*|[^.!?]+$/g) || [text];
      var chunk = "";
      parts.forEach(function (p) {
        if ((chunk + p).length > 220 && chunk) {
          out.push({ el: el, text: chunk.trim() });
          chunk = "";
        }
        chunk += p;
      });
      if (chunk.trim()) out.push({ el: el, text: chunk.trim() });
    });
    return out;
  }

  function mark(el) {
    if (current === el) return;
    if (current) current.classList.remove("sc-tts-reading");
    current = el;
    if (!el) return;
    el.classList.add("sc-tts-reading");
    var r = el.getBoundingClientRect();
    if (r.top < 80 || r.bottom > window.innerHeight - 40) {
      el.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }

  function speakNext() {
    if (state !== "playing") return;
    if (index >= queue.length) {
      stop();
      return;
    }
    var item = queue[index];
    var g = gen;
    var u = new SpeechSynthesisUtterance(item.text);
    var voice = pickVoice();
    if (voice) u.voice = voice;
    u.lang = (voice && voice.lang) || document.documentElement.lang || "en-US";
    u.rate = RATES[rateIndex];
    u.onstart = function () { if (g === gen) mark(item.el); };
    u.onend = function () {
      if (g !== gen || state !== "playing") return;
      index++;
      speakNext();
    };
    u.onerror = function (e) {
      if (g !== gen) return;
      if (e.error === "interrupted" || e.error === "canceled") return;
      index++;
      speakNext();
    };
    synth.speak(u);
  }

  function play() {
    if (state === "paused") {
      state = "playing";
      synth.resume();
      // Chrome sometimes drops a paused queue; restart the current chunk if nothing is speaking.
      setTimeout(function () {
        if (state === "playing" && !synth.speaking) speakNext();
      }, 250);
    } else {
      queue = collect();
      if (!queue.length) return;
      index = 0;
      state = "playing";
      gen++;
      synth.cancel();
      speakNext();
    }
    render();
  }

  function pause() {
    state = "paused";
    synth.pause();
    render();
  }

  function stop() {
    state = "idle";
    gen++;
    synth.cancel();
    index = 0;
    mark(null);
    render();
  }

  var ICON_PLAY = '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 5 6 9H2v6h4l5 4z"/><path d="M15.5 8.5a5 5 0 0 1 0 7M19 5a10 10 0 0 1 0 14"/></svg>';
  var ICON_PAUSE = '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" fill="currentColor"><rect x="6" y="5" width="4" height="14" rx="1"/><rect x="14" y="5" width="4" height="14" rx="1"/></svg>';
  var ICON_STOP = '<svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true" fill="currentColor"><rect x="6" y="6" width="12" height="12" rx="2"/></svg>';

  function render() {
    var label = state === "playing" ? "Pause" : state === "paused" ? "Resume" : "Listen";
    playBtn.innerHTML = (state === "playing" ? ICON_PAUSE : ICON_PLAY) + "<span>" + label + "</span>";
    playBtn.setAttribute("aria-label", label + " (read this page aloud)");
    playBtn.classList.toggle("is-active", state !== "idle");
    stopBtn.hidden = state === "idle";
    rateBtn.textContent = RATES[rateIndex] + "×";
  }

  function mount() {
    article = document.querySelector(".learn-lesson") || document.querySelector("article.blog-article");
    if (!article || article.querySelector(".sc-tts") || !article.querySelector("h1")) return;
    var facts = article.querySelector(".learn-facts");
    // Blog and solution posts: under the "date · author" line, else under the title.
    var anchor = facts ? null : article.querySelector(":scope > .meta") || article.querySelector("h1");
    readRate();

    bar = document.createElement(facts ? "li" : "div");
    bar.className = "sc-tts";
    bar.innerHTML =
      '<button type="button" class="sc-tts-play"></button>' +
      '<button type="button" class="sc-tts-rate" title="Reading speed" aria-label="Reading speed"></button>' +
      '<select class="sc-tts-voice" title="Voice" aria-label="Voice" hidden></select>' +
      '<button type="button" class="sc-tts-stop" title="Stop" aria-label="Stop reading" hidden>' + ICON_STOP + "</button>";
    playBtn = bar.querySelector(".sc-tts-play");
    rateBtn = bar.querySelector(".sc-tts-rate");
    stopBtn = bar.querySelector(".sc-tts-stop");
    voiceSel = bar.querySelector(".sc-tts-voice");
    voiceSel.addEventListener("change", function () {
      try { localStorage.setItem("sc-tts-voice", voiceSel.value); } catch (e) {}
      // Switch voice from the current chunk.
      if (state === "playing") {
        gen++;
        synth.cancel();
        setTimeout(speakNext, 50);
      }
    });

    playBtn.addEventListener("click", function () {
      if (state === "playing") pause();
      else play();
    });
    stopBtn.addEventListener("click", stop);
    rateBtn.addEventListener("click", function () {
      rateIndex = (rateIndex + 1) % RATES.length;
      try { localStorage.setItem("sc-tts-rate", String(RATES[rateIndex])); } catch (e) {}
      render();
      // Apply the new speed from the current chunk.
      if (state === "playing") {
        gen++;
        synth.cancel();
        setTimeout(speakNext, 50);
      }
    });

    if (facts) facts.appendChild(bar);
    else anchor.insertAdjacentElement("afterend", bar);
    render();

    // Voices load asynchronously in Chrome.
    fillVoices();
    if (synth.addEventListener) synth.addEventListener("voiceschanged", fillVoices);
    else synth.onvoiceschanged = fillVoices;
    window.addEventListener("pagehide", function () {
      gen++;
      synth.cancel();
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", mount);
  else mount();
})();
