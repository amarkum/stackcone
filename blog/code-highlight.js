/** Run highlight.js on fenced code blocks: <pre><code class="language-python"> */
(function () {
  function highlight() {
    if (typeof hljs === "undefined") return;
    document.querySelectorAll("pre code[class*='language-']").forEach(function (el) {
      hljs.highlightElement(el);
    });
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", highlight);
  } else {
    highlight();
  }
})();
