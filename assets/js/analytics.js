// Google Analytics 4 bootstrap. Kept external so the CSP needs no inline
// script, and deferred until the page has loaded and the browser is idle so
// the tag never competes with content. Page views are still recorded: gtag
// queues the initial "config" call and sends it once the library arrives.
(() => {
  const id = document.currentScript && document.currentScript.dataset.gaId;
  if (!id) return;

  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  gtag("js", new Date());
  gtag("config", id);

  const inject = () => {
    const script = document.createElement("script");
    script.async = true;
    script.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(id)}`;
    document.head.append(script);
  };
  const whenIdle = () => ("requestIdleCallback" in window ? requestIdleCallback(inject, { timeout: 3000 }) : setTimeout(inject, 1));
  if (document.readyState === "complete") whenIdle();
  else window.addEventListener("load", whenIdle, { once: true });
})();
