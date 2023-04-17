"""
Démonstration des paramètres obligatoires
"""
import bd
from compte import bp_compte
from encheres import bp_encheres
from flask import Flask, render_template, session

app = Flask(__name__)

app.register_blueprint(bp_compte, url_prefix='/compte')
app.register_blueprint(bp_encheres, url_prefix='/encheres')


# Enregistre toutes les routes disponibles dans dp_jeu avec le préfixe /jeu


app.secret_key = "96dd4003f9cdd09ba3ddb7d5fa66b4ce030773766a50484aa9ddd619a0ac71f0"


@app.route('/')
def index():
    """Affiche l'accueil"""

    with bd.creer_connexion() as conn:
        encheres = bd.get_encheres(conn)

    return render_template('index.jinja', encheres=encheres,
                           utilisateur=session.get("utilisateur"),
                           classe_accueil="active")


@app.errorhandler(404)
def page_non_trouvee(error):
    """Affiche la page d'erreur 404"""
    print(error)
    message = "Cette page a peut-être été déplacée ? a été supprimée ? Se cache-t-elle en quarantaine ? " \
              "N'aie jamais existé ?"
    return render_template('erreur.jinja', premier_char_erreur=4, dernier_char_erreur=4, message=message,
                           utilisateur=session.get("utilisateur")), 404


@app.errorhandler(500)
def erreur_interne(error):
    print(error)
    """Affiche la page d'erreur 500"""
    message = "Un problème est survenu lors de la connexion avec la base de données."
    return render_template('erreur.jinja', premier_char_erreur=5, dernier_char_erreur=0, message=message,
                           utilisateur=session.get("utilisateur")), 500


@app.errorhandler(403)
def erreur_compte(error):
    print(error)
    """Affiche la page d'erreur 403"""
    message = "Vous n'avez pas les droits pour accéder à cette page."
    return render_template('erreur.jinja', premier_char_erreur=4, dernier_char_erreur=3, message=message,
                           utilisateur=session.get("utilisateur")), 403


@app.errorhandler(400)
def erreur_requete(error):
    print(error)
    """Affiche la page d'erreur 400"""
    message = "La requête n'a pas pu être traitée."
    return render_template('erreur.jinja', premier_char_erreur=4, dernier_char_erreur=0, message=message,
                           utilisateur=session.get("utilisateur")), 400


@app.errorhandler(401)
def erreur_non_autorise(error):
    print(error)
    """Affiche la page d'erreur 401"""
    message = "Vous n'êtes pas autorisé à accéder à cette page. Veuillez vous connecter."
    return render_template('erreur.jinja', premier_char_erreur=4, dernier_char_erreur=1, message=message,
                           utilisateur=session.get("utilisateur")), 401
