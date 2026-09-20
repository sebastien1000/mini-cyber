// Remplit la zone de texte avec un exemple, pour tester l'outil sans avoir à taper.
document.addEventListener("DOMContentLoaded", function () {
  const zoneTexte = document.getElementById("zone-texte");

  const exemples = {
    piege:
      "Cher client, votre compte sera bloqué sous 24h. Confirmez votre mot de passe " +
      "immédiatement ici : http://192.168.1.1@faux-banque.com/verif",
    sur: "Bonjour Sébastien, voici le compte-rendu de notre réunion d'hier. À bientôt, Marie.",
  };

  document.querySelectorAll("[data-exemple]").forEach(function (bouton) {
    bouton.addEventListener("click", function () {
      zoneTexte.value = exemples[bouton.dataset.exemple];
    });
  });
});
