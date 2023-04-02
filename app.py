"""
Démonstration des paramètres obligatoires
"""

from flask import Flask, redirect, render_template, request, abort, session, Blueprint
import hashlib

app = Flask(__name__)

import bd
from compte import bp_compte


app.register_blueprint(bp_compte, url_prefix='/compte')

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


