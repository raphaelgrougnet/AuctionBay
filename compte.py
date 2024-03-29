import datetime
import hashlib
import re

from flask import redirect, render_template, request, session, Blueprint, current_app as app

import bd

bp_compte = Blueprint('compte', __name__)

regex_escape = re.compile("<(.*)>.*?|<(.*) />")
regex_courriel = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")


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
            app.logger.info("Début de la connexion pour le courriel %s", courriel)
            mdpHashed = hacher_mdp(mdp)

            utilisateur_trouve = bd.get_compte(conn, courriel, mdpHashed)
            if utilisateur_trouve:
                session.permanent = True
                session["utilisateur"] = utilisateur_trouve
                app.logger.info("Connexion réussie pour le courriel %s", courriel)
                app.logger.info("Redirection vers la page d'accueil de l'utilisateur %s", courriel)
                return redirect("/", 303)

            if not utilisateur_trouve:
                app.logger.info("Connexion échouée pour le courriel %s", courriel)
                return render_template('compte/connexion.jinja', classe_erreur="is-invalid")
        app.logger.info("Affichage de la page de connexion")
        return render_template('compte/connexion.jinja', utilisateur=session.get("utilisateur"))


@bp_compte.route('/deconnexion')
def deconnexion():
    """Permet de se déconnecter"""
    user = session.get("utilisateur")

    session.pop("utilisateur", None)
    app.logger.info("Déconnexion réussie pour le courriel %s", user['courriel'])
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
            app.logger.info("Début de l'inscription pour le courriel %s", courriel)
            mdpHashed = hacher_mdp(mdp)

            utilisateur_trouve = None

            ""
            contenu_erreur_email = ""
            ""
            contenu_erreur_nom = ""
            classe_erreur_mdp = ""
            contenu_erreur_mdp = ""
            classe_erreur_mdp_confirm = ""
            app.logger.info("Début de la vérification des champs")
            if nom == "":
                classe_erreur_nom = "is-invalid"
                contenu_erreur_nom = "Le nom est obligatoire."
            elif len(nom) > 50 or len(nom) < 3:
                classe_erreur_nom = "is-invalid"
                contenu_erreur_nom = "Le nom doit être entre 3 et 50 caractères."
            elif regex_escape.search(nom):
                classe_erreur_nom = "is-invalid"
                contenu_erreur_nom = "Le nom ne doit pas contenir de caractères spéciaux."
            else:
                classe_erreur_nom = "is-valid"

            if courriel == "":
                classe_erreur_email = "is-invalid"
                contenu_erreur_email = "Le courriel est obligatoire."
            elif len(courriel) > 50:
                classe_erreur_email = "is-invalid"
                contenu_erreur_email = "Le courriel doit être inférieur à 50 caractères."
            elif regex_escape.search(courriel):
                classe_erreur_email = "is-invalid"
                contenu_erreur_email = "Le courriel ne doit pas contenir de caractères spéciaux."
            elif not re.match(regex_courriel, courriel):
                classe_erreur_email = "is-invalid"
                contenu_erreur_email = "Le courriel n'est pas valide."
            elif bd.get_compte(conn, courriel, mdpHashed):
                classe_erreur_email = "is-invalid"
                contenu_erreur_email = "Le courriel est déjà associé à un autre utilisateur."
            else:
                classe_erreur_email = "is-valid"
                utilisateur_trouve = bd.get_compte(conn, courriel, mdpHashed)

            if mdp == "":
                classe_erreur_mdp = "is-invalid"
                contenu_erreur_mdp = "Le mot de passe est obligatoire."
            elif len(mdp) < 4:
                classe_erreur_mdp = "is-invalid"
                contenu_erreur_mdp = "Le mot de passe doit être supérieur à 4 caractères."
            elif regex_escape.search(mdp):
                classe_erreur_mdp = "is-invalid"
                contenu_erreur_mdp = "Le mot de passe ne doit pas contenir de caractères spéciaux."

            if mdp != mdp_confirm:
                classe_erreur_mdp_confirm = "is-invalid"
                classe_erreur_mdp = "is-invalid"
                contenu_erreur_mdp = "Les mots de passe ne correspondent pas."

            if classe_erreur_email != "is-valid" or classe_erreur_nom != "is-valid" or classe_erreur_mdp != "" \
                    or classe_erreur_mdp_confirm != "":
                app.logger.info("Erreur dans les champs")
                return render_template('compte/inscription.jinja',
                                       classe_erreur_email=classe_erreur_email,
                                       contenu_erreur_email=contenu_erreur_email,
                                       classe_erreur_nom=classe_erreur_nom,
                                       contenu_erreur_nom=contenu_erreur_nom,
                                       classe_erreur_mdp=classe_erreur_mdp,
                                       contenu_erreur_mdp=contenu_erreur_mdp,
                                       classe_erreur_mdp_confirm=classe_erreur_mdp_confirm,
                                       value_nom=nom,
                                       value_courriel=courriel,
                                       utilisateur=session.get("utilisateur"))

            if not utilisateur_trouve:
                app.logger.info("Inscription réussie pour le courriel %s", courriel)
                session["utilisateur"] = bd.ajouter_compte(conn, courriel, mdpHashed, nom)
                app.logger.info("Redirection vers la page d'accueil de l'utilisateur %s", courriel)
                return redirect("/", 303)
        app.logger.info("Affichage de la page d'inscription")
        return render_template('compte/inscription.jinja', utilisateur=session.get("utilisateur"))


@bp_compte.route('/mes_encheres')
def mes_encheres():
    """Permet d'afficher les enchères de l'utilisateur"""
    if not session.get("utilisateur"):
        app.logger.info("Redirection vers la page de connexion car l'utilisateur n'est pas connecté")
        return redirect("/compte/connexion", 303)

    with bd.creer_connexion() as conn:
        app.logger.info("Affichage des enchères de l'utilisateur %s", session.get("utilisateur")["courriel"])
        encheres = bd.get_encheres_utilisateur(conn, session.get("utilisateur")["id_utilisateur"])
        date_now = datetime.date.today()
        for enchere in encheres:
            enchere["est_invalide"] = enchere["date_limite"] < date_now
            mise = bd.get_mise_enchere(conn, enchere["id_enchere"])
            if mise:
                enchere["miseur"] = bd.get_nom_compte(conn, mise["fk_miseur"])["nom"]
                enchere["derniere_mise"] = mise["montant"]

        return render_template('compte/mes_encheres.jinja', encheres=encheres,
                               utilisateur=session.get("utilisateur"), classe_encheres="active")


@bp_compte.route('/mes_mises')
def mes_mises():
    """Permet d'afficher les mises de l'utilisateur"""
    if not session.get("utilisateur"):
        app.logger.info("Redirection vers la page de connexion car l'utilisateur n'est pas connecté")
        return redirect("/compte/connexion", 303)

    with bd.creer_connexion() as conn:
        app.logger.info("Affichage des mises de l'utilisateur %s", session.get("utilisateur")["courriel"])
        encheres = bd.get_mises_utilisateur(conn, session.get("utilisateur")["id_utilisateur"])
        date_now = datetime.date.today()
        for enchere in encheres:
            enchere["est_invalide"] = enchere["date_limite"] < date_now
            enchere["miseur"] = bd.get_nom_compte(conn, session["utilisateur"]["id_utilisateur"])["nom"]
            enchere["montant"] = bd.get_mise_utilsateur_details_enchere(conn, session["utilisateur"]["id_utilisateur"], enchere["id_enchere"])["montant"]
            # enchere["derniere_mise"] = bd.get_mise_enchere(conn, enchere["id_enchere"])
            # enchere["derniere_mise"]["dernier_miseur"] = bd.get_nom_compte(conn, enchere["derniere_mise"]["fk_miseur"])[
            #     "nom"]
            miseActuelle = bd.get_mise_enchere(conn, enchere["id_enchere"])
            enchere["derniere_mise"] = miseActuelle["montant"]
            enchere["dernier_miseur"] = bd.get_nom_compte(conn, miseActuelle["fk_miseur"])[
                "nom"]

        return render_template('compte/mes_mises.jinja', encheres=encheres,
                               utilisateur=session.get("utilisateur"), classe_mises="active")
