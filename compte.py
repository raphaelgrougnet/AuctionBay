import datetime
import re

from flask import redirect, render_template, request, session, Blueprint
import hashlib
import re
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

            utilisateur_trouve = None

            classe_erreur_email = ""
            contenu_erreur_email = ""
            classe_erreur_nom = ""
            contenu_erreur_nom = ""
            classe_erreur_mdp = ""
            contenu_erreur_mdp = ""
            classe_erreur_mdp_confirm = ""

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

            if classe_erreur_email != "is-valid" or classe_erreur_nom != "is-valid" or classe_erreur_mdp != "" or classe_erreur_mdp_confirm != "":
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
                session["utilisateur"] = bd.ajouter_compte(conn, courriel, mdpHashed, nom)
                return redirect("/", 303)

        return render_template('compte/inscription.jinja', utilisateur=session.get("utilisateur"))


@bp_compte.route('/mes_encheres')
def mes_encheres():
    """Permet d'afficher les enchères de l'utilisateur"""
    if not session.get("utilisateur"):
        return redirect("/compte/connexion", 303)

    with bd.creer_connexion() as conn:
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
        return redirect("/compte/connexion", 303)

    with bd.creer_connexion() as conn:
        encheres = bd.get_mises_utilisateur(conn, session.get("utilisateur")["id_utilisateur"])
        date_now = datetime.date.today()
        for enchere in encheres:
            enchere["est_invalide"] = enchere["date_limite"] < date_now
            enchere["miseur"] = bd.get_nom_compte(conn, session["utilisateur"]["id_utilisateur"])["nom"]
            enchere["derniere_mise"] = bd.get_mise_enchere(conn, enchere["id_enchere"])
            enchere["derniere_mise"]["dernier_miseur"] = bd.get_nom_compte(conn, enchere["derniere_mise"]["fk_miseur"])[
                "nom"]

        return render_template('compte/mes_mises.jinja', encheres=encheres,
                               utilisateur=session.get("utilisateur"), classe_mises="active")
