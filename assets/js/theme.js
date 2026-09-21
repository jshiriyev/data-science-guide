/* Applies the saved theme before first paint. Load this synchronously in <head>
   so a pinned theme never flashes the other palette. With nothing saved we leave
   data-theme unset and the OS preference wins via the media query in base.css. */
(function () {
  try {
    var saved = localStorage.getItem("dsg-theme");
    if (saved === "light" || saved === "dark") {
      document.documentElement.setAttribute("data-theme", saved);
    }
  } catch (e) {
    /* Private mode or blocked storage: fall back to the OS preference. */
  }
})();

/* Wired up by the [data-theme-toggle] button in the top bar. */
function dsgToggleTheme() {
  var root = document.documentElement;
  var prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  var current = root.getAttribute("data-theme") || (prefersDark ? "dark" : "light");
  var next = current === "dark" ? "light" : "dark";
  root.setAttribute("data-theme", next);
  try {
    localStorage.setItem("dsg-theme", next);
  } catch (e) {
    /* Not persisting is acceptable; the page still switches for this visit. */
  }
}

document.addEventListener("click", function (event) {
  var button = event.target.closest("[data-theme-toggle]");
  if (button) dsgToggleTheme();
});
