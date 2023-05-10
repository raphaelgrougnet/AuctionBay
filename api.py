from flask import Blueprint, current_app as app, jsonify, session
import time
import bd

bp_api = Blueprint('api', __name__)


@bp_api.route('/afficher-encheres/<int:offset>', methods=['GET'])
def afficher_encheres(offset):
    """Affiche les enchères"""
    with bd.creer_connexion() as conn:
        app.logger.info("Get des enchères depuis api")
        encheres = bd.get_encheres(conn, offset)

    return jsonify(encheres)


@bp_api.route('/afficher-encheres/<int:offset>/<recherche>', methods=['GET'])
def afficher_encheres_recherche(offset, recherche):
    """Affiche les enchères"""
    with bd.creer_connexion() as conn:
        app.logger.info("Get des enchères depuis api")
        encheres = bd.get_encheres_recherche(conn, offset, recherche)

    return jsonify(encheres)


@bp_api.route('/recuperer-utilisateur')
def recuperer_utilisateur():
    """Récupère l'utilisateur"""
    return jsonify(session.get("utilisateur"))


@bp_api.route('/recuperer-suggestions/<search>')
def recuperer_suggestions(search):
    """Récupère les suggestions"""
    with bd.creer_connexion() as conn:
        suggestions = bd.get_suggestions(conn, search)

    return jsonify(suggestions)
