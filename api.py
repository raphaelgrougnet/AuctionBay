from flask import Blueprint, current_app as app, jsonify, session, request, abort
import time
import bd
import datetime

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


@bp_api.route('/recuperer-mise/<int:id>', methods=['GET'])
def recuperer_mise(id):
    with bd.creer_connexion() as conn:
        mise = bd.get_mise_enchere(conn, id)

    return jsonify(mise)


@bp_api.route('/miser', methods=['POST'])
def miser():
    """Permet de miser"""
    if request.method == "POST":
        user = session.get("utilisateur")
        est_miseur = False
        est_vendeur = False
        id_enchere = request.form.get("id", default="")
        montant = request.form.get("motant_miser", default="")
        date_now = datetime.date.today()

        with bd.creer_connexion() as conn:
            enchere = bd.get_enchere(conn, id_enchere)
            mise = bd.get_mise_enchere(conn, id_enchere)
            active = enchere['date_limite'] >= date_now and enchere['est_supprimee'] == 0
            if not user:
                est_vendeur = False
            elif enchere['fk_vendeur'] == user['id_utilisateur']:
                est_vendeur = True
            else:
                est_vendeur = False
            if not mise:
                est_miseur = False
            else:
                if user:
                    if user['id_utilisateur'] == mise['fk_miseur']:
                        est_miseur = True
                    else:
                        mises_utilisateur = bd.get_mises_encheres_details(conn, mise['fk_enchere'])
                        for mise_utilisateur in mises_utilisateur:
                            if mise_utilisateur['fk_miseur'] == user['id_utilisateur']:
                                est_miseur = True
                                break

            if id_enchere == "" or enchere['est_supprimee'] == 1:
                app.logger.info("L'enchère %s n'existe pas", id_enchere)
                abort(404)
            elif not user:
                app.logger.info("L'utilisateur n'est pas connecté")
                abort(401)
            elif est_vendeur:
                app.logger.info("L'utilisateur est le vendeur")
                abort(400)
            elif not active:
                app.logger.info("L'enchère n'est pas active")
                abort(400)
            else:
                if est_miseur:
                    app.logger.info("Mise à jour de la mise de l'utilisateur %s sur l'enchère %s", user['courriel'],
                                    id_enchere)
                    bd.update_mise_miseur(conn, id_enchere, session["utilisateur"]["id_utilisateur"], montant)

                else:
                    app.logger.info("Ajout de la mise de l'utilisateur %s sur l'enchère %s", user['courriel'],
                                    id_enchere)
                    bd.faire_mise(conn, id_enchere, user['id_utilisateur'], montant)

            return jsonify(bd.get_mise_enchere(conn, id_enchere))
