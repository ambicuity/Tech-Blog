// Plays figure timelines (docs/figures.md). Loaded only on pages whose figures
// have [data-step] / [data-until] elements.
//
// A figure shows its final state until it is half in view, then plays once:
// step 0 hides everything with a data-step, each step reveals the next
// elements, and it ends on the final state again. Readers who prefer reduced
// motion get no autoplay. Pause / Play / Replay are always available, so
// nothing moves for more than a moment without a way to stop it.
(() => {
  const STEP_MS = 1300; // time on each step
  const HOLD_STEPS = 2; // extra steps spent on the final state before finishing
  const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;

  function setup(figure) {
    const nodes = [...figure.querySelectorAll(".figure__svg [data-step], .figure__svg [data-until]")];
    if (!nodes.length) return;
    const stepOf = (node, key) => Number(node.dataset[key] || 0);
    const last = Math.max(...nodes.map((n) => Math.max(stepOf(n, "step"), stepOf(n, "until"))));

    let step = 0;
    let timer = null;
    let finished = true;

    const button = document.createElement("button");
    button.type = "button";
    button.className = "figure__button";
    const controls = document.createElement("div");
    controls.className = "figure__controls";
    controls.append(button);
    figure.querySelector(".figure__svg").after(controls);

    const label = (text) => {
      button.textContent = text;
      button.setAttribute("aria-label", `${text} the diagram animation`);
    };
    const render = () => {
      for (const node of nodes) {
        node.classList.toggle("is-on", stepOf(node, "step") <= step);
        node.classList.toggle("is-off", node.dataset.until !== undefined && stepOf(node, "until") <= step);
      }
    };
    const stop = () => {
      clearInterval(timer);
      timer = null;
    };
    const finish = () => {
      stop();
      finished = true;
      figure.classList.remove("is-running");
      label("Replay");
    };
    const tick = () => {
      step += 1;
      if (step > last + HOLD_STEPS) finish();
      else render();
    };
    const play = () => {
      if (finished) {
        step = 0;
        finished = false;
      }
      figure.classList.add("is-running");
      render();
      label("Pause");
      stop();
      timer = setInterval(tick, STEP_MS);
    };
    const pause = () => {
      stop();
      label("Play");
    };

    button.addEventListener("click", () => (timer ? pause() : play()));
    label(reduceMotion ? "Play" : "Replay");

    if (reduceMotion || !("IntersectionObserver" in window)) return;
    const observer = new IntersectionObserver((entries) => {
      if (!entries.some((e) => e.isIntersecting)) return;
      observer.disconnect();
      play();
    }, { threshold: 0.5 });
    observer.observe(figure);
  }

  document.querySelectorAll(".figure[data-timeline]").forEach(setup);
})();
