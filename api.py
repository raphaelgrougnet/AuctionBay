from flask import Blueprint, current_app as app, jsonify

import bd

bp_api = Blueprint('api', __name__)


@bp_api.route('/api/afficher-encheres/<int:offset>', methods=['GET'])
def afficher_encheres(offset):
    """Affiche les enchères"""
    with bd.creer_connexion() as conn:
        app.logger.info("Get des enchères depuis api")
        encheres = bd.get_encheres(conn, offset)
    return jsonify(encheres)
