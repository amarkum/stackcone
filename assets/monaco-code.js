(function () {
  var PLAY_ICON =
    '<svg class="learn-code-run-icon" viewBox="0 0 384 512" width="11" height="11" aria-hidden="true" focusable="false">' +
    '<path fill="none" stroke="currentColor" stroke-width="32" stroke-linejoin="round" d="M73 39l281 217c8 6 8 18 0 24L73 497c-11 8-27 1-27-12V51c0-13 16-20 27-12z"/></svg>';

  var MONACO_VERSION = '0.52.2';
  var MONACO_BASE = 'https://cdn.jsdelivr.net/npm/monaco-editor@' + MONACO_VERSION + '/min/vs';

  var LANG_MAP = {
    python: 'python',
    py: 'python',
    pyfile: 'python',
    jsfile: 'javascript',
    javascript: 'javascript',
    js: 'javascript',
    typescript: 'typescript',
    ts: 'typescript',
    java: 'java',
    javafile: 'java',
    bash: 'shell',
    sh: 'shell',
    shell: 'shell',
    zsh: 'shell',
    sql: 'sql',
    sqlfile: 'sql',
    json: 'json',
    yaml: 'yaml',
    yml: 'yaml',
    html: 'html',
    xml: 'xml',
    css: 'css',
    go: 'go',
    golang: 'go',
    rust: 'rust',
    kotlin: 'kotlin',
    dart: 'dart',
    ruby: 'ruby',
    rb: 'ruby',
    dockerfile: 'dockerfile',
    markdown: 'markdown',
    md: 'markdown',
    plaintext: 'plaintext',
    text: 'plaintext',
    ini: 'ini',
    env: 'ini',
    toml: 'ini',
    plist: 'xml',
    podfile: 'ruby',
    gradle: 'kotlin',
    kts: 'kotlin',
    groovy: 'java',
    pubspec: 'yaml',
    firestore: 'javascript',
    rules: 'javascript',
    graphql: 'graphql',
    proto: 'protobuf',
    hcl: 'hcl',
    terraform: 'hcl',
    mermaid: 'plaintext'
  };

  function detectLang(code, hint) {
    if (hint) {
      var key = hint.toLowerCase().trim();
      if (key !== 'mermaid' && key !== 'auto') {
        var mapped = LANG_MAP[key];
        if (mapped) return mapped;
      }
    }
    var text = code || '';

    if (/[├└│]/.test(text)) return 'plaintext';
    if (/^\s*#!\/usr\/bin\/env\s+python/m.test(text)) return 'python';
    if (/^\s*#!\//.test(text)) return 'shell';

    if (/\b(public|private|protected)\s+(class|interface|void|static)/.test(text) || /\bSystem\.out\b/.test(text)) {
      return 'java';
    }

    // Dart before Python/JS — `import` and `class` match all three.
    if (
      /import\s+['"]package:/.test(text) ||
      /import\s+['"]dart:/.test(text) ||
      /\b(StatelessWidget|StatefulWidget|WidgetRef|BuildContext|kIsWeb|FlutterFire)\b/.test(text) ||
      /Future<\w+>/.test(text) ||
      /\bbool get\b/.test(text) ||
      (/\bstatic const\b/.test(text) && /;\s*$/m.test(text)) ||
      /^\s*final\s+\w+/.test(text) ||
      /^\s*const _\w+/.test(text) ||
      /\b(StreamProvider|GoRouter|WidgetRef)\b/.test(text) ||
      (/\bstatic String\b/.test(text) && /=>/.test(text))
    ) {
      return 'dart';
    }

    if (/rules_version\s*=/.test(text) || /service cloud\.firestore/.test(text)) return 'javascript';
    if (/<\/?(key|plist|string|dict|array)>/.test(text) || /^\s*<\?xml/i.test(text)) return 'xml';
    if (/<!DOCTYPE html|<html[\s>]|<div[\s>]/i.test(text)) return 'html';
    if (/\buse_frameworks!/.test(text) || /^\s*target\s+['"][^'"]+['"]\s+do\b/m.test(text)) return 'ruby';
    if (/^\s*plugins\s*\{/m.test(text) || /id\(["']com\.(android|google)/.test(text) || /\bfun\s+\w+\s*\(/.test(text)) {
      return 'kotlin';
    }
    if (
      /\{\{\s*config\(/.test(text) ||
      /^\s*SELECT\s+/im.test(text) ||
      /^\s*INSERT\s+INTO\b/im.test(text) ||
      /^\s*UPDATE\s+\S+\s+SET\b/im.test(text) ||
      /^\s*DELETE\s+FROM\b/im.test(text) ||
      /^\s*MERGE\s+INTO\b/im.test(text) ||
      /^\s*CREATE\s+(TABLE|INDEX|VIEW|OR|UNIQUE|SCHEMA|DATABASE|MATERIALIZED)\b/im.test(text) ||
      /^\s*WITH\s+\w+\s+AS\s*\(/im.test(text)
    ) {
      return 'sql';
    }
    if (/^\s*package\s+\w+/m.test(text) || /^\s*func\s+\(/.test(text) || /^\s*func\s+\w+\s*\(/.test(text)) {
      return 'go';
    }
    if (/^\s*[\{\[]/.test(text) && /"[^"]+"\s*:/.test(text)) return 'json';
    if (
      /^\s*---\s*$/m.test(text) ||
      /^\s*(dependencies|dev_dependencies|name|on|jobs|services):\s*$/m.test(text)
    ) {
      return 'yaml';
    }
    if (
      /^\s*(def |async def |from \w|class \w+\s*[:\(])/m.test(text) ||
      (/^\s*import\s+[A-Za-z_]\w*/m.test(text) && !/import\s+['"]/.test(text)) ||
      /^\s*yield\s+/m.test(text) ||
      /^\s*with\s+.+\s+as\s+/m.test(text) ||
      /^\s*for\s+\w+\s+in\s+/m.test(text)
    ) {
      return 'python';
    }
    if (/\b(public|private|protected)\s+(class|interface|void|static)/.test(text) || /\bSystem\.out\b/.test(text)) {
      return 'java';
    }
    if (/\b(interface|type)\s+\w+\s*[{=]/.test(text) || /:\s*(string|number|boolean|Promise)</.test(text)) {
      return 'typescript';
    }
    if (
      /^\s*(function |const |let |var |export |async function )/m.test(text) ||
      /=>\s*\{/.test(text) ||
      /import\s+['"]/.test(text)
    ) {
      return 'javascript';
    }
    if (/^\s*(FROM|RUN|CMD|COPY|WORKDIR)\s/m.test(text)) return 'dockerfile';
    if (
      /^\s*(flutter |dart |npm |npx |pip3? |python3 |curl |cd |export |echo |git |keytool |chmod |sudo |brew |mkdir |cat |docker )/m.test(text)
    ) {
      return 'shell';
    }
    if (/:\s*\n\s+\S/.test(text)) return 'yaml';
    return 'plaintext';
  }

  function extractCode(codeEl) {
    return (codeEl.textContent || '').replace(/\n$/, '');
  }

  function shouldSkipPre(pre) {
    if (!pre || !pre.querySelector('code')) return true;
    if (pre.classList.contains('mermaid')) return true;
    if (pre.closest('.mermaid, .diagram-wrap, .monaco-code-block')) return true;
    if (pre.classList.contains('monaco-replaced')) return true;
    if (pre.closest('.learn-code-wrap.monaco-ready, .learn-code-wrap.monaco-booting')) return true;
    if (pre.previousElementSibling && pre.previousElementSibling.classList.contains('monaco-code-host')) return true;
    var codeEl = pre.querySelector('code');
    if (codeEl && /language-mermaid|\bmermaid\b/.test(codeEl.className || '')) return true;
    return false;
  }

  function collectBlocks() {
    var blocks = [];
    document.querySelectorAll('pre').forEach(function (pre) {
      if (shouldSkipPre(pre)) return;
      var codeEl = pre.querySelector('code');
      if (!codeEl) return;

      var wrap = pre.closest('.learn-code-wrap');
      var hint = '';
      if (wrap) {
        hint = wrap.getAttribute('data-lang') || '';
      } else {
        var cls = codeEl.className || '';
        var match = cls.match(/language-([\w-]+)/);
        if (match) hint = match[1];
      }

      blocks.push({
        pre: pre,
        wrap: wrap,
        code: extractCode(codeEl),
        hint: hint,
        solution: wrap && wrap.hasAttribute('data-solution') ? wrap.getAttribute('data-solution') : null
      });
    });
    return blocks;
  }

  function fitEditor(editor) {
    var height = editor.getContentHeight();
    editor.getContainerDomNode().style.height = Math.max(height, 48) + 'px';
    editor.layout();
  }

  // Languages we can actually execute in the browser. 'pyfile' and 'jsfile'
  // mark snippets that describe a file on disk, so they get no Run button.
  var RUNNERS = {
    python: { hint: 'pyfile', run: function () { return window.stackconeRunPython; } },
    javascript: { hint: 'jsfile', run: function () { return window.stackconeRunJs; } },
    java: { hint: 'javafile', run: function () { return window.stackconeRunJava; } },
    sql: { hint: 'sqlfile', run: function () { return window.stackconeRunSql; } }
  };

  // Web frameworks and LLM libraries cannot run in the in-browser runtime.
  var PYODIDE_PAGE_BLOCK = /\/(flask|django|fastapi|langchain)(\/|-)/;
  var JS_PAGE_BLOCK = /\/(react|express|nextjs)(\/|-)/;
  var JAVA_PAGE_BLOCK = /\/(spring)(\/|-)/;
  // SQL runs against the lesson database seeded by sql-runner.js, so the Run button
  // is only offered on the SQL course, where the snippets match that schema.
  var SQL_PAGE_ALLOW = /\/sql\//;

  var PY_STDLIB = {
    __future__: 1, abc: 1, argparse: 1, array: 1, ast: 1, asyncio: 1, atexit: 1,
    base64: 1, bisect: 1, builtins: 1, calendar: 1, cmath: 1, collections: 1,
    colorsys: 1, contextlib: 1, copy: 1, csv: 1, dataclasses: 1, datetime: 1,
    decimal: 1, difflib: 1, enum: 1, errno: 1, fnmatch: 1, fractions: 1,
    functools: 1, gc: 1, glob: 1, gzip: 1, hashlib: 1, heapq: 1, hmac: 1, html: 1,
    http: 1, io: 1, ipaddress: 1, itertools: 1, json: 1, keyword: 1, linecache: 1,
    locale: 1, logging: 1, math: 1, mimetypes: 1, numbers: 1, operator: 1, os: 1,
    pathlib: 1, pickle: 1, platform: 1, pprint: 1, queue: 1, random: 1, re: 1,
    secrets: 1, shlex: 1, shutil: 1, signal: 1, socket: 1, sqlite3: 1, ssl: 1,
    stat: 1, statistics: 1, string: 1, struct: 1, subprocess: 1, sys: 1,
    tempfile: 1, textwrap: 1, threading: 1, time: 1, timeit: 1, tokenize: 1,
    traceback: 1, types: 1, typing: 1, unicodedata: 1, unittest: 1, urllib: 1,
    uuid: 1, warnings: 1, weakref: 1, xml: 1, zipfile: 1, zlib: 1
  };

  // Packages Pyodide can load natively (e.g. pandas via loadPackagesFromImports).
  var PYODIDE_MODULES = {
    pandas: 1,
    numpy: 1,
    matplotlib: 1,
    PIL: 1,
    scipy: 1,
    sklearn: 1,
    dateutil: 1,
    pytz: 1,
    openpyxl: 1
  };

  function extractImportedNames(code) {
    var names = [];
    var re = /^\s*(?:from\s+(\S+)\s+import|import\s+([^\n#]+))/gm;
    var m;
    while ((m = re.exec(code))) {
      if (m[1]) {
        names.push(m[1]);
        continue;
      }
      var parts = (m[2] || '').split(',');
      for (var i = 0; i < parts.length; i++) {
        var name = parts[i].trim().split(/\s+/)[0];
        if (name) names.push(name);
      }
    }
    return names;
  }

  function pythonCanRunInPyodide(code) {
    if (PYODIDE_PAGE_BLOCK.test(location.pathname || '')) return false;
    var names = extractImportedNames(code);
    for (var i = 0; i < names.length; i++) {
      var raw = names[i];
      if (!raw || raw.charAt(0) === '.') return false;
      var top = raw.split('.')[0];
      if (!(PY_STDLIB[top] || PYODIDE_MODULES[top])) return false;
    }
    return true;
  }

  function javaCanRunInBrowser(code) {
    if (JAVA_PAGE_BLOCK.test(location.pathname || '')) return false;
    if (/\bimport\s+org\.springframework/.test(code)) return false;
    if (/\bSpringApplication\b/.test(code)) return false;
    return true;
  }

  function jsCanRunInBrowser(code) {
    if (JS_PAGE_BLOCK.test(location.pathname || '')) return false;
    if (/from\s+['"](?!\.|https?:)/.test(code)) return false;
    if (/require\s*\(\s*['"](?!\.|https?:)/.test(code)) return false;
    if (/<[A-Za-z][\w]*[\s/>]/.test(code) && /(?:return\s*\(|=>\s*\()/.test(code)) return false;
    return true;
  }


  // Earlier runnable Python snippets on the page, in order. Lessons build on
  // each other, so the Python runner replays these before the snippet you run.
  function preludeFor(block) {
    var out = [];
    var wraps = document.querySelectorAll('.learn-code-wrap[data-lang="python"]');
    for (var i = 0; i < wraps.length; i++) {
      var w = wraps[i];
      if (w === block.wrap) break;
      if (w.hasAttribute('data-solution')) continue;
      var code = w.querySelector('pre code');
      if (code) out.push(extractCode(code));
    }
    return out;
  }

  function runnerFor(block, lang) {
    if (!block.wrap || !document.body.classList.contains('learn-page')) return null;
    var r = RUNNERS[lang];
    if (!r || block.hint === r.hint) return null;
    if (lang === 'python' && !pythonCanRunInPyodide(block.code)) return null;
    if (lang === 'javascript' && !jsCanRunInBrowser(block.code)) return null;
    if (lang === 'java' && !javaCanRunInBrowser(block.code)) return null;
    if (lang === 'sql' && !SQL_PAGE_ALLOW.test(location.pathname || '')) return null;
    return r;
  }

  var LANG_LABELS = {
    python: 'Python', javascript: 'JavaScript', typescript: 'TypeScript', java: 'Java',
    shell: 'Terminal', sql: 'SQL', json: 'JSON', yaml: 'YAML', html: 'HTML', css: 'CSS',
    xml: 'XML', dockerfile: 'Dockerfile', go: 'Go', rust: 'Rust', kotlin: 'Kotlin',
    dart: 'Dart', ruby: 'Ruby', plaintext: 'Text', ini: 'Config', graphql: 'GraphQL',
    protobuf: 'Protobuf', hcl: 'HCL'
  };

  function resolveBlockTitle(block) {
    // Headings stay in the document; only an explicit data-title labels the bar.
    return block.wrap ? (block.wrap.getAttribute('data-title') || '').trim() : '';
  }

  function createCodeToolbar(block, host, editor) {
    if (block.wrap && block.wrap.querySelector('.learn-code-toolbar')) return;

    var lang = detectLang(block.code, block.hint);
    var title = resolveBlockTitle(block) || LANG_LABELS[lang] || '';
    var runner = editor ? runnerFor(block, lang) : null;
    var runnable = !!runner;
    var practice = !!(editor && block.solution !== null);
    if (!title && !runnable && !practice) return;

    var toolbar = document.createElement('div');
    toolbar.className = 'learn-code-toolbar';

    if (title) {
      var titleEl = document.createElement('span');
      titleEl.className = 'learn-code-title';
      titleEl.textContent = title;
      toolbar.appendChild(titleEl);
    } else {
      var spacer = document.createElement('span');
      spacer.className = 'learn-code-title learn-code-title--empty';
      toolbar.appendChild(spacer);
    }

    var actions = document.createElement('div');
    actions.className = 'learn-code-actions';
    toolbar.appendChild(actions);

    if (practice) {
      var solBtn = document.createElement('button');
      solBtn.type = 'button';
      solBtn.className = 'learn-code-solution';
      solBtn.textContent = 'Show solution';
      actions.appendChild(solBtn);
      block.wrap.classList.add('monaco-practice');

      solBtn.addEventListener('click', function () {
        editor.setValue(block.solution);
        solBtn.textContent = 'Solution shown';
        solBtn.disabled = true;
      });
      editor.onDidChangeModelContent(function () {
        if (editor.getValue() !== block.solution) {
          solBtn.textContent = 'Show solution';
          solBtn.disabled = false;
        }
      });
    }

    if (runnable) {
      var runBtn = document.createElement('button');
      runBtn.type = 'button';
      runBtn.className = 'learn-code-run';
      runBtn.innerHTML = PLAY_ICON + '<span>Run</span>';
      actions.appendChild(runBtn);

      var output = document.createElement('div');
      output.className = 'learn-code-output';
      output.hidden = true;
      output.setAttribute('aria-live', 'polite');

      block.wrap.classList.add('monaco-runnable');
      block.wrap.insertBefore(toolbar, host);
      host.insertAdjacentElement('afterend', output);

      runBtn.addEventListener('click', function () {
        var fn = runner.run();
        if (typeof fn !== 'function') {
          output.hidden = false;
          output.textContent = 'Runner not loaded. Refresh the page.';
          output.classList.add('is-error');
          return;
        }
        fn(editor.getValue(), output, runBtn, lang === 'python' ? preludeFor(block) : undefined);
      });
      return;
    }

    block.wrap.insertBefore(toolbar, host);
  }

  function createRunnableChrome(block, host, editor) {
    createCodeToolbar(block, host, editor);
  }

  function createHost(block) {
    if (block.wrap) {
      if (block.wrap.querySelector('.monaco-code-host')) return null;
      block.wrap.classList.add('monaco-booting');
    }

    var host = document.createElement('div');
    host.className = 'monaco-code-host';
    host.setAttribute('data-language', block.hint || 'auto');

    var mount = document.createElement('div');
    mount.className = 'monaco-code-mount';
    host.appendChild(mount);

    if (block.wrap) {
      block.pre.insertAdjacentElement('beforebegin', host);
      block.wrap.classList.add('monaco-ready');
      block.wrap.classList.remove('monaco-booting');
    } else {
      var shell = document.createElement('div');
      shell.className = 'monaco-code-block';
      var lang = detectLang(block.code, block.hint);
      var label = LANG_LABELS[lang];
      if (label && lang !== 'plaintext') {
        var badge = document.createElement('span');
        badge.className = 'monaco-code-lang';
        badge.textContent = label;
        shell.appendChild(badge);
      }
      shell.appendChild(host);
      block.pre.insertAdjacentElement('beforebegin', shell);
    }

    block.pre.classList.add('monaco-replaced');
    return host;
  }

  function loadMonaco() {
    return new Promise(function (resolve, reject) {
      if (window.monaco) {
        resolve(window.monaco);
        return;
      }

      window.MonacoEnvironment = {
        getWorkerUrl: function () {
          var code =
            "self.MonacoEnvironment={baseUrl:'" + MONACO_BASE + "'};" +
            "importScripts('" + MONACO_BASE + "/base/worker/workerMain.js');";
          return 'data:text/javascript;charset=utf-8,' + encodeURIComponent(code);
        }
      };

      if (!document.querySelector('link[data-monaco-editor]')) {
        var css = document.createElement('link');
        css.rel = 'stylesheet';
        css.setAttribute('data-monaco-editor', 'true');
        css.href = MONACO_BASE + '/editor/editor.main.css';
        document.head.appendChild(css);
      }

      var script = document.createElement('script');
      script.src = MONACO_BASE + '/loader.js';
      script.onload = function () {
        window.require.config({ paths: { vs: MONACO_BASE } });
        window.require(['vs/editor/editor.main'], function () {
          resolve(window.monaco);
        }, reject);
      };
      script.onerror = reject;
      document.body.appendChild(script);
    });
  }

  // Editor colours follow the site theme (html[data-theme], set by /assets/theme.js).
  // Backgrounds match --code-bg in styles.css so the editor blends into its card.
  function siteMonacoTheme() {
    return document.documentElement.getAttribute('data-theme') === 'dark' ? 'sc-dark' : 'sc-light';
  }

  var themesReady = false;
  function setupThemes(monaco) {
    if (themesReady) return;
    themesReady = true;
    monaco.editor.defineTheme('sc-light', {
      base: 'vs',
      inherit: true,
      rules: [],
      colors: {
        'editor.background': '#f8fafc',
        'editorLineNumber.foreground': '#94a3b8',
        'editorLineNumber.activeForeground': '#475569',
        'editor.selectionBackground': '#cbd5e1'
      }
    });
    monaco.editor.defineTheme('sc-dark', {
      base: 'vs-dark',
      inherit: true,
      rules: [],
      colors: {
        'editor.background': '#111113',
        'editorLineNumber.foreground': '#52525b',
        'editorLineNumber.activeForeground': '#a1a1aa',
        'editor.selectionBackground': '#3f3f46'
      }
    });
    new MutationObserver(function () {
      monaco.editor.setTheme(siteMonacoTheme());
    }).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
  }

  function createEditor(monaco, host, block) {
    setupThemes(monaco);
    var mount = host.querySelector('.monaco-code-mount') || host;
    var lang = detectLang(block.code, block.hint);
    var runner = runnerFor(block, lang);
    var runnable = !!runner;
    if (block.solution !== null && !runnable) {
      block.code = block.solution;
      block.solution = null;
    }
    var practice = block.solution !== null && runnable;
    var editable = runnable || practice;
    var editor = monaco.editor.create(mount, {
      value: block.code,
      language: lang,
      readOnly: !editable,
      domReadOnly: !editable,
      minimap: { enabled: false },
      scrollBeyondLastLine: false,
      lineNumbers: 'on',
      renderLineHighlight: 'none',
      overviewRulerLanes: 0,
      hideCursorInOverviewRuler: true,
      overviewRulerBorder: false,
      scrollbar: {
        vertical: 'hidden',
        horizontal: 'auto',
        alwaysConsumeMouseWheel: false
      },
      folding: true,
      glyphMargin: false,
      lineDecorationsWidth: 8,
      lineNumbersMinChars: 3,
      fontSize: 13,
      lineHeight: 20,
      fontFamily: "'Stackcone Mono', ui-monospace, monospace",
      theme: siteMonacoTheme(),
      wordWrap: 'off',
      automaticLayout: true,
      padding: { top: 12, bottom: 12 },
      contextmenu: false,
      quickSuggestions: false,
      suggestOnTriggerCharacters: false,
      acceptSuggestionOnEnter: 'off',
      tabCompletion: 'off',
      wordBasedSuggestions: 'off',
      links: false,
      hover: { enabled: false },
      occurrencesHighlight: 'off',
      selectionHighlight: false,
      renderValidationDecorations: 'off'
    });

    host.setAttribute('data-language', lang);
    if (editable) {
      host.classList.add('monaco-code-host--editable');
      createRunnableChrome(block, host, editor);
      editor.onDidChangeModelContent(function () {
        fitEditor(editor);
      });
    } else if (block.wrap) {
      createCodeToolbar(block, host, null);
    }
    fitEditor(editor);
    editor.onDidContentSizeChange(function () {
      fitEditor(editor);
    });
    return editor;
  }

  function initMonacoCodeBlocks() {
    if (window.__stackconeMonacoBooted) return;
    var blocks = collectBlocks();
    if (!blocks.length) return;
    window.__stackconeMonacoBooted = true;

    loadMonaco()
      .then(function (monaco) {
        blocks.forEach(function (block) {
          var host = createHost(block);
          if (!host) return;
          createEditor(monaco, host, block);
        });
      })
      .catch(function () {
        window.__stackconeMonacoBooted = false;
        blocks.forEach(function (block) {
          block.pre.classList.remove('monaco-replaced');
          if (block.wrap) {
            block.wrap.classList.remove('monaco-ready', 'monaco-booting');
          }
        });
      });
  }

  window.initMonacoCodeBlocks = initMonacoCodeBlocks;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMonacoCodeBlocks, { once: true });
  } else {
    initMonacoCodeBlocks();
  }
})();
