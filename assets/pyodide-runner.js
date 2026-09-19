(function () {
  var PYODIDE_VERSION = '0.26.4';
  var PYODIDE_BASE = 'https://cdn.jsdelivr.net/pyodide/v' + PYODIDE_VERSION + '/full/';

  function loadPyodideScript() {
    return new Promise(function (resolve, reject) {
      if (typeof window.loadPyodide === 'function') {
        resolve(window.loadPyodide);
        return;
      }
      var existing = document.querySelector('script[data-pyodide]');
      if (existing) {
        existing.addEventListener('load', function () {
          resolve(window.loadPyodide);
        });
        existing.addEventListener('error', reject);
        return;
      }
      var script = document.createElement('script');
      script.src = PYODIDE_BASE + 'pyodide.js';
      script.setAttribute('data-pyodide', 'true');
      script.onload = function () {
        resolve(window.loadPyodide);
      };
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  function getPyodide() {
    if (!window.__stackconePyodidePromise) {
      window.__stackconePyodidePromise = loadPyodideScript()
        .then(function (loadPyodide) {
          return loadPyodide({ indexURL: PYODIDE_BASE });
        });
    }
    return window.__stackconePyodidePromise;
  }

  function runPython(code, outputEl, runBtn) {
    if (!code || !code.trim()) {
      outputEl.textContent = '(no code to run)';
      outputEl.hidden = false;
      outputEl.classList.add('is-error');
      return Promise.resolve();
    }

    outputEl.hidden = false;
    outputEl.classList.remove('is-error');
    outputEl.textContent = 'Loading Python runtime…';
    if (runBtn) {
      runBtn.disabled = true;
      runBtn.classList.add('is-loading');
    }

    return getPyodide()
      .then(function (pyodide) {
        outputEl.textContent = 'Loading packages\u2026';
        // Pulls in pandas, numpy, matplotlib and friends when the code imports them.
        return pyodide.loadPackagesFromImports(code)
          .catch(function () { /* unknown import: let Python report it */ })
          .then(function () { return pyodide; });
      })
      .then(function (pyodide) {
        var stdout = '';
        var stderr = '';
        pyodide.setStdout({
          batched: function (s) {
            stdout += s + '\n';
          }
        });
        pyodide.setStderr({
          batched: function (s) {
            stderr += s + '\n';
          }
        });
        return pyodide.runPythonAsync(code).then(
          function () {
            var out = stdout + (stderr ? (stdout ? '\n' : '') + stderr : '');
            outputEl.textContent = out || '(no output)';
            outputEl.classList.remove('is-error');
          },
          function (err) {
            var msg = err && err.message ? err.message : String(err);
            outputEl.textContent = msg;
            outputEl.classList.add('is-error');
          }
        );
      })
      .catch(function (err) {
        outputEl.textContent = 'Failed to load Python: ' + (err.message || err);
        outputEl.classList.add('is-error');
      })
      .finally(function () {
        if (runBtn) {
          runBtn.disabled = false;
          runBtn.classList.remove('is-loading');
        }
      });
  }

  window.stackconeRunPython = runPython;
  window.stackconeLoadPyodide = getPyodide;
})();
