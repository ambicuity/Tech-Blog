// Renders math with KaTeX (loaded just before this file, only on pages with math).
(() => {
  const script = document.currentScript;
  const dollar = script && script.hasAttribute("data-dollar");
  if (typeof window.renderMathInElement !== "function") return;
  const delimiters = [
    { left: "\\[", right: "\\]", display: true },
    { left: "\\(", right: "\\)", display: false },
  ];
  if (dollar) {
    delimiters.push({ left: "$$", right: "$$", display: true }, { left: "$", right: "$", display: false });
  }
  window.renderMathInElement(document.querySelector("[data-prose]") || document.body, {
    delimiters,
    ignoredTags: ["script", "noscript", "style", "textarea", "pre", "code"],
    throwOnError: false,
    // kramdown's smart quotes turn f'(x) into f’(x); give KaTeX the prime back.
    preProcess: (math) => math.replace(/[’‘]/g, "'"),
  });
})();
