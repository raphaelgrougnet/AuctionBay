

from flask import redirect, render_template, request, session, Blueprint, abort
import bd
import datetime

bp_encheres = Blueprint('encheres', __name__)


@bp_encheres.route('/<int:identifiant>', methods=['GET', 'POST'])
def detail_enchere(identifiant):
    """Affiche-les détailes d'une enchère"""
    user = None
    if "utilisateur" in session:
        user = session.get("utilisateur")
    est_vendeur = False
    est_miseur = False
    nom = ""
    montant_enchere = 0

    with bd.creer_connexion() as conn:
        enchere = bd.get_enchere(conn, identifiant)

        if not enchere:
            return abort(404)

        if user:
            if user['est_admin'] == 0 and enchere['est_supprimee'] == 1:
                abort(403)
        if not user and enchere['est_supprimee'] == 1:
            abort(403)

        mise = bd.get_mise_enchere(conn, identifiant)

        if not mise:
            nom = ""
            montant_enchere = 0
        else:
            miseur = bd.get_nom_compte(conn, mise['fk_miseur'])
            nom = miseur['nom']
            montant_enchere = mise['montant']
            if user:
                if user['id_utilisateur'] == mise['fk_miseur']:
                    est_miseur = True

        date_now = datetime.date.today()
        active = enchere['date_limite'] >= date_now and enchere['est_supprimee'] == 0

        if not user:
            est_vendeur = False
        elif enchere['fk_vendeur'] == user['id_utilisateur']:
            est_vendeur = True
        else:
            est_vendeur = False

    if request.method == 'POST':
        msg = ""
        id_enchere = request.form.get("id", default="")
        montant = request.form.get("motant_miser", default=0)
        validation = ""

        if id_enchere == "" or enchere['est_supprimee'] == 1:
            abort(404)
        elif not user:
            abort(401)
        elif est_vendeur:
            abort(400)
        elif not active:
            abort(400)
        elif est_miseur:
            msg = "Vous êtes déjà le premier sur cette enchère\n"
        elif int(montant) < montant_enchere:
            msg = "Vous devez faire une mise plus grande que celle affichée\n"
        else:
            msg = ""

        if msg == "":
            validation = "is-valid"
            with bd.creer_connexion() as conn:
                bd.faire_mise(conn, id_enchere, user['id_utilisateur'], montant)

            return redirect(f'/encheres/{id_enchere}', 303)
        else:
            return render_template('detailes.jinja', enchere=enchere, active=active, nom=nom, mise=mise,
                                   est_vendeur=est_vendeur, validation="is-invalid", message=msg, user=user)

    return render_template('detailes.jinja', enchere=enchere, active=active, nom=nom,
                           mise=mise, est_vendeur=est_vendeur, user=user)


