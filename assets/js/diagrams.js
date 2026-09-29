// Renders <pre class="mermaid"> diagrams (Mermaid is loaded only on pages that have one).
// Diagram colors and type are taken from the site's design tokens.
(() => {
  if (!window.mermaid) return;
  const css = getComputedStyle(document.documentElement);
  const token = (name) => css.getPropertyValue(name).trim();
  const dark = document.documentElement.getAttribute("data-effective-theme") === "dark";
  window.mermaid.initialize({
    startOnLoad: false,
    securityLevel: "strict",
    theme: dark ? "dark" : "neutral",
    themeVariables: {
      fontFamily: token("--font-sans"),
      edgeLabelBackground: token("--surface"),
      lineColor: token("--text-muted"),
    },
  });
  window.mermaid.run({ querySelector: "pre.mermaid" }).catch((error) => console.error("Diagram failed to render", error));
})();
