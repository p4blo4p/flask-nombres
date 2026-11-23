/* Significados de Nombres — JS mínimo
   - Filtro de búsqueda en la portada (sin servidor)
   - Smooth scroll al índice alfabético
   Nada más: el sitio es estático y no necesita framework. */
(function () {
  "use strict";

  const input = document.getElementById("search-input");
  if (!input) return;

  const cards = Array.from(document.querySelectorAll(".name-card"));
  const groups = Array.from(document.querySelectorAll(".letter-group"));
  const alphaLinks = Array.from(document.querySelectorAll(".alpha-link"));

  function filter() {
    const q = input.value.trim().toLowerCase();
    let visibleByGroup = {};

    cards.forEach(function (card) {
      const name = (card.getAttribute("data-name") || "").toLowerCase();
      const match = q === "" || name.indexOf(q) !== -1;
      card.style.display = match ? "" : "none";
      // Buscar el grupo padre
      const group = card.closest(".letter-group");
      if (group) {
        const gid = group.id;
        visibleByGroup[gid] = (visibleByGroup[gid] || 0) + (match ? 1 : 0);
      }
    });

    // Ocultar grupos vacíos
    groups.forEach(function (g) {
      g.style.display = visibleByGroup[g.id] > 0 ? "" : "none";
    });

    // Ocultar letras sin resultados
    alphaLinks.forEach(function (link) {
      const target = link.getAttribute("href").replace("#", "");
      const visible = visibleByGroup[target] > 0;
      link.style.opacity = visible ? "" : "0.3";
      link.style.pointerEvents = visible ? "" : "none";
    });
  }

  input.addEventListener("input", filter);
  // Atajo: pulsar "/" enfoca el buscador
  document.addEventListener("keydown", function (e) {
    if (e.key === "/" && document.activeElement !== input) {
      e.preventDefault();
      input.focus();
    }
  });
})();
