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
    let encheres = {};
    if (recherche === "") {
        encheres = await envoyerRequeteAjax("/api/afficher-encheres/" + pOffset);
    }
    else {
        encheres = await envoyerRequeteAjax("/api/afficher-encheres/" + pOffset + "/" + recherche);
    }

    //Recuperation de l'utilisateur
    let utilisateur = await recupererUtilisateur();


    // document.querySelectorAll(".card-placeholder").forEach((card) => {
    //     // card.classList.add("cacher");
    //     card.remove();
    //     });

    //Cacher le loader


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
    loaderEncheres.classList.add("cacher");
    //Affichage du message d'aucune enchère
    if (listeEncheres.childElementCount === 0) {
        listeEncheres.innerHTML = `    <div class="clo-12 alert alert-info mx-3">
                                            <p class="text-center m-0">Aucune enchère n'est disponible pour le moment.</p>
                                       </div>`
    }

    return encheres;

}



async function scrollHandler() {
    ///COMMENT ON SAIT QUAND ON ARRIVE A LA FIN ET QUE YA PLUS DE DONNEES A AFFICHER
    ///POURQUOI JE PEUX ENCORE SCROLL MEME QUAND YA AWAIT

    while ((innerHeight + scrollY) > 0.85 * document.body.offsetHeight) {

        if (searchbar.value === "") {
            window.removeEventListener("scroll", scrollHandler);
            let enchereActive = await afficherEncheres(numero);
            window.addEventListener("scroll", scrollHandler);
            if (enchereActive.length === 0) {
                window.removeEventListener("scroll", scrollHandler);

                break
            }
            numero +=offset;
        }
        else {
            window.removeEventListener("scroll", scrollHandler);

            let enchereActive=  await afficherEncheres(numero, recherche);
            numero += offset;
            window.addEventListener("scroll", scrollHandler);
            if (enchereActive.length === 0) {
                window.removeEventListener("scroll", scrollHandler);

                break

            }

        }
    }

}

async function recupererUtilisateur(){
    return envoyerRequeteAjax("/api/recuperer-utilisateur");
}


async function recupererSuggestions(){
    lstSuggestion.innerHTML = `
        <li class="d-flex justify-content-center"><div class="race-by"></div></li>
    `

    if (controler != null) {
        // Annuler la requête précédente, car on lancera une nouvelle requête
        // à chaque input et on ne veut plus le résultat de la requête précédente.
        controler.abort();
    }

    controler = new AbortController()
    let suggestions = await envoyerRequeteAjax("/api/recuperer-suggestions/" + searchbar.value, "GET", {}, controler);

    if (suggestions.length === 0){
        lstSuggestion.innerHTML = "";
        let li = document.createElement("li");
        li.innerText = "Aucune suggestion";
        lstSuggestion.appendChild(li);
    }
    else {
        lstSuggestion.innerHTML = "";
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

async function typeSearchHandler(){
    if (searchbar.value.trim().length > 2){
        divSuggestions.classList.remove("cacher");
        await recupererSuggestions();
    }
    else {
        divSuggestions.classList.add("cacher");
        lstSuggestion.innerHTML = "";
    }
}

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


async function initialize() {
    searchbar.addEventListener("input", typeSearchHandler);
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
