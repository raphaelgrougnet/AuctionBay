"""
Connexion à la BD
"""

import types
import contextlib
import mysql.connector
import hashlib


@contextlib.contextmanager
def creer_connexion():
    """Pour créer une connexion à la BD"""
    conn = mysql.connector.connect(
        user="garneau",
        password="qwerty123",
        host="127.0.0.1",
        database="tp2_enchere",
        raise_on_warnings=True
    )

    # Pour ajouter la méthode get_curseur() à l'objet connexion
    conn.get_curseur = types.MethodType(get_curseur, conn)

    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    else:
        conn.commit()
    finally:
        conn.close()


@contextlib.contextmanager
def get_curseur(self):
    """Permet d'avoir les enregistrements sous forme de dictionnaires"""
    curseur = self.cursor(dictionary=True)
    try:
        yield curseur
    finally:
        curseur.close()


def get_encheres(conn):
    """Obtient toutes les enchères"""
    with conn.get_curseur() as curseur:
        curseur.execute("SELECT id_enchere, titre, date_limite, est_supprimee FROM enchere order by date_limite desc")
        return curseur.fetchall()


def get_utilisateurs(conn):
    """Obtient tous les utilisateurs"""
    with conn.get_curseur() as curseur:
        curseur.execute("SELECT id_utilisateur, courriel, nom, est_admin FROM utilisateur")
        return curseur.fetchall()


def get_compte(conn, courriel, mdp):
    """Obtient le compte correspondant au courriel"""
    with conn.get_curseur() as curseur:
        curseur.execute("SELECT id_utilisateur, courriel, nom, est_admin "
                        "FROM utilisateur WHERE courriel = %(courriel)s AND mdp = %(mdp)s",
                        {"courriel": courriel, "mdp": mdp})
        return curseur.fetchone()


def get_nom_compte(conn, id_utilisateur):
    """Obtient le compte correspondant au courriel"""
    with conn.get_curseur() as curseur:
        curseur.execute("SELECT nom FROM utilisateur WHERE id_utilisateur = %(id_utilisateur)s",
                        {"id_utilisateur": id_utilisateur})
        return curseur.fetchone()


def ajouter_compte(conn, courriel, mdp, nom):
    """Ajoute un compte"""
    with conn.get_curseur() as curseur:
        curseur.execute("INSERT INTO utilisateur (courriel, mdp, nom, est_admin) "
                        "VALUES (%(courriel)s, %(mdp)s, %(nom)s, 0)",
                        {"courriel": courriel, "mdp": mdp, "nom": nom})
        return get_compte(conn, courriel, mdp)


def get_encheres_utilisateur(conn, id_utilisateur):
    """Obtient les enchères d'un utilisateur"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            "SELECT id_enchere, titre, date_limite, est_supprimee FROM enchere "
            "WHERE fk_vendeur = %(id_utilisateur)s order by date_limite desc",
            {"id_utilisateur": id_utilisateur})
        return curseur.fetchall()


def get_enchere(conn, id_enchere):
    """Obtient une enchère"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            "SELECT id_enchere, titre, date_limite, est_supprimee FROM enchere "
            "WHERE id_enchere = %(id_enchere)s",
            {"id_enchere": id_enchere})
        return curseur.fetchone()


def get_mise_enchere(conn, fk_enchere):
    """Obtient les mises d'une enchère"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            "SELECT fk_miseur, montant, fk_enchere FROM mise "
            "WHERE fk_enchere = %(id_enchere)s order by montant desc limit 1",
            {"id_enchere": fk_enchere})
        return curseur.fetchone()


def get_mises_utilisateur(conn, id_utilisateur):
    """Obtient les mises d'un utilisateur"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            "SELECT e.id_enchere, e.titre, e.description, e.date_limite, e.est_supprimee, e.fk_vendeur, m.montant "
            "FROM `enchere` e "
            "JOIN mise m ON e.id_enchere = m.fk_enchere "
            "JOIN utilisateur u on u.id_utilisateur = m.fk_miseur "
            "WHERE u.id_utilisateur = %(id_utilisateur)s order by date_limite desc",
            {"id_utilisateur": id_utilisateur})
        return curseur.fetchall()
