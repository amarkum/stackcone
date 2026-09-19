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

  function isPandasPage() {
    var path = location.pathname || '';
    return path.indexOf('/pandas/') !== -1 || /\/pandas-/.test(path);
  }

  function pagePackages() {
    if (!isPandasPage()) return [];
    var pkgs = ['pandas', 'numpy'];
    if ((location.pathname || '').indexOf('time-plots') !== -1) pkgs.push('matplotlib');
    return pkgs;
  }

  function ensurePagePrelude(pyodide) {
    if (!isPandasPage()) return Promise.resolve(pyodide);
    if (!window.__stackconePandasPrelude) {
      window.__stackconePandasPrelude = pyodide.runPythonAsync(
        'import pandas as pd\nimport numpy as np'
      );
    }
    return window.__stackconePandasPrelude.then(function () {
      return pyodide;
    });
  }

  // `prelude` is the earlier runnable snippets of the lesson. Lessons build on
  // each other (a DataFrame defined in one block is used in the next), so each
  // Run replays them silently in a fresh namespace first. Errors there are ignored.
  function runPython(code, outputEl, runBtn, prelude) {
    prelude = prelude || [];
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
        var extra = pagePackages();
        var ready = extra.length ? pyodide.loadPackage(extra) : Promise.resolve();
        return ready.then(function () {
          outputEl.textContent = 'Loading packages\u2026';
          // Native Pyodide loader for pandas, numpy, matplotlib, and other supported wheels.
          return pyodide.loadPackagesFromImports(prelude.concat([code]).join('\n'))
            .catch(function () { /* unknown import: let Python report it */ })
            .then(function () { return ensurePagePrelude(pyodide); });
        });
      })
      .then(function (pyodide) {
        var stdout = '';
        var stderr = '';
        var capture = false;
        pyodide.setStdout({ batched: function (t) { if (capture) stdout += t + '\n'; } });
        pyodide.setStderr({ batched: function (t) { if (capture) stderr += t + '\n'; } });

        var ns = pyodide.globals.get('dict')();
        var seed = isPandasPage() ? 'import pandas as pd\nimport numpy as np' : '';
        var chain = Promise.resolve();
        if (seed) chain = chain.then(function () { return pyodide.runPythonAsync(seed, { globals: ns }); });
        prelude.forEach(function (snippet) {
          chain = chain.then(function () {
            return pyodide.runPythonAsync(snippet, { globals: ns }).catch(function () {});
          });
        });
        return chain
          .then(function () {
            capture = true;
            return pyodide.runPythonAsync(code, { globals: ns });
          })
          .then(
            function () {
              var out = stdout + (stderr ? (stdout ? '\n' : '') + stderr : '');
              outputEl.textContent = out || '(no output)';
              outputEl.classList.remove('is-error');
            },
            function (err) {
              var msg = err && err.message ? err.message : String(err);
              outputEl.textContent = (stdout ? stdout + '\n' : '') + msg;
              outputEl.classList.add('is-error');
            }
          )
          .finally(function () { capture = false; ns.destroy(); });
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
