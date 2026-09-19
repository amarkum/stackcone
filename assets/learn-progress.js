/* stackcone Learn — lesson progress.
   Source of truth is localStorage so the site keeps working with no backend.
   When assets/learn-auth.js signs a user in it calls SCProgress.merge() with the
   cloud copy and listens for changes to push them back. */
(function () {
  "use strict";

  var KEY = "sc.learn.progress.v1";
  var listeners = [];
  var state = read();

  function read() {
    try {
      var raw = localStorage.getItem(KEY);
      var data = raw ? JSON.parse(raw) : null;
      if (!data || typeof data !== "object" || !data.completed) return { completed: {} };
      return { completed: data.completed };
    } catch (e) {
      return { completed: {} }; // private mode, blocked storage, corrupt JSON
    }
  }

  function write() {
    try {
      localStorage.setItem(KEY, JSON.stringify(state));
    } catch (e) {
      /* progress is a convenience; never break the lesson over it */
    }
  }

  function emit() {
    for (var i = 0; i < listeners.length; i++) {
      try { listeners[i](state); } catch (e) { /* one bad listener must not stop the rest */ }
    }
  }

  var SCProgress = {
    all: function () { return state.completed; },

    // Each entry is a timestamp: positive = completed at, negative = un-marked at.
    // Keeping un-marks lets another device's copy merge without resurrecting them.
    isDone: function (slug) { return state.completed[slug] > 0; },

    /** Returns the new state (true = complete). */
    set: function (slug, done) {
      var now = Date.now();
      state.completed[slug] = done ? now : -now;
      write();
      emit();
      return !!done;
    },

    toggle: function (slug) { return SCProgress.set(slug, !SCProgress.isDone(slug)); },

    /** Fold in another copy (cloud or another device). Per lesson, the newest action wins. */
    merge: function (completed) {
      if (!completed) return false;
      var changed = false;
      for (var slug in completed) {
        if (!Object.prototype.hasOwnProperty.call(completed, slug)) continue;
        var ts = Number(completed[slug]);
        if (!ts) continue;
        var mine = state.completed[slug] || 0;
        if (Math.abs(ts) > Math.abs(mine)) {
          state.completed[slug] = ts;
          changed = true;
        }
      }
      if (changed) { write(); emit(); }
      return changed;
    },

    reset: function () { state = { completed: {} }; write(); emit(); },

    onChange: function (fn) { listeners.push(fn); return fn; },
  };

  window.SCProgress = SCProgress;

  /* ---------------- rendering ---------------- */

  // Same format as fmt_minutes() in _dev/generate_learn.py, so the first paint doesn't jump.
  function fmtMinutes(total) {
    if (total <= 0) return "Done";
    var h = Math.floor(total / 60);
    var m = total % 60;
    if (h && m) return h + "h " + m + "m";
    if (h) return h + "h";
    return m + " min";
  }

  function render() {
    var sidebar = document.querySelector("[data-course]");
    if (!sidebar) return;

    var links = Array.prototype.slice.call(sidebar.querySelectorAll("[data-lesson]"));
    var total = links.length;
    if (!total) return;

    var done = 0;
    var minutesLeft = 0;
    links.forEach(function (link) {
      var isDone = SCProgress.isDone(link.getAttribute("data-lesson"));
      link.classList.toggle("is-done", isDone);
      var state = link.querySelector("[data-lesson-state]");
      if (state) state.setAttribute("aria-label", isDone ? "Completed" : "Not started");
      if (isDone) done++;
      else minutesLeft += parseInt(link.getAttribute("data-minutes"), 10) || 0;
    });

    var pct = Math.round((done / total) * 100);

    each("[data-progress-pct]", function (el) { el.textContent = pct + "%"; });
    each("[data-progress-count]", function (el) {
      el.textContent = done + " of " + total + " lessons completed";
    });
    each("[data-progress-fraction]", function (el) { el.textContent = done + " / " + total; });
    each("[data-progress-done]", function (el) { el.textContent = String(done); });
    each("[data-progress-left]", function (el) { el.textContent = fmtMinutes(minutesLeft); });
    each("[data-progress-fill]", function (el) { el.style.width = pct + "%"; });
    each("[data-progress-bar]", function (el) {
      el.setAttribute("aria-valuenow", String(pct));
      el.setAttribute("aria-valuetext", done + " of " + total + " lessons completed");
    });
    each("[data-progress-ring-arc]", function (el) {
      var r = parseFloat(el.getAttribute("r")) || 0;
      var c = 2 * Math.PI * r;
      el.style.strokeDasharray = c.toFixed(2);
      el.style.strokeDashoffset = (c * (1 - pct / 100)).toFixed(2);
    });

    var btn = document.querySelector("[data-mark-complete]");
    if (btn) {
      var slug = btn.getAttribute("data-mark-complete");
      var isDone = SCProgress.isDone(slug);
      btn.classList.toggle("is-done", isDone);
      btn.setAttribute("aria-pressed", isDone ? "true" : "false");
      var label = btn.querySelector("[data-mark-label]");
      if (label) label.textContent = isDone ? "Completed" : "Mark as complete";
    }
  }

  function each(sel, fn) {
    Array.prototype.forEach.call(document.querySelectorAll(sel), fn);
  }

  function init() {
    var btn = document.querySelector("[data-mark-complete]");
    if (btn) {
      btn.addEventListener("click", function () {
        SCProgress.toggle(btn.getAttribute("data-mark-complete"));
      });
    }
    SCProgress.onChange(render);
    render();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
