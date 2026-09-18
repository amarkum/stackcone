(function () {
  var PLAY_ICON =
    '<svg class="learn-code-run-icon" viewBox="0 0 384 512" width="11" height="11" aria-hidden="true" focusable="false">' +
    '<path fill="none" stroke="currentColor" stroke-width="32" stroke-linejoin="round" d="M73 39l281 217c8 6 8 18 0 24L73 497c-11 8-27 1-27-12V51c0-13 16-20 27-12z"/></svg>';

  var MONACO_VERSION = '0.52.2';
  var MONACO_BASE = 'https://cdn.jsdelivr.net/npm/monaco-editor@' + MONACO_VERSION + '/min/vs';

  var LANG_MAP = {
    python: 'python',
    py: 'python',
    javascript: 'javascript',
    js: 'javascript',
    typescript: 'typescript',
    ts: 'typescript',
    java: 'java',
    bash: 'shell',
    sh: 'shell',
    shell: 'shell',
    zsh: 'shell',
    sql: 'sql',
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
    text: 'plaintext'
  };

  function detectLang(code, hint) {
    if (hint) {
      var mapped = LANG_MAP[hint.toLowerCase().trim()];
      if (mapped) return mapped;
    }
    if (/^\s*#!\/usr\/bin\/env\s+(python|bash|sh)/m.test(code)) {
      return /python/.test(code) ? 'python' : 'shell';
    }
    if (/^\s*(def |import |from |class |print\(|async def )/m.test(code)) return 'python';
    if (/^\s*(public |private |protected |class |void |int |String |System\.out)/m.test(code)) return 'java';
    if (/^\s*(function |const |let |var |=>|import |export )/m.test(code)) return 'javascript';
    if (/^\s*(SELECT|INSERT|CREATE|WITH|UPDATE|DELETE)\s/im.test(code)) return 'sql';
    if (/^\s*\{[\s\S]*"[^"]+"\s*:/m.test(code)) return 'json';
    if (/^\s*---\s*$/m.test(code) || /:\s*\n/m.test(code)) return 'yaml';
    if (/^<\?xml|<html|<div|<!DOCTYPE/i.test(code)) return 'html';
    if (/^\s*#\s/.test(code) && /\b(apt|npm|pip|curl|cd |echo )/m.test(code)) return 'shell';
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
        hint: hint
      });
    });
    return blocks;
  }

  function fitEditor(editor) {
    var height = editor.getContentHeight();
    editor.getContainerDomNode().style.height = Math.max(height, 48) + 'px';
    editor.layout();
  }

  function isRunnablePython(block, lang) {
    return (
      block.wrap &&
      document.body.classList.contains('learn-page') &&
      lang === 'python'
    );
  }

  function resolveBlockTitle(block) {
    if (!block.wrap) return '';
    var titled = block.wrap.getAttribute('data-title');
    if (titled) return titled.trim();
    var prev = block.wrap.previousElementSibling;
    if (prev && /^H[1-6]$/.test(prev.tagName)) {
      var text = (prev.textContent || '').trim();
      if (text) {
        block.wrap.setAttribute('data-title', text);
        prev.remove();
        return text;
      }
    }
    return '';
  }

  function createCodeToolbar(block, host, editor) {
    if (block.wrap && block.wrap.querySelector('.learn-code-toolbar')) return;

    var title = resolveBlockTitle(block);
    var runnable = !!(editor && isRunnablePython(block, detectLang(block.code, block.hint)));
    if (!title && !runnable) return;

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

    if (runnable) {
      var runBtn = document.createElement('button');
      runBtn.type = 'button';
      runBtn.className = 'learn-code-run';
      runBtn.innerHTML = PLAY_ICON + '<span>Run</span>';
      toolbar.appendChild(runBtn);

      var output = document.createElement('div');
      output.className = 'learn-code-output';
      output.hidden = true;
      output.setAttribute('aria-live', 'polite');

      block.wrap.classList.add('monaco-runnable');
      block.wrap.insertBefore(toolbar, host);
      host.insertAdjacentElement('afterend', output);

      runBtn.addEventListener('click', function () {
        if (typeof window.stackconeRunPython !== 'function') {
          output.hidden = false;
          output.textContent = 'Python runner not loaded. Refresh the page.';
          output.classList.add('is-error');
          return;
        }
        window.stackconeRunPython(editor.getValue(), output, runBtn);
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

    if (block.wrap) {
      block.pre.insertAdjacentElement('beforebegin', host);
      block.wrap.classList.add('monaco-ready');
      block.wrap.classList.remove('monaco-booting');
    } else {
      var shell = document.createElement('div');
      shell.className = 'monaco-code-block';
      if (block.hint) {
        var badge = document.createElement('span');
        badge.className = 'monaco-code-lang';
        badge.textContent = block.hint;
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

  function createEditor(monaco, host, block) {
    var lang = detectLang(block.code, block.hint);
    var runnable = isRunnablePython(block, lang);
    var editor = monaco.editor.create(host, {
      value: block.code,
      language: lang,
      readOnly: !runnable,
      domReadOnly: !runnable,
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
      fontFamily: "'Source Code Pro', ui-monospace, monospace",
      theme: 'vs-dark',
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
    if (runnable) {
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
