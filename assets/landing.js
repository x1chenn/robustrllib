/* The project page: the shift toolbox, and the buttons that lead nowhere yet. */
(function () {
  "use strict";

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
