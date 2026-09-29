/*
 * Site behaviour. Progressive enhancement only: every feature here un-hides
 * its own controls, so nothing interactive is rendered when JS is unavailable.
 * The search UI lives in search.js and is imported on first use.
 */
(() => {
  "use strict";

  const root = document.documentElement;
  const SCRIPT_URL = document.currentScript ? document.currentScript.src : location.href;
  const $ = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));
  const reveal = (els) => els.forEach((el) => el.removeAttribute("hidden"));
  const isMac = /Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent);

  // One polite live region for transient announcements ("Copied", …).
  const announcer = document.createElement("p");
  announcer.className = "visually-hidden";
  announcer.setAttribute("role", "status");
  announcer.setAttribute("aria-live", "polite");
  document.body.append(announcer);
  const announce = (msg) => {
    announcer.textContent = "";
    requestAnimationFrame(() => { announcer.textContent = msg; });
  };

  const storage = {
    get(key) { try { return localStorage.getItem(key); } catch { return null; } },
    set(key, value) { try { localStorage.setItem(key, value); } catch { /* private mode */ } },
  };

  // ---- Theme ---------------------------------------------------------------
  const systemDark = window.matchMedia("(prefers-color-scheme: dark)");
  const effectiveTheme = () => root.getAttribute("data-theme") || (systemDark.matches ? "dark" : "light");

  function applyTheme() {
    const theme = effectiveTheme();
    root.setAttribute("data-effective-theme", theme);
    $$("[data-theme-toggle]").forEach((btn) => {
      btn.setAttribute("aria-label", theme === "dark" ? "Switch to light theme" : "Switch to dark theme");
    });
    const giscus = $("iframe.giscus-frame");
    if (giscus) {
      giscus.contentWindow.postMessage({ giscus: { setConfig: { theme: giscusTheme() } } }, "https://giscus.app");
    }
  }

  function initTheme() {
    const toggles = $$("[data-theme-toggle]");
    reveal(toggles);
    toggles.forEach((btn) => btn.addEventListener("click", () => {
      const next = effectiveTheme() === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      storage.set("theme", next);
      applyTheme();
    }));
    systemDark.addEventListener("change", applyTheme);
    applyTheme();
  }

  // ---- Dialogs (menu + search) --------------------------------------------------
  function wireDialog(dialog) {
    dialog.addEventListener("click", (event) => {
      if (event.target === dialog) dialog.close(); // backdrop click
      if (event.target.closest("[data-dialog-close]")) dialog.close();
    });
  }

  function initMenu() {
    const dialog = $("#mobile-menu");
    const toggle = $("[data-menu-open]");
    if (!dialog || !toggle || typeof dialog.showModal !== "function") return;
    wireDialog(dialog);
    toggle.addEventListener("click", () => {
      dialog.showModal();
      toggle.setAttribute("aria-expanded", "true");
    });
    dialog.addEventListener("close", () => toggle.setAttribute("aria-expanded", "false"));
    dialog.addEventListener("click", (event) => { if (event.target.closest("a")) dialog.close(); });
    window.matchMedia("(min-width: 1100px)").addEventListener("change", (e) => { if (e.matches && dialog.open) dialog.close(); });
  }

  // ---- Search ------------------------------------------------------------------------
  function initSearch() {
    const dialog = $("#search-dialog");
    if (!dialog || typeof dialog.showModal !== "function") return;
    const triggers = $$("[data-search-open]");
    reveal(triggers);
    $$("[data-shortcut-key]").forEach((kbd) => { kbd.textContent = isMac ? "⌘K" : "Ctrl K"; });
    wireDialog(dialog);

    let module = null;
    const open = async () => {
      if (dialog.open) return;
      dialog.showModal();
      try {
        module = module || await import(new URL("search.js", SCRIPT_URL).href);
        module.attach(dialog);
      } catch (error) {
        console.error("Search failed to load", error);
        const view = $("[data-search-view]", dialog);
        view.innerHTML = "";
        const p = document.createElement("p");
        p.className = "search-dialog__group muted";
        p.textContent = "Search could not be loaded. Check your connection and try again.";
        view.append(p);
      }
    };

    triggers.forEach((btn) => btn.addEventListener("click", open));
    document.addEventListener("keydown", (event) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        if (dialog.open) dialog.close(); else open();
      }
    });
  }

  // ---- Code blocks ------------------------------------------------------------------
  function initCopy() {
    const buttons = $$("[data-copy]");
    reveal(buttons);
    buttons.forEach((btn) => btn.addEventListener("click", async () => {
      const code = btn.closest(".code-block")?.querySelector("pre code");
      const label = btn.querySelector("[data-copy-label]");
      if (!code || !label) return;
      let ok = false;
      try {
        await navigator.clipboard.writeText(code.innerText.replace(/\n$/, ""));
        ok = true;
      } catch {
        ok = false;
      }
      btn.dataset.state = ok ? "copied" : "error";
      label.textContent = ok ? "Copied" : "Press Ctrl+C";
      announce(ok ? "Code copied to clipboard" : "Copy failed. Select the code and copy it manually.");
      clearTimeout(btn._reset);
      btn._reset = setTimeout(() => { delete btn.dataset.state; label.textContent = "Copy"; }, 2000);
    }));
  }

  // ---- Table of contents: scroll-spy, progression, section bar ----------------------
  // One scroll-spy drives every TOC on the page (desktop sidebar + the compact
  // section bar on smaller screens). Sections above the current one are marked
  // data-passed so readers can see how far through the piece they are.
  function initToc() {
    const links = $$("[data-toc-link]").filter((a) => !a.closest(".toc--inline"));
    if (!links.length) return;
    const idOf = (a) => decodeURIComponent(a.hash.slice(1));
    const ids = [...new Set(links.map(idOf))];
    const headings = ids.map((id) => document.getElementById(id)).filter(Boolean);
    const sidebar = $("[data-toc]");
    const bar = initSectionBar();
    let currentId = null;

    const setCurrent = (id) => {
      if (id === currentId) return;
      currentId = id;
      const index = ids.indexOf(id);
      links.forEach((a) => {
        const i = ids.indexOf(idOf(a));
        a.toggleAttribute("data-passed", i < index);
        if (i === index) a.setAttribute("aria-current", "true"); else a.removeAttribute("aria-current");
      });
      const active = sidebar && sidebar.querySelector("[aria-current=true]");
      if (active && sidebar.scrollHeight > sidebar.clientHeight) {
        const { offsetTop } = active;
        if (offsetTop < sidebar.scrollTop || offsetTop > sidebar.scrollTop + sidebar.clientHeight - 40) {
          sidebar.scrollTop = offsetTop - sidebar.clientHeight / 3;
        }
      }
      if (bar) bar.setLabel(document.getElementById(id)?.textContent.trim() || "");
    };

    // Current = the last heading above a line 25% down the viewport. Computed
    // on every animation frame while scrolling, so it is correct when a smooth
    // scroll settles (an IntersectionObserver can miss that final position).
    let ticking = false;
    const update = () => {
      ticking = false;
      const line = window.innerHeight * 0.25;
      let current = headings[0];
      for (const h of headings) {
        if (h.getBoundingClientRect().top <= line) current = h; else break;
      }
      if (current) setCurrent(current.id);
      if (bar) bar.update();
    };
    const schedule = () => { if (!ticking) { ticking = true; requestAnimationFrame(update); } };
    window.addEventListener("scroll", schedule, { passive: true });
    window.addEventListener("resize", schedule, { passive: true });
    update();

    // Inline (mobile) TOC closes after navigating.
    $$(".toc--inline a").forEach((a) => a.addEventListener("click", () => a.closest("details")?.removeAttribute("open")));
  }

  // Compact "On this page" bar under the header (below the desktop breakpoint):
  // visible between the article header and the end of the article.
  function initSectionBar() {
    const bar = $("[data-section-bar]");
    const head = $(".article-head");
    const prose = $("[data-prose]");
    if (!bar || !head || !prose) return null;
    const toggle = $(".section-bar__toggle", bar);
    const panel = $(".section-bar__panel", bar);
    const label = $("[data-section-current]", bar);
    reveal([bar]);

    const setOpen = (open) => {
      toggle.setAttribute("aria-expanded", String(open));
      panel.hidden = !open;
    };
    toggle.addEventListener("click", () => setOpen(panel.hidden));
    panel.addEventListener("click", (event) => { if (event.target.closest("a")) setOpen(false); });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && !panel.hidden) { setOpen(false); toggle.focus(); }
    });
    document.addEventListener("click", (event) => { if (!panel.hidden && !bar.contains(event.target)) setOpen(false); });

    return {
      setLabel(text) { label.textContent = text; },
      update() {
        const headerH = parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--header-h")) * 16 || 60;
        const visible = head.getBoundingClientRect().bottom < headerH && prose.getBoundingClientRect().bottom > headerH + 80;
        if (bar.dataset.visible !== String(visible)) {
          bar.dataset.visible = String(visible);
          if (!visible) setOpen(false);
        }
      },
    };
  }

  // ---- Reading progress ----------------------------------------------------------------
  function initProgress() {
    const bar = $("[data-reading-progress]");
    const article = $("[data-prose]");
    if (!bar || !article) return;
    if (article.offsetHeight < window.innerHeight * 1.5) return; // not worth it on short pages
    reveal([bar]);
    let ticking = false;
    const update = () => {
      const rect = article.getBoundingClientRect();
      const total = rect.height - window.innerHeight * 0.6;
      const progress = Math.min(1, Math.max(0, -rect.top / Math.max(total, 1)));
      bar.style.transform = `scaleX(${progress})`;
      ticking = false;
    };
    const schedule = () => { if (!ticking) { ticking = true; requestAnimationFrame(update); } };
    window.addEventListener("scroll", schedule, { passive: true });
    window.addEventListener("resize", schedule, { passive: true });
    update();
  }

  // ---- Newsletter -------------------------------------------------------------------------
  const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

  function initSubscribe() {
    $$("form[data-subscribe]").forEach((form) => {
      reveal([form]);
      const input = form.querySelector("input[type=email]");
      const button = form.querySelector("button[type=submit]");
      const status = form.querySelector(".subscribe-form__status");
      const setStatus = (state, message) => {
        status.dataset.state = state;
        status.textContent = message;
      };

      input.addEventListener("input", () => {
        if (input.getAttribute("aria-invalid") === "true" && EMAIL_RE.test(input.value.trim())) {
          input.removeAttribute("aria-invalid");
          setStatus("", "");
        }
      });

      form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const email = input.value.trim();
        if (!EMAIL_RE.test(email)) {
          input.setAttribute("aria-invalid", "true");
          setStatus("error", email ? "That doesn't look like a valid email address." : "Enter your email address to subscribe.");
          input.focus();
          return;
        }
        input.removeAttribute("aria-invalid");
        button.disabled = true;
        button.setAttribute("aria-busy", "true");
        const label = button.textContent;
        button.textContent = "Subscribing…";
        setStatus("", "");

        try {
          const response = await fetch(form.action, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email }),
          });
          const data = await response.json().catch(() => ({}));
          if (response.ok && data.status !== "error") {
            setStatus("success", data.message === "You're already subscribed!"
              ? "You're already subscribed — nothing else to do."
              : "You're subscribed. The next article will land in your inbox.");
            form.reset();
          } else if (response.status === 400) {
            input.setAttribute("aria-invalid", "true");
            setStatus("error", "That email address was rejected. Please check it and try again.");
          } else {
            throw new Error(`HTTP ${response.status}`);
          }
        } catch (error) {
          console.error("Subscription failed", error);
          setStatus("error", error instanceof TypeError
            ? "Couldn't reach the subscription server. Check your connection and try again."
            : "Something went wrong on our side. Please try again in a minute.");
        } finally {
          button.disabled = false;
          button.removeAttribute("aria-busy");
          button.textContent = label;
        }
      });
    });
  }

  // ---- Client-side filters (tags index, resources) --------------------------------------
  const normalize = (s) => s.toLowerCase().normalize("NFKD").replace(/[̀-ͯ]/g, "").trim();

  function initTagExplorer() {
    const explorer = $("[data-tag-explorer]");
    if (!explorer) return;
    const controls = $("[data-tag-controls]", explorer);
    const text = $("[data-tag-filter]", explorer);
    const topic = $("[data-tag-topic]", explorer);
    const status = $("[data-tag-status]", explorer);
    const empty = $("[data-tag-empty]", explorer);
    const groups = $$("[data-tag-group]", explorer);
    const letters = new Map($$(".letter-jump a", explorer).map((a) => [a.hash.slice(1), a.parentElement]));
    reveal([controls]);

    const params = new URLSearchParams(location.search);
    if (params.get("q")) text.value = params.get("q");
    if (params.get("topic")) topic.value = params.get("topic");

    const apply = () => {
      const q = normalize(text.value);
      const t = topic.value;
      let shown = 0;
      groups.forEach((group) => {
        let groupShown = 0;
        $$("li[data-tag-name]", group).forEach((li) => {
          const match = (!q || normalize(li.dataset.tagName).includes(q)) &&
            (!t || li.dataset.tagCats.split(" ").includes(t));
          li.hidden = !match;
          if (match) groupShown += 1;
        });
        group.hidden = groupShown === 0;
        const letter = letters.get(group.id);
        if (letter) letter.hidden = groupShown === 0;
        shown += groupShown;
      });
      empty.hidden = shown !== 0;
      status.textContent = `${shown} ${shown === 1 ? "tag" : "tags"} shown`;
      const url = new URL(location.href);
      q ? url.searchParams.set("q", text.value.trim()) : url.searchParams.delete("q");
      t ? url.searchParams.set("topic", t) : url.searchParams.delete("topic");
      history.replaceState(null, "", url);
    };
    text.addEventListener("input", apply);
    topic.addEventListener("change", apply);
    if (text.value || topic.value) apply();
  }

  function initResourceFilter() {
    const controls = $("[data-resource-controls]");
    if (!controls) return;
    reveal([controls]);
    const input = $("[data-resource-filter]", controls);
    const status = $("[data-resource-status]", controls);
    const empty = $("[data-resource-empty]");
    input.addEventListener("input", () => {
      const q = normalize(input.value);
      let shown = 0;
      $$("[data-filter-group]").forEach((group) => {
        let n = 0;
        $$("[data-filter-item]", group).forEach((item) => {
          const match = !q || item.dataset.filterText.includes(q);
          item.parentElement.hidden = !match;
          if (match) n += 1;
        });
        group.hidden = n === 0;
        shown += n;
      });
      if (empty) empty.hidden = shown !== 0;
      status.textContent = `${shown} ${shown === 1 ? "resource" : "resources"} shown`;
    });
  }

  // ---- Comments (giscus), loaded on approach -----------------------------------------------
  function giscusTheme() {
    return effectiveTheme() === "dark" ? "dark_dimmed" : "light";
  }

  function initComments() {
    const host = $("[data-giscus]");
    if (!host || !("IntersectionObserver" in window)) return;
    // giscus reports failures (e.g. app not installed) via postMessage; show a
    // plain link to the repository's Discussions instead of an empty box.
    window.addEventListener("message", (event) => {
      if (event.origin !== "https://giscus.app" || !event.data?.giscus?.error) return;
      $("iframe.giscus-frame")?.remove();
      reveal($$("[data-giscus-fallback]"));
    });

    const observer = new IntersectionObserver((entries) => {
      if (!entries.some((e) => e.isIntersecting)) return;
      observer.disconnect();
      const script = document.createElement("script");
      script.src = "https://giscus.app/client.js";
      script.async = true;
      script.crossOrigin = "anonymous";
      Object.entries(host.dataset).forEach(([key, value]) => {
        if (key !== "giscus") script.dataset[key] = value;
      });
      script.dataset.theme = giscusTheme();
      script.dataset.loading = "lazy";
      host.append(script);
    }, { rootMargin: "600px 0px" });
    observer.observe(host);
  }

  // ---- Retire the previous theme's service worker ----------------------------------------------
  function retireServiceWorkers() {
    if (!("serviceWorker" in navigator)) return;
    navigator.serviceWorker.getRegistrations()
      .then((regs) => regs.forEach((reg) => reg.unregister()))
      .catch(() => { /* nothing registered, or blocked by the browser */ });
  }

  const init = [initTheme, initMenu, initSearch, initCopy, initToc, initProgress, initSubscribe,
    initTagExplorer, initResourceFilter, initComments, retireServiceWorkers];
  init.forEach((fn) => {
    try { fn(); } catch (error) { console.error(`${fn.name} failed`, error); }
  });
})();
