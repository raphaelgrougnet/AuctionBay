

from flask import redirect, render_template, request, session, Blueprint, abort
import bd
import datetime

bp_encheres = Blueprint('encheres', __name__)


@bp_encheres.route('/<int:identifiant>', methods=['GET', 'POST'])
def detail_enchere(identifiant):
    """Affiche-les détailes d'une enchère"""
    user = session.get("utilisateur")
    est_miseur = False

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

    if request.method == 'POST':
        msg = ""
        id_enchere = request.form.get("id", default="")
        montant = request.form.get("motant_miser", default="")

        if not montant:
            montant = 0

        if id_enchere == "" or enchere['est_supprimee'] == 1:
            abort(404)
        elif not user:
            abort(401)
        elif int(montant) == 0:
            msg = "Vous devez mettre un montant"
        elif int(montant) > 2147483647:
            msg = "Le montant ne peut pas dépasser 2147483647\n"
        elif est_vendeur:
            abort(400)
        elif not active:
            abort(400)
        elif int(montant) <= montant_enchere:
            msg = "Vous devez faire une mise plus grande que celle affichée\n"
        else:
            msg = ""

        if msg == "":
            if est_miseur:
                with bd.creer_connexion() as conn:
                    bd.update_mise_miseur(conn, id_enchere, mise['fk_miseur'], montant)
            else:
                with bd.creer_connexion() as conn:
                    bd.faire_mise(conn, id_enchere, user['id_utilisateur'], montant)

            return redirect(f'/encheres/{id_enchere}', 303)
        else:
            return render_template('details/details.jinja', enchere=enchere, active=active, nom=nom, mise=mise,
                                   est_vendeur=est_vendeur, validation="is-invalid",
                                   message=msg, user=user, valeur_btn=valeur_btn,
                                   route_btn=route_btn, utilisateur=user, montant_min=montant_min)

    return render_template('details/details.jinja', enchere=enchere, active=active, nom=nom,
                           mise=mise, est_vendeur=est_vendeur, user=user, route_btn=route_btn,
                           valeur_btn=valeur_btn, utilisateur=user, montant_min=montant_min)


@bp_encheres.route('/suppression', methods=['POST'])
def suppression():
    """Suppression de l'enchère"""
    id = request.form.get("id", default="")
    user = session.get("utilisateur")

    if not user:
        abort(401)
    if user['est_admin'] == 0:
        abort(403)
    if not id:
        abort(404)

    with bd.creer_connexion() as conn:
        bd.supprimer_enchere(conn, id)

    return render_template('details/suppression.jinja', id=id, utilisateur=user)


@bp_encheres.route('/retablir', methods=['POST'])
def retablir():
    """Rétablir l'enchère supprimée"""
    id = request.form.get("id", default="")
    user = session.get("utilisateur")

    if not user:
        abort(401)
    if user['est_admin'] == 0:
        abort(403)
    if not id:
        abort(404)

    with bd.creer_connexion() as conn:
        bd.retablir_enchere(conn, id)

    return render_template('details/retablir.jinja', id=id, utilisateur=user)
