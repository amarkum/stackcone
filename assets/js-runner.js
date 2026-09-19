(function () {
  // Lesson JavaScript runs inside a sandboxed iframe, not on the page, so a bad
  // loop or a thrown error cannot take the lesson down with it.
  var TIMEOUT_MS = 5000;

  // Source for the helpers the frame needs. Kept as a string because the frame
  // is a separate realm and cannot see anything defined out here.
  var FRAME_HELPERS = [
    'function inspect(v, seen) {',
    '  return typeof v === "string" ? JSON.stringify(v) : format(v, seen);',
    '}',
    'function format(v, seen) {',
    '  seen = seen || [];',
    '  if (v === null) return "null";',
    '  if (v === undefined) return "undefined";',
    '  var t = typeof v;',
    '  if (t === "number" || t === "boolean" || t === "bigint") return String(v);',
    '  if (t === "string") return v;',
    '  if (t === "function") return v.name ? "[Function: " + v.name + "]" : "[Function]";',
    '  if (t === "symbol") return v.toString();',
    '  if (seen.indexOf(v) !== -1) return "[Circular]";',
    '  seen = seen.concat([v]);',
    '  if (Array.isArray(v)) return "[ " + v.map(function (x) { return inspect(x, seen); }).join(", ") + " ]";',
    '  if (v instanceof Error) return v.name + ": " + v.message;',
    '  if (v instanceof Date) return v.toISOString();',
    '  if (v instanceof Map) return "Map(" + v.size + ") { " + Array.from(v).map(function (p) { return inspect(p[0], seen) + " => " + inspect(p[1], seen); }).join(", ") + " }";',
    '  if (v instanceof Set) return "Set(" + v.size + ") { " + Array.from(v).map(function (x) { return inspect(x, seen); }).join(", ") + " }";',
    '  var keys = Object.keys(v);',
    '  if (!keys.length) return "{}";',
    '  return "{ " + keys.map(function (k) { return k + ": " + inspect(v[k], seen); }).join(", ") + " }";',
    '}'
  ].join('\n');

  function frameSource(code, token) {
    var body = [
      FRAME_HELPERS,
      'var lines = [];',
      'function emit() { lines.push([].slice.call(arguments).map(function (a) { return format(a); }).join(" ")); }',
      'console.log = console.info = console.warn = console.debug = console.error = emit;',
      'var payload;',
      'try {',
      '  (0, eval)(' + JSON.stringify(code) + ');',
      '  payload = { token: ' + JSON.stringify(token) + ', output: lines.join("\\n") };',
      '} catch (e) {',
      '  lines.push((e && e.name ? e.name + ": " : "") + (e && e.message ? e.message : String(e)));',
      '  payload = { token: ' + JSON.stringify(token) + ', output: lines.join("\\n"), error: true };',
      '}',
      'parent.postMessage(payload, "*");'
    ].join('\n');

    return '<!DOCTYPE html><html><body><scr' + 'ipt>\n' + body + '\n</scr' + 'ipt></body></html>';
  }

  function runJs(code, outputEl, runBtn) {
    if (!code || !code.trim()) {
      outputEl.hidden = false;
      outputEl.textContent = '(no code to run)';
      outputEl.classList.add('is-error');
      return Promise.resolve();
    }

    outputEl.hidden = false;
    outputEl.classList.remove('is-error');
    outputEl.textContent = 'Running…';
    if (runBtn) {
      runBtn.disabled = true;
      runBtn.classList.add('is-loading');
    }

    return new Promise(function (resolve) {
      var token = 'run-' + Math.random().toString(36).slice(2);
      var frame = document.createElement('iframe');
      frame.setAttribute('sandbox', 'allow-scripts');
      frame.setAttribute('aria-hidden', 'true');
      frame.style.cssText = 'position:absolute;width:0;height:0;border:0;visibility:hidden';

      var done = false;
      function finish(text, isError) {
        if (done) return;
        done = true;
        clearTimeout(timer);
        window.removeEventListener('message', onMessage);
        if (frame.parentNode) frame.parentNode.removeChild(frame);
        outputEl.textContent = text || '(no output)';
        outputEl.classList.toggle('is-error', !!isError);
        if (runBtn) {
          runBtn.disabled = false;
          runBtn.classList.remove('is-loading');
        }
        resolve();
      }

      function onMessage(event) {
        if (!event.data || event.data.token !== token) return;
        finish(event.data.output, event.data.error);
      }

      var timer = setTimeout(function () {
        finish('Timed out after ' + TIMEOUT_MS / 1000 + 's — check for an infinite loop.', true);
      }, TIMEOUT_MS);

      window.addEventListener('message', onMessage);
      frame.srcdoc = frameSource(code, token);
      document.body.appendChild(frame);
    });
  }

  window.stackconeRunJs = runJs;
})();
