(function () {
  var CHEERPJ_LOADER = 'https://cjrtnc.leaningtech.com/4.3/loader.js';
  var ECJ_PATH = '/app/assets/vendor/ecj.jar';
  var ECJ_MAIN = 'org.eclipse.jdt.internal.compiler.batch.Main';

  function loadCheerpjScript() {
    return new Promise(function (resolve, reject) {
      if (typeof window.cheerpjInit === 'function') {
        resolve();
        return;
      }
      var existing = document.querySelector('script[data-cheerpj]');
      if (existing) {
        existing.addEventListener('load', function () { resolve(); });
        existing.addEventListener('error', reject);
        return;
      }
      var script = document.createElement('script');
      script.src = CHEERPJ_LOADER;
      script.setAttribute('data-cheerpj', 'true');
      script.onload = function () { resolve(); };
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  function consoleEl() {
    return document.getElementById('stackcone-java-console');
  }

  function ensureDisplay() {
    if (document.getElementById('stackcone-java-root')) return;
    var root = document.createElement('div');
    root.id = 'stackcone-java-root';
    root.setAttribute('aria-hidden', 'true');
    root.style.cssText =
      'position:absolute;left:-9999px;width:320px;height:200px;overflow:hidden;';
    var pre = document.createElement('pre');
    pre.id = 'stackcone-java-console';
    pre.style.cssText = 'white-space:pre-wrap;margin:0;';
    var display = document.createElement('div');
    display.id = 'stackcone-java-display';
    root.appendChild(pre);
    root.appendChild(display);
    document.body.appendChild(root);
  }

  function getRuntime() {
    if (!window.__stackconeCheerpjPromise) {
      window.__stackconeCheerpjPromise = loadCheerpjScript().then(function () {
        ensureDisplay();
        return window.cheerpjInit({
          version: 17,
          status: 'none'
        }).then(function () {
          window.cheerpjCreateDisplay(64, 64, document.getElementById('stackcone-java-display'));
          return window.cheerpjRunLibrary('');
        }).then(function (lib) {
          window.__stackconeCjLib = lib;
        });
      });
    }
    return window.__stackconeCheerpjPromise;
  }

  function extractClassName(code) {
    var match = code.match(/\b(?:public\s+)?(?:class|interface|enum)\s+([A-Za-z_]\w*)/);
    return match ? match[1] : 'Main';
  }

  function extractPackage(code) {
    var match = code.match(/^\s*package\s+([\w.]+)\s*;/m);
    return match ? match[1] : '';
  }

  function qualifiedName(code, className) {
    var pkg = extractPackage(code);
    return pkg ? pkg + '.' + className : className;
  }

  function sourcePath(code, className) {
    var pkg = extractPackage(code);
    if (pkg) return '/files/' + pkg.replace(/\./g, '/') + '/' + className + '.java';
    return '/files/' + className + '.java';
  }

  function hasMain(code) {
    return /public\s+static\s+void\s+main\s*\(/.test(code);
  }

  function looksLikeType(code) {
    return /\b(?:public\s+)?(?:class|interface|enum)\s+[A-Za-z_]/.test(code);
  }

  function looksLikeMethod(code) {
    return (
      /^(?:public|private|protected|static|\s)*[\w.<>,\[\]]+\s+[A-Za-z_]\w*\s*\([^;]*\)\s*\{/m.test(
        code
      ) && !looksLikeType(code)
    );
  }

  function splitImports(code) {
    var imports = [];
    var body = code.replace(/^\s*import\s+.+;\s*/gm, function (line) {
      imports.push(line.trim());
      return '';
    });
    return { imports: imports, body: body.replace(/^\s+/, '') };
  }

  function wrapStatements(code) {
    var parts = splitImports(code);
    var body = parts.body.replace(/\n/g, '\n        ');
    return (
      (parts.imports.length ? parts.imports.join('\n') + '\n\n' : '') +
      'public class Main {\n' +
      '    public static void main(String[] args) {\n' +
      '        ' +
      body +
      '\n    }\n}'
    );
  }

  function wrapMethods(code) {
    var parts = splitImports(code);
    var body = parts.body.replace(/\n/g, '\n    ');
    return (
      (parts.imports.length ? parts.imports.join('\n') + '\n\n' : '') +
      'public class Main {\n' +
      '    ' +
      body +
      '\n    public static void main(String[] args) {}\n}'
    );
  }

  function prepareSource(code) {
    var trimmed = (code || '').replace(/^\uFEFF/, '').trim();
    if (!trimmed) return null;
    if (looksLikeType(trimmed)) {
      var name = extractClassName(trimmed);
      return { name: name, fqn: qualifiedName(trimmed, name), source: trimmed, run: hasMain(trimmed) };
    }
    if (looksLikeMethod(trimmed)) {
      var wrappedMethods = wrapMethods(trimmed);
      return { name: 'Main', fqn: 'Main', source: wrappedMethods, run: false };
    }
    var wrapped = wrapStatements(trimmed);
    return { name: 'Main', fqn: 'Main', source: wrapped, run: true };
  }

  function readConsole() {
    var el = consoleEl();
    var display = document.getElementById('stackcone-java-display');
    var chunks = [];
    if (el && el.textContent) chunks.push(el.textContent);
    if (display) {
      var text = (display.innerText || display.textContent || '').trim();
      if (text) chunks.push(text);
    }
    return chunks.join('\n').replace(/\s+$/, '');
  }

  function clearConsole() {
    var el = consoleEl();
    if (el) el.textContent = '';
    var display = document.getElementById('stackcone-java-display');
    if (display) {
      display.querySelectorAll('#console, pre, .cheerpjConsole').forEach(function (node) {
        node.textContent = '';
      });
    }
  }

  function writeSource(prepared) {
    var path = sourcePath(prepared.source, prepared.name);
    var lib = window.__stackconeCjLib;
    if (!lib) return Promise.reject(new Error('CheerpJ filesystem is not available.'));
    return lib.java.io.File.then(function (File) {
      return new File(path).then(function (file) {
        return Promise.resolve(file.getParentFile()).then(function (parent) {
          return Promise.resolve(parent ? parent.mkdirs() : null).then(function () {
            return lib.java.io.FileWriter.then(function (FileWriter) {
              return new FileWriter(file).then(function (writer) {
                return Promise.resolve(writer.write(prepared.source)).then(function () {
                  return Promise.resolve(writer.close());
                });
              });
            });
          });
        });
      });
    }).then(function () {
      return path;
    });
  }

  function compile(path) {
    return window.cheerpjRunMain(
      ECJ_MAIN,
      ECJ_PATH + ':/files/',
      '-d',
      '/files/',
      '-classpath',
      '/files/',
      '-sourcepath',
      '/files/',
      '-source',
      '17',
      '-target',
      '17',
      '-proc:none',
      '-nowarn',
      path
    );
  }

  function compileFailed(exit) {
    return typeof exit === 'number' && exit !== 0;
  }

  function harnessSource(fqn) {
    return [
      'public class __SCRun {',
      '    public static void main(String[] args) throws Exception {',
      '        java.io.PrintStream ps = new java.io.PrintStream(',
      '            new java.io.FileOutputStream("/files/stdout.txt"), true, "UTF-8");',
      '        System.setOut(ps);',
      '        System.setErr(ps);',
      '        ' + fqn + '.main(args);',
      '        ps.close();',
      '    }',
      '}'
    ].join('\n');
  }

  function readStdoutFile() {
    if (typeof window.cjFileBlob !== 'function') return Promise.resolve('');
    return window
      .cjFileBlob('/files/stdout.txt')
      .then(function (blob) {
        return blob.text();
      })
      .catch(function () {
        return '';
      });
  }

  function runJava(code, outputEl, runBtn) {
    if (!code || !code.trim()) {
      outputEl.hidden = false;
      outputEl.textContent = '(no code to run)';
      outputEl.classList.add('is-error');
      return Promise.resolve();
    }

    var prepared = prepareSource(code);
    if (!prepared) {
      outputEl.hidden = false;
      outputEl.textContent = '(no code to run)';
      outputEl.classList.add('is-error');
      return Promise.resolve();
    }

    outputEl.hidden = false;
    outputEl.classList.remove('is-error');
    outputEl.textContent = 'Loading Java runtime…';
    if (runBtn) {
      runBtn.disabled = true;
      runBtn.classList.add('is-loading');
    }

    return getRuntime()
      .then(function () {
        outputEl.textContent = 'Compiling…';
        clearConsole();
        return writeSource(prepared);
      })
      .then(function (path) {
        return compile(path).then(function (exit) {
          var log = readConsole();
          if (compileFailed(exit)) {
            outputEl.textContent = log || 'Compilation failed.';
            outputEl.classList.add('is-error');
            return;
          }
          if (!prepared.run) {
            outputEl.textContent = log || '(compiled)';
            outputEl.classList.remove('is-error');
            return;
          }
          outputEl.textContent = 'Running…';
          clearConsole();
          var harness = { name: '__SCRun', source: harnessSource(prepared.fqn) };
          return writeSource(harness).then(function (harnessPath) {
            return compile(harnessPath).then(function (harnessExit) {
              if (compileFailed(harnessExit)) {
                return window.cheerpjRunMain(prepared.fqn, '/files/').then(function (runExit) {
                  var out = readConsole();
                  outputEl.textContent = out || (compileFailed(runExit) ? 'Program exited with code ' + runExit : '(no output)');
                  outputEl.classList.toggle('is-error', compileFailed(runExit));
                });
              }
              return window.cheerpjRunMain('__SCRun', '/files/').then(function (runExit) {
                return readStdoutFile().then(function (fileOut) {
                  var out = (fileOut || '').replace(/\s+$/, '') || readConsole();
                  if (compileFailed(runExit) && !out) {
                    outputEl.textContent = 'Program exited with code ' + runExit;
                    outputEl.classList.add('is-error');
                    return;
                  }
                  outputEl.textContent = out || '(no output)';
                  outputEl.classList.toggle('is-error', compileFailed(runExit));
                });
              });
            });
          });
        });
      })
      .catch(function (err) {
        outputEl.textContent = 'Failed to run Java: ' + (err && err.message ? err.message : err);
        outputEl.classList.add('is-error');
      })
      .finally(function () {
        if (runBtn) {
          runBtn.disabled = false;
          runBtn.classList.remove('is-loading');
        }
      });
  }

  window.stackconeRunJava = runJava;
})();
