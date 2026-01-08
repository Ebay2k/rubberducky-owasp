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
            flash("Onbekende gebruiker", "error")
            return render_template("login.html")

        if user["password"] != password:
            flash("Onjuist wachtwoord", "error")
            return render_template("login.html")

        if user["status"] == "nieuw":
            flash(
                "Je account wordt nog beoordeeld door een beheerder. Je ontvangt bericht zodra je account is goedgekeurd.",
                "warning")
            return render_template("login.html")

        session.clear()
        session["user_id"] = user["id"]
        session["role"] = user["role"]

        if user["organization_id"] is not None:
            session["organization_id"] = user["organization_id"]

        if user["role"] == "admin":
            return redirect(url_for("dashboard_bhd"))

        elif user["role"] == "expert":
            return redirect(url_for("dashboard_ev"))

        elif user["role"] == "organization":
            return redirect(url_for("dashboard_org"))

    return render_template("login.html")


"""                                                     ### LOGOUT ###                        """
@app.route("/logout")
def logout():
    session.clear()
    flash("Je bent succesvol uitgelogd", "success")
    return redirect(url_for("login"))

"""                                                     ### REGISTRATIE ###         """

@app.route("/registreer", methods=["GET", "POST"])
def registreer():
    if request.method == "POST":
        step = request.form.get("step", "1")

        if step == "1":
            # Persoonsgegeven opslan
            session["registratie"] = {
                "first_name": request.form.get("first_name"),
                "last_name": request.form.get("last_name"),
                "email": request.form.get("email"),
                "password": request.form.get("password"),
                "postcode": request.form.get("postcode"),
                "gender": request.form.get("gender"),
                "phone": request.form.get("phone"),
                "birth_date": request.form.get("birth_date"),
            }
            return redirect(url_for("registreer_stap2"))

    return render_template("registreer-stap1.html")


@app.route("/registreer/stap2", methods=["GET", "POST"])
def registreer_stap2():
    if "registratie" not in session:
        return redirect(url_for("registreer"))

    if request.method == "POST":
        session["registratie"]["disabilities"] = request.form.getlist("disabilities")
        session["registratie"]["assistive_tools"] = request.form.get("assistive_tools")
        session["registratie"]["intro"] = request.form.get("intro")
        session["registratie"]["contact_preference"] = request.form.get("contact_preference")
        session["registratie"]["preferred_study_type"] = request.form.get("preferred_study_type")
        session["registratie"]["availability"] = request.form.get("availability")
        session["registratie"]["has_guardian"] = 1 if request.form.get("has_guardian") else 0

        if session["registratie"]["has_guardian"]:
            return redirect(url_for("registreer_stap3"))
        else:
            return redirect(url_for("registreer_stap4"))
    # Beperkingen ophalen
    db = Database('data/app.db')
    with db.connect() as con:
        cur = con.cursor()
        cur.execute('SELECT * FROM disabilities ORDER BY category, name')
        disabilities = cur.fetchall()

    return render_template("registreer-stap2.html", disabilities=disabilities)


@app.route("/registreer/stap3", methods=["GET", "POST"])
def registreer_stap3():
    if "registratie" not in session:
        return redirect(url_for("registreer"))

    if request.method == "POST":
        # Toezichthouder
        session["registratie"]["guardian_name"] = request.form.get("guardian_name")
        session["registratie"]["guardian_email"] = request.form.get("guardian_email")
        session["registratie"]["guardian_phone"] = request.form.get("guardian_phone")
        return redirect(url_for("registreer_stap4"))

    return render_template("registreer-stap3.html")


@app.route("/registreer/stap4", methods=["GET", "POST"])
def registreer_stap4():
    if "registratie" not in session:
        return redirect(url_for("registreer"))

    if request.method == "POST":
        agreed_terms = request.form.get("agreed_terms")

        if not agreed_terms:
            flash("Je moet akkoord gaan met de voorwaarden", "error")
            return render_template("registreer-stap4.html", data=session["registratie"])

        # slaat alles op
        data = session["registratie"]

        db = Database('data/app.db')
        with db.connect() as con:
            cur = con.cursor()

            # user create
            cur.execute('''
                INSERT INTO users (email, password, role, status)
                VALUES (?, ?, 'expert', 'nieuw')
            ''', (data["email"], data["password"]))

            user_id = cur.lastrowid

            # profiel
            cur.execute('''
                INSERT INTO profiles
                (user_id, first_name, last_name, postcode, gender, phone, birth_date,
                 assistive_tools, intro, agreed_terms, has_guardian,
                 guardian_name, guardian_email, guardian_phone,
                 contact_preference, preferred_study_type, availability)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, data["first_name"], data["last_name"],
                data["postcode"], data["gender"], data["phone"], data["birth_date"],
                data.get("assistive_tools"), data.get("intro"),
                data.get("has_guardian", 0),
                data.get("guardian_name"), data.get("guardian_email"), data.get("guardian_phone"),
                data.get("contact_preference"), data.get("preferred_study_type"), data.get("availability")
            ))

            profile_id = cur.lastrowid

            # beperkingen
            for disability_id in data.get("disabilities", []):
                cur.execute('''
                    INSERT INTO profile_disabilities (profile_id, disability_id)
                    VALUES (?, ?)
                ''', (profile_id, disability_id))

            con.commit()

        # verwijderd registratie uit sessie
        session.pop("registratie", None)

        flash("Registratie voltooid! Je account wordt beoordeeld door een beheerder.", "success")
        return redirect(url_for("login"))

    return render_template("registreer-stap4.html", data=session.get("registratie", {}))

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

        cur.execute('SELECT id FROM profiles WHERE user_id = ?', (user_id,))
        profile = cur.fetchone()
        
        if not profile:
            return "Profiel niet gevonden", 404
        
        profile_id = profile['id']

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

        studies_data = []
        for study in studies:
            study_dict = dict(study)

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

        cur.execute('SELECT id FROM profiles WHERE user_id = ?', (user_id,))
        profile = cur.fetchone()
        
        if not profile:
            return "Profiel niet gevonden", 404
        
        profile_id = profile['id']

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

        cur.execute('''
            SELECT d.name
            FROM study_disabilities sd
            JOIN disabilities d ON sd.disability_id = d.id
            WHERE sd.study_id = ?
        ''', (study_id,))
        disabilities = [row['name'] for row in cur.fetchall()]
        study_dict['disabilities'] = disabilities

        cur.execute('''
            SELECT id FROM enrollments
            WHERE study_id = ? AND profile_id = ?
        ''', (study_id, profile_id))
        study_dict['is_enrolled'] = cur.fetchone() is not None
    
    return render_template("ev-aanvraag-detail.html", study=study_dict)


# route om in te schrijven op een onderzoek
@app.route('/ev-aanvragen/<int:study_id>/enroll', methods=['POST'])
def enroll_study(study_id):
    if session.get("role") != "expert":
        return "Geen Toegang", 403
    
    user_id = session.get('user_id')
    
    db = Database('data/app.db')
    with db.connect() as con:
        cur = con.cursor()

        cur.execute('SELECT id FROM profiles WHERE user_id = ?', (user_id,))
        profile = cur.fetchone()
        
        if not profile:
            return "Profiel niet gevonden", 404
        
        profile_id = profile['id']
        
        try:
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

    user_id = session.get('user_id')

    db = Database('data/app.db')
    with db.connect() as con:
        cur = con.cursor()

        cur.execute('''
            SELECT 
                p.*,
                u.email
            FROM profiles p
            JOIN users u ON u.id = p.user_id
            WHERE p.user_id = ?
        ''', (user_id,))

        profile = cur.fetchone()

        if not profile:
            return "Profiel niet gevonden", 404

        profile_dict = dict(profile)

        cur.execute('''
            SELECT d.name, d.category
            FROM profile_disabilities pd
            JOIN disabilities d ON pd.disability_id = d.id
            WHERE pd.profile_id = ?
        ''', (profile['id'],))

        disabilities = [{'name': row['name'], 'category': row['category']} for row in cur.fetchall()]
        profile_dict['disabilities'] = disabilities

    return render_template("ev-profiel.html", profile=profile_dict)


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

@app.route("/org-aanvragen/<int:study_id>/inschrijvingen")
def org_aanvraag_inschrijvingen(study_id):
    if session.get("role") != "organization":
        return "Geen Toegang", 403

    organization_id = session.get("organization_id")

    study = organizations.get_single_form(study_id, organization_id)
    if not study:
        return "Geen toegang tot dit onderzoek", 403

    enrollments = organizations.get_enrollments_for_study(study_id)

    return render_template(
        "org-aanvragen-inschrijvingen.html",
        study=study, enrollments=enrollments)

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

@app.route("/bhd-goedkeuringen", methods=["GET", "POST"])
def bhd_goedkeuringen():
    if session.get("role") != "admin":
        return "Geen Toegang", 403

    if request.method == "POST":
        status = request.form.get("status")
        id = request.form.get("id")

        users.update_users(status, id)
        return redirect(url_for("bhd_goedkeuringen"))

    user_ev = users.get_user_ervaringsdeskundige()
    return render_template("/bhd-goedkeuringen.html", user_ev=user_ev)

@app.route("/bhd-org-aanmaken", methods=["GET", "POST"])
def org_registreer():
    if request.method == "POST":
            session["org_registratie"] = {
                "name": request.form.get("name"),
                "type": request.form.get("type"),
                "website": request.form.get("website"),
                "description": request.form.get("description"),
                "contact_person": request.form.get("contact_person"),
                "email": request.form.get("email"),
                "phone": request.form.get("phone"),
                "details": request.form.get("details"),
            }
            return redirect(url_for("org_registreer_2"))

    return render_template("bhd-org-aanmaken.html")

@app.route("/bhd-org-aanmaken-2", methods=["GET", "POST"])
def org_registreer_2():
    org_data = session.get("org_registratie")

    if not org_data:
        return redirect(url_for("org_registreer"))

    if request.method == "POST":
        db = Database('data/app.db')
        with db.connect() as con:
            cur = con.cursor()
            cur.execute(
                '''
                INSERT INTO organizations
                (name, type, website, description, contact_person, email, phone, details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    org_data["name"],
                    org_data["type"],
                    org_data["website"],
                    org_data["description"],
                    org_data["contact_person"],
                    org_data["email"],
                    org_data["phone"],
                    org_data["details"],
                )
            )
            con.commit()

        session.pop("org_registratie", None)
        flash("Registratie voltooid!", "success")
        return redirect(url_for("dashboard_bhd"))

    return render_template("bhd-org-aanmaken-2.html", org_data=org_data)

if __name__ == "__main__":
    app.run(debug=True)
