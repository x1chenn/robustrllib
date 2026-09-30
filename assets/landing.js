/* The project page: the sections that come in as they scroll into view, the counted
   numbers, the loop of the six sources, the shift toolbox, and the buttons that lead
   nowhere yet. */
(function () {
  "use strict";
  var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var observe = window.IntersectionObserver && !reduced;
  document.documentElement.classList.add("has-js");

  // ---- every block of a section comes in when it scrolls into view, one after another
  (function () {
    var wraps = document.querySelectorAll("section > .wrap, .hero");
    var items = [];
    Array.prototype.forEach.call(wraps, function (wrap) {
      var i = 0;
      Array.prototype.forEach.call(wrap.children, function (child) {
        if (child.matches("script, style, .rl-book, [data-no-reveal]")) { return; }
        child.classList.add("reveal");
        child.style.setProperty("--d", String(Math.min(i, 6)));
        items.push(child);
        i += 1;
      });
    });
    if (!observe) { items.forEach(function (el) { el.classList.add("is-visible"); }); return; }
    var io = new window.IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) { entry.target.classList.add("is-visible"); io.unobserve(entry.target); }
      });
    }, { threshold: 0.1, rootMargin: "0px 0px -36px 0px" });
    items.forEach(function (el) { io.observe(el); });
  }());

  // ---- the five numbers count up once
  (function () {
    var nums = document.querySelectorAll("[data-count]");
    if (!nums.length) { return; }
    function run(el) {
      var target = parseInt(el.getAttribute("data-count"), 10), t0 = null, dur = 1100;
      function step(ts) {
        if (t0 === null) { t0 = ts; }
        var p = Math.min((ts - t0) / dur, 1), eased = 1 - Math.pow(1 - p, 3);
        el.textContent = String(Math.round(eased * target));
        if (p < 1) { window.requestAnimationFrame(step); } else { el.textContent = String(target); }
      }
      window.requestAnimationFrame(step);
    }
    if (!observe) { return; }
    var io = new window.IntersectionObserver(function (entries) {
      entries.forEach(function (entry) { if (entry.isIntersecting) { run(entry.target); io.unobserve(entry.target); } });
    }, { threshold: 0.5 });
    Array.prototype.forEach.call(nums, function (n) { io.observe(n); });
  }());

  // ---- the loop of the six sources: the chain appears from the agent on, then flows
  (function () {
    var scene = document.getElementById("shift-loop-scene");
    if (!scene) { return; }
    var steps = parseInt(scene.getAttribute("data-steps") || "12", 10);
    function flow() { scene.classList.add("flow"); }
    function play() {
      scene.classList.add("play");
      window.setTimeout(flow, steps * 260 + 700);
    }
    if (!observe) { scene.classList.add("play", "still"); return; }
    var io = new window.IntersectionObserver(function (entries) {
      if (entries.some(function (e) { return e.isIntersecting; })) { io.disconnect(); play(); }
    }, { threshold: 0.25 });
    io.observe(scene);
  }());

  // ---- links that are not live yet shake instead of leaving the page
  document.querySelectorAll("[data-blocked]").forEach(function (el) {
    el.addEventListener("click", function (event) {
      event.preventDefault();
      el.animate(
        [{ transform: "translateX(0)" }, { transform: "translateX(-3px)" },
         { transform: "translateX(3px)" }, { transform: "translateX(0)" }],
        { duration: 220 }
      );
    });
  });

  // ---- the shift toolbox: a source, a mode, and what the toolbox offers for the two
  var box = document.getElementById("shift-toolbox");
  var dataNode = document.getElementById("shift-data");
  if (!box || !dataNode) { return; }
  var data;
  try { data = JSON.parse(dataNode.textContent); } catch (e) { return; }
  var sources = data.sources, modes = data.modes;
  var panel = document.getElementById("tb-panel");
  var sourceButtons = Array.prototype.slice.call(box.querySelectorAll(".tb-source"));
  var modeButtons = Array.prototype.slice.call(box.querySelectorAll(".tb-mode"));
  var state = { source: sources[0].key, mode: null };

  function bySource(key) { return sources.filter(function (s) { return s.key === key; })[0]; }
  function byMode(key) { return modes.filter(function (m) { return m.key === key; })[0]; }

  function element(tag, className, text) {
    var node = document.createElement(tag);
    if (className) { node.className = className; }
    if (text !== undefined) { node.textContent = text; }
    return node;
  }

  function render() {
    var source = bySource(state.source);
    if (!source.modes[state.mode]) {
      state.mode = modes.filter(function (m) { return source.modes[m.key]; })[0].key;
    }
    var mode = byMode(state.mode);
    var entry = source.modes[state.mode];

    sourceButtons.forEach(function (b) {
      var on = b.getAttribute("data-source") === state.source;
      b.classList.toggle("is-active", on);
      b.setAttribute("aria-selected", on ? "true" : "false");
    });
    modeButtons.forEach(function (b) {
      var key = b.getAttribute("data-mode");
      var offered = !!source.modes[key];
      var on = key === state.mode;
      b.classList.toggle("is-active", on);
      b.setAttribute("aria-selected", on ? "true" : "false");
      if (offered) { b.removeAttribute("aria-disabled"); b.removeAttribute("title"); }
      else { b.setAttribute("aria-disabled", "true"); b.title = "Not offered for this source"; }
    });

    // the panel is built from text, never from markup
    var figure = element("figure", "tb-figure");
    var img = element("img");
    img.src = source.example.image;
    img.alt = source.example.caption;
    figure.appendChild(img);
    figure.appendChild(element("figcaption", "", source.example.caption));

    var detail = element("div", "tb-detail");
    var title = element("p", "tb-title");
    title.appendChild(element("b", "", source.name));
    title.appendChild(document.createTextNode(" · " + mode.name));
    detail.appendChild(title);
    detail.appendChild(element("p", "tb-blurb", entry.note || ""));
    if (entry.names && entry.names.length) {
      var names = element("p", "tb-names");
      entry.names.forEach(function (n) { names.appendChild(element("code", "", n)); });
      detail.appendChild(names);
    }
    detail.appendChild(element("pre", "code tb-code", entry.code));
    var links = element("p", "tb-links");
    var a = element("a", "", source.name + " in the tutorial"); a.href = source.page;
    var b = element("a", "", mode.name + " mode"); b.href = mode.page;
    links.appendChild(a); links.appendChild(document.createTextNode(" · ")); links.appendChild(b);
    detail.appendChild(links);

    panel.classList.add("is-changing");
    panel.replaceChildren(figure, detail);
    window.requestAnimationFrame(function () { panel.classList.remove("is-changing"); });
  }

  sourceButtons.forEach(function (b) {
    b.addEventListener("click", function () { state.source = b.getAttribute("data-source"); render(); });
  });
  modeButtons.forEach(function (b) {
    b.addEventListener("click", function () {
      var key = b.getAttribute("data-mode");
      if (bySource(state.source).modes[key]) { state.mode = key; render(); }
    });
  });
  box.classList.add("is-live");
  render();
}());
