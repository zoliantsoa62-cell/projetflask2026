import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret"

# Identifiants fixes
USERNAME = "admin"
PASSWORD = "pronostic26"

# Configuration PostgreSQL
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "postgresql://zo:pczo@localhost/projet_pg"  # ⚡ Fallback local
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Modèle Inscription
class Inscription(db.Model):
    matricule = db.Column(db.String(50), primary_key=True)
    billets = db.Column(db.Integer, default=0)
    date = db.Column(db.String(50), default=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    equipes = db.relationship("Equipe", backref="inscription", cascade="all, delete-orphan")

# Modèle Equipe
class Equipe(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom = db.Column(db.String(100), nullable=False)
    matricule = db.Column(db.String(50), db.ForeignKey("inscription.matricule"))

# ✅ Création automatique des tables au premier appel
@app.before_first_request
def create_tables():
    db.create_all()

# Routes Login / Logout
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == USERNAME and password == PASSWORD:
            session["user"] = username
            return redirect(url_for("index"))
        else:
            flash("Identifiants invalides")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# Page principale protégée
@app.route("/", methods=["GET", "POST"])
def index():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        matricule = request.form.get("matricule")
        equipe_nom = request.form.get("equipe")

        if not matricule or not equipe_nom:
            flash("Veuillez entrer un matricule et un nom d'équipe.")
        else:
            inscription = Inscription.query.get(matricule)

            if not inscription:
                new_inscription = Inscription(matricule=matricule, billets=1)
                db.session.add(new_inscription)
                db.session.commit()

                new_equipe = Equipe(nom=equipe_nom, matricule=matricule)
                db.session.add(new_equipe)
                db.session.commit()

                flash("Inscription ajoutée avec succès !")
            else:
                if inscription.billets < 2:  # ✅ Limite fixée à 2 billets
                    inscription.billets += 1
                    db.session.commit()

                    new_equipe = Equipe(nom=equipe_nom, matricule=matricule)
                    db.session.add(new_equipe)
                    db.session.commit()

                    flash("Billet supplémentaire ajouté !")
                else:
                    flash("Vous ne pouvez plus acheter d'autre billets (max 2) !")

        return redirect(url_for("index"))

    inscriptions = Inscription.query.all()
    total = sum(i.billets * 1000 for i in inscriptions)

    return render_template(
        "index.html",
        inscriptions=inscriptions,
        total=total,
        total_matricules=len(inscriptions)
    )

@app.route("/delete/<matricule>", methods=["POST"])
def delete(matricule):
    if "user" not in session:
        return redirect(url_for("login"))

    inscription = Inscription.query.get(matricule)
    if inscription:
        db.session.delete(inscription)
        db.session.commit()
        flash(f"Inscription du matricule {matricule} supprimée.")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=False)
