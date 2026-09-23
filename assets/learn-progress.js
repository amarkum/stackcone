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

  // Keep the first paint stable: "Xm left" until under an hour, then "Done".
  function fmtMinutes(total) {
    if (total <= 0) return "Done";
    if (total < 60) return "~ " + total + " min";
    var h = Math.round(total / 60);
    return "~ " + h + (h === 1 ? " hour" : " hours");
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
    each("[data-progress-short]", function (el) { el.textContent = done + " of " + total + " lessons"; });
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

    each("[data-mark-complete]", function (btn) {
      var isDone = SCProgress.isDone(btn.getAttribute("data-mark-complete"));
      btn.classList.toggle("is-done", isDone);
      btn.setAttribute("aria-pressed", isDone ? "true" : "false");
      var label = btn.querySelector("[data-mark-label]");
      if (label) label.textContent = isDone ? "Completed" : (btn.classList.contains("learn-top-btn") ? "Mark complete" : "Mark as complete");
    });
    each("[data-finish]", function (el) {
      var b = el.querySelector("[data-mark-complete]");
      el.classList.toggle("is-done", !!b && SCProgress.isDone(b.getAttribute("data-mark-complete")));
    });
    document.body.classList.toggle("learn-course-done", done === total);
  }

  function each(sel, fn) {
    Array.prototype.forEach.call(document.querySelectorAll(sel), fn);
  }

  /* A small toast so auto-marking is visible and reversible. */
  var toastTimer;
  function toast(msg, undo) {
    var el = document.getElementById("sc-learn-toast");
    if (!el) {
      el = document.createElement("div");
      el.id = "sc-learn-toast";
      el.className = "learn-toast";
      el.setAttribute("role", "status");
      el.setAttribute("aria-live", "polite");
      document.body.appendChild(el);
    }
    el.innerHTML = "";
    var text = document.createElement("span");
    text.textContent = msg;
    el.appendChild(text);
    if (undo) {
      var b = document.createElement("button");
      b.type = "button";
      b.textContent = "Undo";
      b.addEventListener("click", function () { undo(); el.classList.remove("is-open"); });
      el.appendChild(b);
    }
    el.classList.add("is-open");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { el.classList.remove("is-open"); }, 4000);
  }

  function currentSlug() {
    var b = document.querySelector("[data-mark-complete]");
    return b ? b.getAttribute("data-mark-complete") : null;
  }

  /* Catalog / category pages: progress per course and a "Continue" link. */
  function renderCards() {
    var cards = document.querySelectorAll("[data-track-card]");
    if (!cards.length) return;
    loadCourses(function (list) {
      var tracks = {};
      list.forEach(function (c) { (tracks[c.track] = tracks[c.track] || []).push(c); });
      Array.prototype.forEach.call(cards, function (card) {
        var lessons = tracks[card.getAttribute("data-track-card")];
        if (!lessons) return;
        var done = lessons.filter(function (c) { return SCProgress.isDone(c.id); }).length;
        var box = card.querySelector("[data-card-progress]");
        if (!box) {
          box = document.createElement("span");
          box.className = "learn-card-progress";
          box.setAttribute("data-card-progress", "");
          var open = card.querySelector(".learn-track-open");
          card.insertBefore(box, open);
        }
        if (!done) { box.hidden = true; return; }
        box.hidden = false;
        var pct = Math.round((done / lessons.length) * 100);
        box.innerHTML = '<span class="learn-bar" aria-hidden="true"><span style="width:' + pct + '%"></span></span>' +
          "<small>" + done + " of " + lessons.length + " done</small>";
        var next = lessons.filter(function (c) { return !SCProgress.isDone(c.id); })[0];
        var open = card.querySelector(".learn-track-open");
        if (next) {
          card.setAttribute("href", "/learn/" + next.href.replace(/^\.\//, ""));
          if (open) open.textContent = "Continue: " + next.title;
        } else if (open) {
          open.textContent = "Completed. Review course";
        }
      });
    });
  }

  var coursesCache;
  function loadCourses(cb) {
    if (coursesCache) return cb(coursesCache);
    if (!window.fetch) return;
    fetch("/learn/courses.json").then(function (r) { return r.json(); }).then(function (d) {
      coursesCache = d.courses || [];
      cb(coursesCache);
    }).catch(function () { /* cards still work as plain links */ });
  }

  function init() {
    each("[data-mark-complete]", function (btn) {
      btn.addEventListener("click", function () {
        var slug = btn.getAttribute("data-mark-complete");
        var nowDone = SCProgress.toggle(slug);
        toast(nowDone ? "Lesson marked complete" : "Marked as not complete", function () { SCProgress.set(slug, !nowDone); });
      });
    });
    // Moving on to the next lesson counts as finishing this one.
    each("[data-complete-on-click]", function (link) {
      link.addEventListener("click", function () {
        var slug = currentSlug();
        if (slug && !SCProgress.isDone(slug)) SCProgress.set(slug, true);
      });
    });
    SCProgress.onChange(render);
    SCProgress.onChange(renderCards);
    render();
    renderCards();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
