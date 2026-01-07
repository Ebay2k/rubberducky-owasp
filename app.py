import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_session import Session
from data.database import Database
from models.user import User
from models.organization import Organization
from models.study import Study
from models.enrollment import Enrollment
from models.profiles import Profiles

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = "super secret key"

Session(app)

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "data", "data/app.db")

_db = Database(DB_PATH)
users = User(DB_PATH)
organizations = Organization(DB_PATH)
studies = Study(DB_PATH)
enrollments = Enrollment(DB_PATH)
profiles = Profiles(DB_PATH)

"""                                                     ### HOME PAGE ###                   """
@app.route("/")
def index():
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    return render_template("home.html")

"""                                                     ### LOGIN PAGE ###                   """
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = users.get_user_by_email(email)

        if user is None:
            return "Onbekende gebruiker", 403

        if user["password"] != password:
            return "Onjuiste wachtwoord", 403

        session.clear()
        session["user_id"] = user["id"]
        session["role"] = user["role"]

        if user["organization_id"] is not None:
            session["organization_id"] = user["organization_id"]

        """    vanaf hier gaat het om de rollen     """
        if user["role"] == "admin":
            return redirect(url_for("dashboard_bhd"))

        elif user["role"] == "expert":
            return redirect(url_for("dashboard_ev"))

        elif user["role"] == "organization":
            return redirect(url_for("dashboard_org"))

    return render_template("login.html")

"""                                                     ### Ervaringsdeskundige ###         """
@app.route("/dashboard-ev")
def dashboard_ev():
    if session.get("role") != "expert":
        return "Geen Toegang", 403

    return render_template("dashboard-ev.html")

@app.route("/ev-aanvragen")
def ev_aanvragen():
    if session.get("role") != "expert":
        return "Geen Toegang", 403

    user_id = session.get('user_id')
    
    db = Database('data/app.db')
    with db.connect() as con:
        cur = con.cursor()
        
        # Haal het profiel van de gebruiker op
        cur.execute('SELECT id FROM profiles WHERE user_id = ?', (user_id,))
        profile = cur.fetchone()
        
        if not profile:
            return "Profiel niet gevonden", 404
        
        profile_id = profile['id']
        
        # Haal alle goedgekeurde EN nieuwe studies op
        cur.execute('''
            SELECT 
                s.*,
                o.name as organization_name
            FROM studies s
            JOIN organizations o ON s.organization_id = o.id
            WHERE s.status IN ('goedgekeurd', 'nieuw') AND s.available = 1
            ORDER BY s.start_date DESC
        ''')
        studies = cur.fetchall()
        
        # Verrijk met extra informatie
        studies_data = []
        for study in studies:
            study_dict = dict(study)
            
            # Haal disabilities op voor deze study
            cur.execute('''
                SELECT d.name
                FROM study_disabilities sd
                JOIN disabilities d ON sd.disability_id = d.id
                WHERE sd.study_id = ?
            ''', (study['id'],))
            disabilities = [row['name'] for row in cur.fetchall()]
            study_dict['disabilities'] = disabilities
            
            studies_data.append(study_dict)
    
    return render_template("ev-aanvragen.html", studies=studies_data)


@app.route("/ev-aanvragen/<int:study_id>")
def ev_aanvraag_detail(study_id):
    if session.get("role") != "expert":
        return "Geen Toegang", 403

    user_id = session.get('user_id')
    
    db = Database('data/app.db')
    with db.connect() as con:
        cur = con.cursor()
        
        # Haal het profiel van de gebruiker op
        cur.execute('SELECT id FROM profiles WHERE user_id = ?', (user_id,))
        profile = cur.fetchone()
        
        if not profile:
            return "Profiel niet gevonden", 404
        
        profile_id = profile['id']
        
        # Haal de studie op
        cur.execute('''
            SELECT 
                s.*,
                o.name as organization_name
            FROM studies s
            JOIN organizations o ON s.organization_id = o.id
            WHERE s.id = ?
        ''', (study_id,))
        study = cur.fetchone()
        
        if not study:
            return "Onderzoek niet gevonden", 404
        
        study_dict = dict(study)
        
        # Haal disabilities op
        cur.execute('''
            SELECT d.name
            FROM study_disabilities sd
            JOIN disabilities d ON sd.disability_id = d.id
            WHERE sd.study_id = ?
        ''', (study_id,))
        disabilities = [row['name'] for row in cur.fetchall()]
        study_dict['disabilities'] = disabilities
        
        # Check of de gebruiker al is ingeschreven
        cur.execute('''
            SELECT id FROM enrollments
            WHERE study_id = ? AND profile_id = ?
        ''', (study_id, profile_id))
        study_dict['is_enrolled'] = cur.fetchone() is not None
    
    return render_template("ev-aanvraag-detail.html", study=study_dict)


# Route om in te schrijven op een onderzoek
@app.route('/ev-aanvragen/<int:study_id>/enroll', methods=['POST'])
def enroll_study(study_id):
    if session.get("role") != "expert":
        return "Geen Toegang", 403
    
    user_id = session.get('user_id')
    
    db = Database('data/app.db')
    with db.connect() as con:
        cur = con.cursor()
        
        # Haal het profiel van de gebruiker op
        cur.execute('SELECT id FROM profiles WHERE user_id = ?', (user_id,))
        profile = cur.fetchone()
        
        if not profile:
            return "Profiel niet gevonden", 404
        
        profile_id = profile['id']
        
        try:
            # Maak de inschrijving aan
            cur.execute('''
                INSERT INTO enrollments (study_id, profile_id, status)
                VALUES (?, ?, 'nieuw')
            ''', (study_id, profile_id))
            con.commit()
            
            flash('Je bent succesvol ingeschreven voor het onderzoek!', 'success')
        except sqlite3.IntegrityError:
            flash('Je bent al ingeschreven voor dit onderzoek.', 'warning')
    
    return redirect(url_for('ev_aanvraag_detail', study_id=study_id))

@app.route("/ev-profiel")
def ev_profiel():
    if session.get("role") != "expert":
        return "Geen Toegang", 403

    return render_template("/ev-profiel.html")


"""                                                     ### Organisaties ###                """
@app.route("/dashboard-org")
def dashboard_org():
    if session.get("role") != "organization":
        return "Geen Toegang", 403

    return render_template("dashboard-org.html")

@app.route("/org-aanvragen")
def org_aanvragen():
    if session.get("role") != "organization":
        return "Geen Toegang", 403

    organization_id = session.get("organization_id")

    forms = organizations.get_form_by_org(organization_id=organization_id)
    return render_template("/org-aanvragen.html", forms=forms)

@app.route("/org-profiel", methods=["GET", "POST"])
def org_profiel():
    if session.get("role") != "organization":
        return "Geen Toegang", 403

    organization_id = session.get("organization_id")

    if request.method == "POST":
        email = request.form.get("email")
        phone = request.form.get("phone")
        description = request.form.get("description")
        type = request.form.get("type")
        website = request.form.get("website")
        contact_person = request.form.get("contact_person")

        organizations.update_organization(organization_id, type, website, description, contact_person, email, phone)
        return redirect(url_for("org_profiel"))

    organization = organizations.get_organization_by_id(organization_id)
    return render_template("/org-profiel.html", organization=organization)

@app.route("/org-aanvragen/<int:form_id>", methods=["GET", "POST"])
def org_aanvraag_edit(form_id):
    organization_id = session.get("organization_id")

    if request.method == "POST":
        title = request.form["title"]
        status = request.form["status"]
        description = request.form["description"]
        available = 1 if "available" in request.form else 0

        organizations.edit_form(
            form_id, organization_id, title, status, description, available)

        return redirect(url_for("org_aanvragen"))

    form = organizations.get_single_form(form_id, organization_id)

    if not form:
        return "Geen toegang om dit onderzoek te wijzigen", 403

    return render_template("/org-aanvraag-edit.html", form=form)

@app.route("/org-aanvragen/nieuw", methods=["GET", "POST"])
def org_aanvraag_nieuw():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        available = 1 if "available" in request.form else 0

        organization_id = session.get("organization_id")

        organizations.create_form(title, description, available, organization_id)
        return redirect(url_for("org_aanvragen"))
    return render_template("/org-nieuwe-aanvraag.html")



"""                                                     ### Beheerder ###                     """
@app.route("/dashboard-bhd")
def dashboard_bhd():
    if session.get("role") != "admin":
        return "Geen Toegang", 403
    return render_template("/dashboard-bhd.html")

@app.route("/bhd-org-detail")
def bhd_org_detail():
    if session.get("role") != "admin":
        return "Geen Toegang", 403
    organization = organizations.get_organization()
    return render_template("/bhd-org-detail.html", organization=organization)

@app.route("/bhd-ev-detail")
def bhd_ev_detail():
    if session.get("role") != "admin":
        return "Geen Toegang", 403
    profile = profiles.get_profile()
    return render_template("/bhd-ev-detail.html", profile=profile)

@app.route("/bhd-goedkeuringen")
def bhd_goedkeuringen():
    if session.get("role") != "admin":
        return "Geen Toegang", 403
    return render_template("/bhd-goedkeuringen.html")


if __name__ == "__main__":
    app.run(debug=True)
