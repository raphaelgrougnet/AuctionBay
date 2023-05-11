"use strict";
let numero = 0;
let controler = null;
const lstSuggestion = document.getElementById("listeSuggestions");
const searchbar = document.getElementById("search");
const divSuggestions = document.getElementById("divSuggestions");
const btnSearch = document.getElementById("btnSearch");
const listeEncheres = document.getElementById("div-encheres");
const loaderEncheres = document.getElementById("loader-encheres");
let recherche = ""
const offset = 14

/**
 * Fonction qui permet d'afficher les enchères sur la page d'accueil
 * @param pOffset
 * @param recherche
 * @returns {Promise<{[p: string]: *}>}
 */
async function afficherEncheres(pOffset, recherche = "") {

    // for (let i = 0; i < offset; i++) {
    //     let divPlaceholder = document.createElement("div");
    //     divPlaceholder.classList.add("col-sm-12", "col-md-6", "col-lg-3", "card-placeholder");
    //     divPlaceholder.innerHTML = `
    //                 <div class="card">
    //                     <span class="placeholder" style="height: 325px;"></span>
    //                     <div class="card-body d-flex flex-column placeholder-glow">
    //                         <span class="card-title placeholder col-8 mb-3"></span>
    //                         <span class="card-text placeholder col-5 mb-3"></span>
    //                         <a href="" class="btn btn-primary disabled col-6 placeholder"></a>
    //                     </div>
    //                 </div>
    //     `
    //     listeEncheres.appendChild(divPlaceholder);
    // }

    //Affichage du loader
    loaderEncheres.classList.remove("cacher");



    //Recuperation des enchères avec AJAX
    let encheres;
    if (recherche === "") {
        encheres = await envoyerRequeteAjax("/api/afficher-encheres/" + pOffset);
    }
    else {
        encheres = await envoyerRequeteAjax("/api/afficher-encheres/" + pOffset + "/" + recherche);
    }

    //Recuperation de l'utilisateur
    let utilisateur = await recupererUtilisateur();

    //Affichage des enchères
    if (encheres.length > 0) {
        for (let enchere of encheres) {
            let div = document.createElement("div");
            div.classList.add("col-sm-12", "col-md-6", "col-lg-3");
            let year = new Date(enchere["date_limite"]).toLocaleString("default", { year: "numeric" });
            let month = new Date(enchere["date_limite"]).toLocaleString("default", { month: "2-digit" });
            let day = new Date(enchere["date_limite"]).toLocaleString("default", { day: "2-digit" });
            if (enchere["est_supprimee"] === 0) {
                div.innerHTML = `<div class="card">
                                    <img src="https://picsum.photos/seed/${enchere["id_enchere"]}/900/1000" class="card-img-top"
                                         alt="Image de {{ e.titre }}">
                                    <div class="card-body">
                                        <h5 class="card-title">${enchere["titre"]}</h5>
                                        <p class="card-text">${day}-${month}-${year}</p>
                                        <a href="/encheres/${enchere["id_enchere"]}" class="btn btn-primary stretched-link">Détails</a>
                                    </div>
                                </div>
                             `


                listeEncheres.appendChild(div);

            }
            else {
                if (utilisateur !== null && utilisateur["est_admin"] === 1) {
                    div.innerHTML = `  
                                <div class="card border-danger">
                                    <img src="https://picsum.photos/seed/${enchere["id_enchere"]}/900/1000" class="card-img-top"
                                         alt="Image de {{ e.titre }}">
                                    <div class="card-body">
                                        <h5 class="card-title">${enchere["titre"]}</h5>
                                        <p class="card-text">${day}-${month}-${year}</p>
                                        <p class="card-text text-muted">Supprimée</p>
                                        <a href="/encheres/${enchere["id_enchere"]}" class="btn btn-primary stretched-link">Détails</a>
                                    </div>
                                </div>
                             `

                    listeEncheres.appendChild(div);
                }


            }


        }
    }
    ///Cache le loader
    loaderEncheres.classList.add("cacher");

    //Affichage du message d'aucune enchère
    if (listeEncheres.childElementCount === 0) {
        listeEncheres.innerHTML = `    <div class="clo-12 alert alert-info mx-3">
                                            <p class="text-center m-0">Aucune enchère n'est disponible pour le moment.</p>
                                       </div>`
    }

    ///Retourne les enchères pour vérifier s'il y en a encore à afficher
    return encheres;

}


/**
 * Fonction qui permet de gérer le scroll de la page d'accueil afin d'ajouter des enchères continuellement
 * tant qu'on voit le bas de la page et qu'il y a des enchères à afficher
 * @returns {Promise<void>}
 */
async function scrollHandler() {
    while ((innerHeight + scrollY) > 0.85 * document.body.offsetHeight) {

        ///Si il n'y a rien dans la recherche
        if (searchbar.value === "") {
            ///Remove le scrollHandler pour ne pas faire de requête AJAX en boucle
            window.removeEventListener("scroll", scrollHandler);
            ///Afficher les enchères
            let enchereActive = await afficherEncheres(numero);
            ///Ajout du scrollHandler pour pouvoir faire une nouvelle requête AJAX
            window.addEventListener("scroll", scrollHandler);
            ///S'il n'y a plus d'enchère à afficher, on enlève le scrollHandler
            if (enchereActive.length === 0) {
                window.removeEventListener("scroll", scrollHandler);

                break
            }
            //Ajout de l'offset pour la prochaine requête AJAX
            numero +=offset;
        }
        ///Si il y a quelque chose dans la recherche
        else {
            ///Remove le scrollHandler pour ne pas faire de requête AJAX en boucle
            window.removeEventListener("scroll", scrollHandler);
            ///Afficher les enchères
            let enchereActive=  await afficherEncheres(numero, recherche);
            ///Ajout de l'offset pour la prochaine requête AJAX
            numero += offset;
            ///Ajout du scrollHandler pour pouvoir faire une nouvelle requête AJAX
            window.addEventListener("scroll", scrollHandler);
            ///S'il n'y a plus d'enchère à afficher, on enlève le scrollHandler
            if (enchereActive.length === 0) {
                window.removeEventListener("scroll", scrollHandler);

                break

            }

        }
    }

}

/**
 * Fonction qui permet de récupérer l'utilisateur
 * @returns {Promise<Record<string, *>>}
 */
async function recupererUtilisateur(){
    return envoyerRequeteAjax("/api/recuperer-utilisateur");
}

/**
 * Fonction qui permet de récupérer les suggestions de recherche
 * @returns {Promise<void>}
 */
async function recupererSuggestions(){
    ///Affiche le loader
    lstSuggestion.innerHTML = `
        <li class="d-flex justify-content-center"><div class="race-by"></div></li>
    `

    if (controler != null) {
        // Annuler la requête précédente, car on lancera une nouvelle requête
        // à chaque input et on ne veut plus le résultat de la requête précédente.
        controler.abort();
    }

    controler = new AbortController()

    ///Recuperation des suggestions
    let suggestions = await envoyerRequeteAjax("/api/recuperer-suggestions/" + searchbar.value, "GET", {}, controler);

    ///Affichage des suggestions
    ///S'il n'y a pas de suggestions
    if (suggestions.length === 0){
        ///Vide la liste de suggestions
        lstSuggestion.innerHTML = "";
        ///Création d'un li pour afficher qu'il n'y a pas de suggestions
        let li = document.createElement("li");
        li.innerText = "Aucune suggestion";
        lstSuggestion.appendChild(li);
    }
    else {
        ///Vide la liste de suggestions
        lstSuggestion.innerHTML = "";
        ///Création d'un li pour chaque suggestion
        for (let suggestion of suggestions){
            let li = document.createElement("li");
            let a = document.createElement("a");
            a.href = "/encheres/" + suggestion["id_enchere"];
            a.innerText = suggestion["titre"];
            li.appendChild(a);
            lstSuggestion.appendChild(li);
        }
    }

}

/**
 * Fonction qui permet de gérer l'input de la barre de recherche
 * @returns {Promise<void>}
 */
async function typeSearchHandler(){
    ///Si la recherche contient plus de 2 caractères
    if (searchbar.value.trim().length > 2){
        ///Affiche la div de suggestions
        divSuggestions.classList.remove("cacher");
        ///Recuperate les suggestions
        await recupererSuggestions();
    }
    else {
        ///Cache la div de suggestions
        divSuggestions.classList.add("cacher");
        ///Vide la liste de suggestions
        lstSuggestion.innerHTML = "";
    }
}

/**
 * Fonction qui permet de gérer le click sur le bouton de recherche
 * @returns {Promise<void>}
 */
async function clickSearchHandler(){
    window.addEventListener("scroll", scrollHandler)
    divSuggestions.classList.add("cacher");
    lstSuggestion.innerHTML = "";
    listeEncheres.innerHTML = "";
    recherche = searchbar.value;
    numero = 0
    await scrollHandler()
    // await afficherEncheres(0, recherche)
    numero = offset;

}

/**
 * Fonction qui permet de fermer le menu de suggestions de recherche
 */
function fermerMenu(){
     // Remplacez 'menu' par l'ID de votre menu

    document.addEventListener('click', function(event) {
    let estClicDansMenu = divSuggestions.contains(event.target); // Vérifie si le clic est à l'intérieur du menu
    estClicDansMenu = searchbar.contains(event.target); // Vérifie si le clic est à l'intérieur du menu

    if (!estClicDansMenu) {
      // Fermer le menu ici
      divSuggestions.classList.add("cacher");
    }
  });
}

async function initialize() {
    fermerMenu()
    searchbar.addEventListener("input", typeSearchHandler);
    searchbar.addEventListener("focus", typeSearchHandler);
    btnSearch.addEventListener("click", clickSearchHandler);
    searchbar.addEventListener("keydown", function(e){
        if (e.key === "Enter"){
            clickSearchHandler();
        }
    })
    await scrollHandler()
    window.addEventListener("scroll", scrollHandler)

}

window.addEventListener("load", initialize)
