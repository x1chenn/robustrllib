/* Filters of the task cards: a family and a regime; both default to all. */
(function () {
  "use strict";
  var root = document.getElementById("tasks");
  if (!root) { return; }
  var state = { family: "all", regime: "all" };
  var cards = Array.prototype.slice.call(root.querySelectorAll(".task"));
  var empty = root.querySelector(".task-empty");
  function apply() {
    var shown = 0;
    cards.forEach(function (c) {
      var ok = (state.family === "all" || c.getAttribute("data-family") === state.family)
            && (state.regime === "all" || c.getAttribute("data-regime").split(" ").indexOf(state.regime) >= 0);
      c.hidden = !ok; if (ok) { shown += 1; }
    });
    if (empty) { empty.hidden = shown > 0; }
  }
  Array.prototype.forEach.call(root.querySelectorAll(".fbtn"), function (b) {
    b.addEventListener("click", function () {
      var key = b.hasAttribute("data-family") ? "family" : "regime";
      state[key] = b.getAttribute("data-" + key);
      Array.prototype.forEach.call(b.parentNode.querySelectorAll(".fbtn"), function (o) { o.classList.toggle("is-active", o === b); });
      apply();
    });
  });
  apply();
}());
