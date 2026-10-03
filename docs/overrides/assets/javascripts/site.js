// Runs on every `document$` page change (navigation.instant swaps pages without a reload); terminal parsing after FastAPI's custom.js (MIT).
(function () {
  "use strict";

  const escapeHtml = (text) =>
    text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

  // In a ```console block: `$ ` starts a command, `---> 100%` is a progress bar, `// ` a remark, the rest is output.
  function parse(text) {
    const lines = [];
    let output = [];
    const flush = () => {
      if (output.length) {
        lines.push({ value: output.map(escapeHtml).join("<br>"), delay: 0 });
        output = [];
      }
    };
    for (const line of text.replace(/\n$/, "").split("\n")) {
      if (line.startsWith("$ ")) {
        flush();
        lines.push({ type: "input", value: escapeHtml(line.slice(2)) });
      } else if (line === "---> 100%") {
        flush();
        lines.push({ type: "progress" });
      } else if (line.startsWith("// ")) {
        flush();
        lines.push({ value: escapeHtml(line.slice(3)), class: "termynal-comment", delay: 0 });
      } else {
        output.push(line);
      }
    }
    flush();
    return lines;
  }

  function animateTerminals() {
    const still = matchMedia("(prefers-reduced-motion: reduce)").matches;
    const visible = new IntersectionObserver((entries, observer) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          observer.unobserve(entry.target);
          entry.target.termynal.init();
        }
      }
    });
    document.querySelectorAll(".termy .highlight code").forEach((code) => {
      if (code.dataset.termy) return;
      code.dataset.termy = "done";
      const source = code.textContent;
      const lines = parse(source);
      // The copy button copies this element's text: leave the commands, without `$ ` or output.
      code.textContent = source
        .split("\n")
        .filter((line) => line.startsWith("$ "))
        .map((line) => line.slice(2))
        .join("\n");
      code.style.display = "none";
      const screen = document.createElement("div");
      code.after(screen);
      // Reduced motion: every delay at its minimum, so the terminal appears complete at once.
      const delays = still ? { startDelay: 1, typeDelay: 1, lineDelay: 1 } : { lineDelay: 500 };
      screen.termynal = new Termynal(screen, { lineData: lines, noInit: true, ...delays });
      visible.observe(screen);
    });
  }

  // The theme keeps the page on a language switch only when its sitemaps load in a lucky order (the root address is a prefix of /ru/).
  function keepPageOnLanguageSwitch() {
    const links = [...document.querySelectorAll("a[hreflang]")];
    const here = location.href.split("#")[0];
    // The header survives a page change, so the language's own address is kept beside the link.
    const bases = links.map((link) => (link.dataset.base ??= link.href.replace(/\/?$/, "/")));
    const current = bases.filter((base) => here.startsWith(base)).sort((a, b) => b.length - a.length)[0];
    if (!current) return;
    links.forEach((link, index) => {
      const base = bases[index];
      link.href = base;
      if (base === current) return;
      const samePage = base + here.slice(current.length);
      // A slow or failed request leaves the link on the other language's home page.
      fetch(samePage, { method: "HEAD", signal: AbortSignal.timeout(3000) })
        .then((answer) => {
          if (answer.ok && location.href.split("#")[0] === here) link.href = samePage;
        })
        .catch(() => {});
    });
  }

  document$.subscribe(() => {
    animateTerminals();
    keepPageOnLanguageSwitch();
  });
})();
