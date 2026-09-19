/* Read lessons aloud with the browser's built-in speech synthesis (free, no API).
   Adds a Listen control to the lesson facts row; code, output and page chrome are skipped. */
(function () {
  if (!("speechSynthesis" in window) || !("SpeechSynthesisUtterance" in window)) return;

  var synth = window.speechSynthesis;
  var RATES = [1, 1.25, 1.5, 0.85];
  var BLOCKS = "h1, .learn-summary, h2, h3, h4, p, li, blockquote, figcaption, td, th";
  var SKIP =
    "pre, code, .learn-code-wrap, .learn-output, .learn-progress, .learn-top-nav, nav, " +
    ".learn-facts, .learn-prereq, .learn-upnext, .learn-solution, .learn-complete, " +
    "[data-auth-note], .diagram-wrap, .learn-eyebrow, .sc-tts, script, style";

  var article, bar, playBtn, rateBtn, stopBtn;
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

  function pickVoice() {
    var voices = synth.getVoices();
    var lang = (document.documentElement.lang || "en").toLowerCase();
    var same = voices.filter(function (v) { return v.lang.toLowerCase().indexOf(lang.slice(0, 2)) === 0; });
    var pool = same.length ? same : voices;
    // Prefer the natural-sounding voices browsers ship when they are available.
    var good = pool.filter(function (v) { return /natural|neural|google|samantha|daniel|aria|jenny/i.test(v.name); });
    return good[0] || pool.find(function (v) { return v.default; }) || pool[0] || null;
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
    playBtn.setAttribute("aria-label", label + " lesson audio");
    playBtn.classList.toggle("is-active", state !== "idle");
    stopBtn.hidden = state === "idle";
    rateBtn.textContent = RATES[rateIndex] + "×";
  }

  function mount() {
    article = document.querySelector(".blog-article.learn-lesson") || document.querySelector(".learn-lesson");
    if (!article || article.querySelector(".sc-tts")) return;
    var facts = article.querySelector(".learn-facts");
    readRate();

    bar = document.createElement(facts ? "li" : "div");
    bar.className = "sc-tts";
    bar.innerHTML =
      '<button type="button" class="sc-tts-play"></button>' +
      '<button type="button" class="sc-tts-rate" title="Reading speed" aria-label="Reading speed"></button>' +
      '<button type="button" class="sc-tts-stop" title="Stop" aria-label="Stop reading" hidden>' + ICON_STOP + "</button>";
    playBtn = bar.querySelector(".sc-tts-play");
    rateBtn = bar.querySelector(".sc-tts-rate");
    stopBtn = bar.querySelector(".sc-tts-stop");

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
    else article.insertBefore(bar, article.firstChild);
    render();

    // Voices load asynchronously in Chrome.
    if (synth.onvoiceschanged !== undefined) synth.onvoiceschanged = function () {};
    window.addEventListener("pagehide", function () {
      gen++;
      synth.cancel();
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", mount);
  else mount();
})();
