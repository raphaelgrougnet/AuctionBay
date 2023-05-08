"""
Démonstration des paramètres obligatoires
"""
import os

import dotenv
import bd
from compte import bp_compte
from encheres import bp_encheres
from api import bp_api
from flask import Flask, render_template, session, request

if not os.getenv('BD_UTILISATEUR'):
    dotenv.load_dotenv(".env")

app = Flask(__name__)

app.register_blueprint(bp_compte, url_prefix='/compte')
app.register_blueprint(bp_encheres, url_prefix='/encheres')
app.register_blueprint(bp_api, url_prefix='/api')


# Enregistre toutes les routes disponibles dans dp_jeu avec le préfixe /jeu


app.secret_key = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    """Affiche l'accueil"""

    # with bd.creer_connexion() as conn:
    #     encheres = bd.get_encheres(conn)
    if session.get("utilisateur"):
        app.logger.info("Accueil affiché pour l'utilisateur %s", session.get("utilisateur")["courriel"])
    else:
        app.logger.info("Accueil affiché pour l'utilisateur %s", "anonyme")

    return render_template('index.jinja',
                           utilisateur=session.get("utilisateur"),
                           classe_accueil="active")


@app.errorhandler(404)
def page_non_trouvee(error):
    """Affiche la page d'erreur 404"""
    print(error)
    message = "Cette page a peut-être été déplacée ? a été supprimée ? Se cache-t-elle en quarantaine ? " \
              "N'aie jamais existé ?"
    app.logger.warning("Page non trouvée : %s", request.path)
    return render_template('erreur.jinja', premier_char_erreur=4, dernier_char_erreur=4, message=message,
                           utilisateur=session.get("utilisateur")), 404


@app.errorhandler(500)
def erreur_interne(error):
    print(error)
    """Affiche la page d'erreur 500"""
    message = "Un problème est survenu lors de la connexion avec la base de données."
    app.logger.error(f"Erreur interne pour l'utilisateur {session.get('utilisateur') or 'anonyme'} : {error}")
    return render_template('erreur.jinja', premier_char_erreur=5, dernier_char_erreur=0, message=message,
                           utilisateur=session.get("utilisateur")), 500


@app.errorhandler(403)
def erreur_compte(error):
    print(error)
    """Affiche la page d'erreur 403"""
    message = "Vous n'avez pas les droits pour accéder à cette page."
    app.logger.warning("Accès interdit pour l'utilisateur %s", session.get("utilisateur") or "anonyme")
    return render_template('erreur.jinja', premier_char_erreur=4, dernier_char_erreur=3, message=message,
                           utilisateur=session.get("utilisateur")), 403


@app.errorhandler(400)
def erreur_requete(error):
    print(error)
    """Affiche la page d'erreur 400"""
    message = "La requête n'a pas pu être traitée."
    app.logger.warning("Requête invalide pour l'utilisateur %s", session.get("utilisateur") or "anonyme")
    return render_template('erreur.jinja', premier_char_erreur=4, dernier_char_erreur=0, message=message,
                           utilisateur=session.get("utilisateur")), 400


@app.errorhandler(401)
def erreur_non_autorise(error):
    print(error)
    """Affiche la page d'erreur 401"""
    message = "Vous n'êtes pas autorisé à accéder à cette page. Veuillez vous connecter."
    app.logger.warning("Accès non autorisé pour l'utilisateur %s", session.get("utilisateur") or "anonyme")
    return render_template('erreur.jinja', premier_char_erreur=4, dernier_char_erreur=1, message=message,
                           utilisateur=session.get("utilisateur")), 401
