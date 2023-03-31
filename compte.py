from flask import Flask, redirect, render_template, request, abort, session, Blueprint
import hashlib

import bd

bp_compte = Blueprint('compte', __name__)


def hacher_mdp(mdp_en_clair):
    """Prend un mot de passe en clair et lui applique une fonction de hachage"""
    return hashlib.sha512(mdp_en_clair.encode()).hexdigest()


@bp_compte.route('/connexion', methods=['GET', 'POST'])
def connexion():
    """Permet de se connecter"""
    with bd.creer_connexion() as conn:
        if request.method == 'POST':

            courriel = request.form.get('courriel', default="")
            mdp = request.form.get('mdp', default="")

            mdpHashed = hacher_mdp(mdp)

            utilisateur_trouve = bd.get_compte(conn, courriel, mdpHashed)
            if utilisateur_trouve:
                session.permanent = True
                session["utilisateur"] = utilisateur_trouve
                return redirect("/", 303)

            if not utilisateur_trouve:
                return render_template('compte/connexion.jinja', classe_erreur="is-invalid")
        return render_template('compte/connexion.jinja', utilisateur=session.get("utilisateur"))


@bp_compte.route('/deconnexion')
def deconnexion():
    """Permet de se déconnecter"""
    session.pop("utilisateur", None)
    return redirect("/", 303)


@bp_compte.route('/inscription', methods=['GET', 'POST'])
def inscription():
    """Permet d'inscrire un utilisateur"""
    with bd.creer_connexion() as conn:
        if request.method == 'POST':

            courriel = request.form.get('courriel', default="")
            mdp = request.form.get('mdp', default="")
            mdp_confirm = request.form.get('mdp_confirm', default="")
            nom = request.form.get('nom', default="")

            mdpHashed = hacher_mdp(mdp)

            utilisateur_trouve = bd.get_compte(conn, courriel, mdpHashed)

            classe_erreur_email = ""
            contenu_erreur_email = ""
            classe_erreur_nom = ""
            classe_erreur_mdp = ""
            contenu_erreur_mdp = ""
            classe_erreur_mdp_confirm = ""

            if nom == "":
                classe_erreur_nom = "is-invalid"
            else:
                classe_erreur_nom = "is-valid"

            if courriel == "":
                classe_erreur_email = "is-invalid"
                contenu_erreur_email = "Le courriel est obligatoire."
            elif utilisateur_trouve:
                classe_erreur_email = "is-invalid"
                contenu_erreur_email = "Le courriel est déjà associé à un autre utilisateur."
            else:
                classe_erreur_email = "is-valid"

            if mdp == "":
                classe_erreur_mdp = "is-invalid"
                contenu_erreur_mdp = "Le mot de passe est obligatoire."

            if mdp != mdp_confirm:
                classe_erreur_mdp_confirm = "is-invalid"
                classe_erreur_mdp = "is-invalid"
                contenu_erreur_mdp = "Les mots de passe ne correspondent pas."

            if classe_erreur_email != "is-valid" or classe_erreur_nom != "is-valid" or classe_erreur_mdp != "" or classe_erreur_mdp_confirm != "":
                return render_template('compte/inscription.jinja',
                                       classe_erreur_email=classe_erreur_email,
                                       contenu_erreur_email=contenu_erreur_email,
                                       classe_erreur_nom=classe_erreur_nom,
                                       classe_erreur_mdp=classe_erreur_mdp,
                                       classe_erreur_mdp_confirm=classe_erreur_mdp_confirm,
                                       contenu_erreur_mdp=contenu_erreur_mdp,
                                       value_nom=nom,
                                       value_courriel=courriel,
                                       utilisateur=session.get("utilisateur"))

            if not utilisateur_trouve:
                session["utilisateur"] = bd.ajouter_compte(conn, courriel, mdpHashed, nom)
                return redirect("/", 303)

        return render_template('compte/inscription.jinja', utilisateur=session.get("utilisateur"))
