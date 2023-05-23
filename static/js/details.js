"use strict"

const id = window.location.href.substring(window.location.href.lastIndexOf('/') + 1)
const champMise = document.getElementById("mise")
const champFeedback = document.getElementById("feedback")
const inputMise = document.getElementById("motant_miser")
const formMise = document.getElementById("form-mise")
const btnMiser = document.getElementById("miser")
let envoieMise = false

/**
 * Récupère l'utilisateur connecté(e)
 * @returns {Promise<Record<string, *>>}
 */
async function recupererUtilisateur(){
    return envoyerRequeteAjax("/api/recuperer-utilisateur");
}

/**
 * Permet d'afficher les mises
 * @param mise une mise
 * @param user un utilisateur
 */
function afficherMise(mise, user){
    if(mise == null){
        champMise.innerHTML = "Il n'y a aucune mise pour cette enchère."
    }
    else {
        if(mise.fk_miseur === user.id_utilisateur){
            champMise.innerHTML = `<span class="text-info">Vous avez la plus grande mise : ${mise.montant}$</span>`
        }
        else{
            champMise.innerHTML = `Plus grande mise : ${mise.montant}$`
        }
    }
}

/**
 * Gère le submission du formulaire de mise
 * @param e event
 * @returns {Promise<void>}
 */
async function gererSubmit(e){
    e.preventDefault()
    try{
        btnMiser.innerHTML = "<div class=\"race-by my-2\"></div>"
        btnMiser.disabled = true
        let msg = ""
        const mise = await envoyerRequeteAjax(`/api/recuperer-mise/${id}`, "GET")

        if(envoieMise){
            return
        }
        envoieMise = true
        if(Number(inputMise.value) === 0){
            msg = "Vous devez mettre un montant"
        }
        else if(Number(inputMise.value) <= mise.montant){
            msg = "Vous devez faire une mise plus grande que celle affichée"
        }
        else if(Number(inputMise.value) > 2147483647){
            msg = "Le montant ne peut pas dépasser 2147483647"
        }
        else{
            msg = ""
        }

        btnMiser.innerHTML = "Miser"
        btnMiser.disabled = false
        envoieMise = false
        if(msg !== ""){
            inputMise.classList.remove("is-valid")
            inputMise.classList.add("is-invalid")
            champFeedback.innerHTML = `${msg}`
            return
        }
        champFeedback.innerHTML = ""
        inputMise.classList.remove("is-invalid")
        inputMise.classList.add("is-valid")
        let miseAEnvoyer = {
            id : id,
            motant_miser : Number(inputMise.value)
        }
        await envoyerRequeteAjax("/api/miser", "POST", miseAEnvoyer)
        await rafraichirMise()
        inputMise.value = ""

    }
    catch (error){

    }
}

/**
 * Rafraichit les mises
 * @returns {Promise<void>}
 */
async function rafraichirMise(){
    try{
        const mise = await envoyerRequeteAjax(`/api/recuperer-mise/${id}`, "GET")
        const user = await recupererUtilisateur()

        afficherMise(mise, user)
    }
    catch (erreur){
        console.error("Une erreur est survenue")
        console.error(erreur)
    }

}

async function initialisation(){
    formMise.addEventListener("submit", gererSubmit)
    await rafraichirMise()
    setInterval(rafraichirMise, 1000)
}

window.addEventListener("load", initialisation)