

from flask import redirect, render_template, request, session, Blueprint, abort
import bd
import datetime

bp_encheres = Blueprint('encheres', __name__)


@bp_encheres.route('/<int:identifiant>', methods=['GET', 'POST'])
def detail_enchere(identifiant):
    """Affiche-les détailes d'une enchère"""
    user = session.get("utilisateur")

    with bd.creer_connexion() as conn:
        enchere = bd.get_enchere(conn, identifiant)

        if not enchere:
            return abort(404)

        mise = bd.get_mise_enchere(conn, identifiant)

        date_now = datetime.date.today()
        active = enchere['date_limite'] >= date_now
        est_vendeur = enchere['fk_vendeur'] == user['id_utilisateur']

    if request.method == 'post':
        msg = ""
        id_enchere = request.form.get("id", default="")
        montant = request.form.get("motant_miser", default=0)

        if user is None:
            msg += "Vous devez vous connecter pour miser\n"


    return render_template('detailes.jinja', enchere=enchere, active=active, mise=mise, est_vendeur=est_vendeur)


