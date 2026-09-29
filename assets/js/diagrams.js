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
    // Tighter than Mermaid's defaults (50/50) so flowcharts stay within a screen.
    flowchart: { nodeSpacing: 28, rankSpacing: 34, padding: 10 },
    // Wrap long messages so sequence diagrams stay about as wide as the article.
    sequence: { wrap: true, width: 120, actorMargin: 30, messageMargin: 30 },
  });
  // Mermaid scales a diagram down to fit its box, which makes wide diagrams
  // unreadable on phones. Never shrink below MIN_SCALE: the box scrolls instead.
  const MIN_SCALE = 0.8;
  const fit = () => {
    document.querySelectorAll("pre.mermaid svg").forEach((svg) => {
      const natural = svg.viewBox.baseVal && svg.viewBox.baseVal.width;
      if (!natural) return;
      svg.style.maxWidth = `${natural}px`;
      svg.style.width = `max(100%, ${Math.round(natural * MIN_SCALE)}px)`;
      svg.style.flex = "none";
    });
  };
  window.mermaid
    .run({ querySelector: "pre.mermaid" })
    .then(fit)
    .catch((error) => console.error("Diagram failed to render", error));
})();
