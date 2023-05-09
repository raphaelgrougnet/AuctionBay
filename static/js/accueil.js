"use strict";
let numero = 0;

const lstSuggestion = document.getElementById("listeSuggestions");
    const searchbar = document.getElementById("search");
    const divSuggestions = document.getElementById("divSuggestions");




async function afficherEncheres(offset) {
    const listeEncheres = document.getElementById("div-encheres");
    for (let i = 0; i < 12; i++) {
        let divPlaceholder = document.createElement("div");
        divPlaceholder.classList.add("col-sm-12", "col-md-6", "col-lg-3", "card-placeholder");
        divPlaceholder.innerHTML = `
                    <div class="card">
                        <span class="placeholder" style="height: 325px;"></span>
                        <div class="card-body d-flex flex-column placeholder-glow">
                            <span class="card-title placeholder col-8 mb-3"></span>
                            <span class="card-text placeholder col-5 mb-3"></span>
                            <a href="" class="btn btn-primary disabled col-6 placeholder"></a>
                        </div>
                    </div>
        `
        listeEncheres.appendChild(divPlaceholder);
    }

    let encheres = await envoyerRequeteAjax("/api/afficher-encheres/" + offset);
    let utilisateur = await recupererUtilisateur();
    document.querySelectorAll(".card-placeholder").forEach((card) => {
        card.classList.add("cacher");
        card.remove();
        });
    if (encheres.length > 0) {
        for (let enchere of encheres) {
            let div = document.createElement("div");
            div.classList.add("col-sm-12", "col-md-6", "col-lg-3");
            if (enchere["est_supprimee"] === 0) {
                div.innerHTML = `<div class="card">
                                    <img src="https://picsum.photos/seed/${enchere["id_enchere"]}/900/1000" class="card-img-top"
                                         alt="Image de {{ e.titre }}">
                                    <div class="card-body">
                                        <h5 class="card-title">${enchere["titre"]}</h5>
                                        <p class="card-text">${new Date(enchere["date_limite"]).getFullYear()}-${new Date(enchere["date_limite"]).getMonth()}-${new Date(enchere["date_limite"]).getDay()}</p>
                                        <a href="/encheres/${enchere["id_enchere"]}" class="btn btn-primary stretched-link">Détails</a>
                                    </div>
                                </div>
                             `


                listeEncheres.appendChild(div);

            }
            else {
                if (utilisateur !== null && utilisateur["est_admin"] === 1) {
                    div.innerHTML = `  <div class="card border-danger">
                                    <img src="https://picsum.photos/seed/${enchere["id_enchere"]}/900/1000" class="card-img-top"
                                         alt="Image de {{ e.titre }}">
                                    <div class="card-body">
                                        <h5 class="card-title">${enchere["titre"]}</h5>
                                        <p class="card-text">${new Date(enchere["date_limite"]).getFullYear()}-${new Date(enchere["date_limite"]).getMonth()}-${new Date(enchere["date_limite"]).getDay()}</p>
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
    if (listeEncheres.childElementCount === 0) {
        listeEncheres.innerHTML = `    <div class="clo-12 alert alert-info mx-3">
                                            <p class="text-center m-0">Aucune enchère n'est disponible pour le moment.</p>
                                       </div>`
    }



}



async function scrollHandler() {
    ///COMMENT ON SAIT QUAND ON ARRIVE A LA FIN ET QUE YA PLUS DE DONNEES A AFFICHER
    ///POURQUOI JE PEUX ENCORE SCROLL MEME QUAND YA AWAIT
    while ((innerHeight + scrollY) > 0.80 * document.body.offsetHeight) {
        await afficherEncheres(numero);
        numero += 12;



    }
}

async function recupererUtilisateur(){
    return envoyerRequeteAjax("/api/recuperer-utilisateur");
}


async function recupererSuggestions(){
    /// AJOUT UN CANCEL AU DEBUT DE LA FONCTION POUR ANNULER LES REQUETES PRECEDENTES
    lstSuggestion.innerHTML = `
        <li class="d-flex justify-content-center"><div class="race-by"></div></li>
    `;
    let suggestions = await envoyerRequeteAjax("/api/recuperer-suggestions/" + searchbar.value);

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


async function initialize() {
    searchbar.addEventListener("input", typeSearchHandler);
    await scrollHandler()
    window.addEventListener("scroll", scrollHandler)

}

window.addEventListener("load", initialize)
