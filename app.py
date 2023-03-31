"""
Démonstration des paramètres obligatoires
"""

from flask import Flask, redirect, render_template, request, abort, session
import hashlib

app = Flask(__name__)

import bd


app = Flask(__name__)

# Enregistre toutes les routes disponibles dans dp_jeu avec le préfixe /jeu


app.secret_key = "fbfd893893844ef4da62c134e0d61a47117d1bc3a33cb78d0a144576d23d2bf3"


@app.route('/')
def index():
    """Affiche l'accueil"""

    with bd.creer_connexion() as conn:
        encheres = bd.get_encheres(conn)

    return render_template('index.jinja', encheres=encheres)
