/* ==========================================================================
   Cheat-sheet behaviour, shared by every sheet in the repo.

   Everything here is derived from the markup, so a new sheet only needs the
   right structure -- <section class="section" id="..."> with an <h2> and
   .card children -- and it gets a table of contents, search, scrollspy and
   copy buttons for free. No per-sheet configuration.
   ========================================================================== */
(function () {
  "use strict";

  var sections = Array.prototype.slice.call(document.querySelectorAll(".section"));
  if (!sections.length) return;

  /* --- Table of contents, built from each section's heading --------------- */

  var tocList = document.querySelector("[data-toc]");
  var tocLinks = [];

  if (tocList) {
    sections.forEach(function (section) {
      var heading = section.querySelector("h2");
      if (!heading || !section.id) return;
      var link = document.createElement("a");
      link.href = "#" + section.id;
      link.textContent = heading.textContent.trim();
      tocList.appendChild(link);
      tocLinks.push({ link: link, section: section });
    });
  }

  /* --- Copy buttons ------------------------------------------------------- */

  document.querySelectorAll(".code").forEach(function (block) {
    var pre = block.querySelector("pre");
    if (!pre) return;

    var button = document.createElement("button");
    button.type = "button";
    button.className = "code__copy";
    button.textContent = "copy";
    button.setAttribute("aria-label", "Copy code to clipboard");

    button.addEventListener("click", function () {
      var done = function (ok) {
        button.textContent = ok ? "copied" : "failed";
        setTimeout(function () { button.textContent = "copy"; }, 1200);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(pre.innerText).then(function () { done(true); },
                                                          function () { done(false); });
      } else {
        done(false);
      }
    });

    block.appendChild(button);
  });

  /* --- Search ------------------------------------------------------------- */

  var input = document.querySelector("[data-search]");
  var count = document.querySelector("[data-search-count]");
  var empty = document.querySelector("[data-empty]");

  /* Cache the searchable text once: re-reading textContent on every keystroke
     is what makes naive filters feel sluggish on a long sheet. */
  var cards = Array.prototype.slice.call(document.querySelectorAll(".card")).map(function (card) {
    var section = card.closest(".section");
    var sectionTitle = section && section.querySelector("h2")
      ? section.querySelector("h2").textContent
      : "";
    return {
      el: card,
      section: section,
      haystack: (sectionTitle + " " + card.textContent).toLowerCase().replace(/\s+/g, " ")
    };
  });

  function applyFilter(raw) {
    var terms = raw.toLowerCase().split(/\s+/).filter(Boolean);
    var shown = 0;

    cards.forEach(function (card) {
      /* Every term must appear somewhere in the card -- lets you narrow with
         "join left" the same way you would in a search box. */
      var match = terms.every(function (term) { return card.haystack.indexOf(term) !== -1; });
      card.el.classList.toggle("is-hidden", !match);
      if (match) shown++;
    });

    /* Hide a section once all of its cards are filtered out. */
    sections.forEach(function (section) {
      var visible = section.querySelectorAll(".card:not(.is-hidden)").length;
      section.classList.toggle("is-hidden", terms.length > 0 && visible === 0);
    });

    if (count) {
      count.textContent = terms.length
        ? shown + " of " + cards.length + " blocks match"
        : "";
    }
    if (empty) empty.classList.toggle("is-hidden", shown > 0 || !terms.length);
  }

  if (input) {
    input.addEventListener("input", function () { applyFilter(input.value); });

    document.addEventListener("keydown", function (event) {
      /* "/" focuses search, Escape clears it -- the shortcuts people expect. */
      if (event.key === "/" && document.activeElement !== input) {
        event.preventDefault();
        input.focus();
        input.select();
      } else if (event.key === "Escape" && document.activeElement === input) {
        input.value = "";
        applyFilter("");
        input.blur();
      }
    });
  }

  /* --- Scrollspy ---------------------------------------------------------- */

  if (tocLinks.length && "IntersectionObserver" in window) {
    var visible = new Set();

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) visible.add(entry.target);
        else visible.delete(entry.target);
      });

      /* Highlight the topmost section currently on screen. */
      var first = null;
      tocLinks.forEach(function (item) {
        if (!first && visible.has(item.section)) first = item;
      });
      tocLinks.forEach(function (item) {
        item.link.classList.toggle("is-active", item === first);
      });
    }, { rootMargin: "-72px 0px -60% 0px", threshold: 0 });

    tocLinks.forEach(function (item) { observer.observe(item.section); });
  }
})();
