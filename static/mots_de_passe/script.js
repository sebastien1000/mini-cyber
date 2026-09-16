// On attend que la page soit entièrement chargée avant de chercher les éléments
document.addEventListener("DOMContentLoaded", function () {
  // querySelectorAll récupère TOUS les boutons "Copier" de la page (il peut y en avoir plusieurs)
  const boutons = document.querySelectorAll(".bouton-copier");

  boutons.forEach(function (bouton) {
    bouton.addEventListener("click", function () {
      // data-cible contient l'id de l'élément à copier (ex: "mot-de-passe-genere")
      const cible = document.getElementById(bouton.dataset.cible);
      const texte = cible.textContent;

      // navigator.clipboard est l'API du navigateur pour copier dans le presse-papiers
      navigator.clipboard.writeText(texte).then(function () {
        const texteOriginal = bouton.textContent;
        bouton.textContent = "Copié !";
        setTimeout(function () {
          bouton.textContent = texteOriginal;
        }, 1500);
      });
    });
  });

  // Le bouton "Supprimer" : vide le champ et cache le résultat de vérification
  const boutonEffacer = document.getElementById("bouton-effacer");

  if (boutonEffacer) {
    boutonEffacer.addEventListener("click", function () {
      document.getElementById("champ-mot-de-passe-teste").value = "";
      document.getElementById("resultat-verification").innerHTML = "";
    });
  }
});
