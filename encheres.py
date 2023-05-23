

from flask import redirect, render_template, request, session, Blueprint, abort, current_app as app
import bd
import datetime

bp_encheres = Blueprint('encheres', __name__)


@bp_encheres.route('/<int:identifiant>', methods=['GET', 'POST'])
def detail_enchere(identifiant):
    """Affiche-les détailes d'une enchère"""

    user = session.get("utilisateur")
    est_miseur = False

    with bd.creer_connexion() as conn:
        app.logger.info("Affichage de l'enchère %s", identifiant)
        enchere = bd.get_enchere(conn, identifiant)

        if not enchere:
            app.logger.info("L'enchère %s n'existe pas", identifiant)
            return abort(404)

        if user:
            if user['est_admin'] == 0 and enchere['est_supprimee'] == 1:
                app.logger.info("Accès interdit. L'enchère %s a été supprimée et l'utilisateur %s n'est pas admin",
                                identifiant, user['courriel'])
                abort(403)
        if not user and enchere['est_supprimee'] == 1:
            app.logger.info("Accès impossible. L'enchère %s a été supprimée et l'utilisateur n'est pas connecté", identifiant)
            abort(401)

        mise = bd.get_mise_enchere(conn, identifiant)

        if not mise:
            nom = ""
            montant_enchere = 0
        else:
            miseur = bd.get_nom_compte(conn, mise['fk_miseur'])
            nom = miseur['nom']
            montant_enchere = mise['montant']

        montant_min = montant_enchere + 1

        date_now = datetime.date.today()
        active = enchere['date_limite'] >= date_now and enchere['est_supprimee'] == 0

        if not user:
            est_vendeur = False
        elif enchere['fk_vendeur'] == user['id_utilisateur']:
            est_vendeur = True
        else:
            est_vendeur = False

        if enchere['est_supprimee'] == 0:
            valeur_btn = "Supprimer l'enchère"
            route_btn = "suppression"
        else:
            valeur_btn = "Rétablir l'enchère supprimée"
            route_btn = "retablir"

    app.logger.info("Affichage de l'enchère %s", identifiant)
    return render_template('details/details.jinja', enchere=enchere, active=active, nom=nom,
                           mise=mise, est_vendeur=est_vendeur, user=user, route_btn=route_btn,
                           valeur_btn=valeur_btn, utilisateur=user, montant_min=montant_min)


@bp_encheres.route('/suppression', methods=['POST'])
def suppression():
    """Suppression de l'enchère"""
    id = request.form.get("id", default="")
    user = session.get("utilisateur")

    if not user:
        app.logger.info("Suppression impossible de l'enchère %s. L'utilisateur n'est pas connecté", id)
        abort(401)
    if user['est_admin'] == 0:
        app.logger.info("Suppression impossible de l'enchère %s. L'utilisateur n'est pas administrateur", id)
        abort(403)
    if not id:
        app.logger.info("Suppression impossible de l'enchère %s. L'identifiant est vide", id)
        abort(404)

    with bd.creer_connexion() as conn:
        app.logger.info("Suppression de l'enchère %s", id)
        bd.supprimer_enchere(conn, id)

    app.logger.info("Affichage de la page de suppression de l'enchère %s", id)
    return render_template('details/suppression.jinja', id=id, utilisateur=user)


@bp_encheres.route('/retablir', methods=['POST'])
def retablir():
    """Rétablir l'enchère supprimée"""
    id = request.form.get("id", default="")
    user = session.get("utilisateur")

    if not user:
        app.logger.info("Rétablissement impossible de l'enchère %s. L'utilisateur n'est pas connecté", id)
        abort(401)
    if user['est_admin'] == 0:
        app.logger.info("Rétablissement impossible de l'enchère %s. L'utilisateur n'est pas administrateur", id)
        abort(403)
    if not id:
        app.logger.info("Rétablissement impossible de l'enchère %s. L'identifiant est vide", id)
        abort(404)

    with bd.creer_connexion() as conn:
        app.logger.info("Rétablissement de l'enchère %s", id)
        bd.retablir_enchere(conn, id)

    app.logger.info("Affichage de la page de rétablissement de l'enchère %s", id)
    return render_template('details/retablir.jinja', id=id, utilisateur=user)
