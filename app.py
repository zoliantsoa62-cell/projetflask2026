from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret"

# Configuration SQLite
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///inscriptions.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

<<<<<<< HEAD
=======
# Création des tables dès le démarrage
with app.app_context():
    db.create_all()

>>>>>>> e12a7061cbe99eeeb184ad3d50b881f1577d4263
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

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        matricule = request.form.get("matricule")
        equipe_nom = request.form.get("equipe")

        if not matricule or not equipe_nom:
            flash("Veuillez entrer un matricule et un nom d'équipe.")
        else:
            inscription = Inscription.query.get(matricule)

            if not inscription:
                # Nouvelle inscription avec 1 billet
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

        # 🚀 Correctif PRG : redirection systématique après POST
        return redirect(url_for("index"))

    # Partie GET uniquement
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
    inscription = Inscription.query.get(matricule)
    if inscription:
        db.session.delete(inscription)
        db.session.commit()
        flash(f"Inscription du matricule {matricule} supprimée.")
    return redirect(url_for("index"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    # ⚠️ Désactiver le reloader automatique pour éviter les doublons
    app.run(debug=False)
