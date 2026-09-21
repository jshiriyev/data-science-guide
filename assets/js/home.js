/* Renders the landing page from window.DSG_CATALOG (data/catalog.js), which
   tools/build_catalog.py regenerates from whatever .html files are actually
   present. Nothing on this page is hand-maintained. */
(function () {
  "use strict";

  var catalog = window.DSG_CATALOG;
  var mount = document.querySelector("[data-subjects]");
  if (!mount) return;

  if (!catalog || !Array.isArray(catalog.subjects)) {
    mount.innerHTML =
      '<p class="soon">Catalog failed to load. Run <code>python tools/build_catalog.py</code>.</p>';
    return;
  }

  var totalSheets = 0;
  var subjectsWithSheets = 0;
  var fragment = document.createDocumentFragment();

  catalog.subjects.forEach(function (subject, index) {
    var sheets = subject.sheets || [];
    totalSheets += sheets.length;
    if (sheets.length) subjectsWithSheets++;

    var section = document.createElement("section");
    section.className = "subject";
    section.id = subject.id;

    var head = document.createElement("div");
    head.className = "subject__head";

    var number = document.createElement("span");
    number.className = "subject__n";
    number.textContent = String(index + 1).padStart(2, "0");

    var heading = document.createElement("h2");
    heading.textContent = subject.title;

    var badge = document.createElement("span");
    badge.className = sheets.length ? "tag tag--accent" : "tag";
    badge.textContent = sheets.length
      ? sheets.length + (sheets.length === 1 ? " sheet" : " sheets")
      : "planned";

    head.append(number, heading, badge);

    var blurb = document.createElement("p");
    blurb.className = "subject__blurb";
    blurb.textContent = subject.blurb || "";

    section.append(head, blurb);

    if (sheets.length) {
      var grid = document.createElement("div");
      grid.className = "sheets";

      sheets.forEach(function (sheet) {
        var card = document.createElement("a");
        card.className = "sheet-card";
        card.href = sheet.href;

        var title = document.createElement("span");
        title.className = "sheet-card__t";
        title.textContent = sheet.title;
        card.appendChild(title);

        if (sheet.blurb) {
          var text = document.createElement("p");
          text.className = "sheet-card__b";
          text.textContent = sheet.blurb;
          card.appendChild(text);
        }

        grid.appendChild(card);
      });

      section.appendChild(grid);
    } else {
      var placeholder = document.createElement("p");
      placeholder.className = "soon";
      placeholder.textContent = "No cheat sheet here yet.";
      section.appendChild(placeholder);
    }

    fragment.appendChild(section);
  });

  mount.appendChild(fragment);

  var counts = {
    sheets: totalSheets,
    subjects: catalog.subjects.length,
    covered: subjectsWithSheets
  };
  Object.keys(counts).forEach(function (key) {
    var node = document.querySelector('[data-count="' + key + '"]');
    if (node) node.textContent = counts[key];
  });
})();
