import os

from flask import Flask, render_template, request, redirect, url_for
from data.database import Database
from models.user import User
from models.organization import Organization
from models.study import Study
from models.enrollment import Enrollment
from models.profiles import Profiles

app = Flask(__name__)

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
    return render_template("home.html")

"""                                                     ### Ervaringsdeskundige ###         """
@app.route("/dashboard-ev")
def dashboard_ev():
    return render_template("dashboard-ev.html")

@app.route("/ev-aanvragen")
def ev_aanvragen():
    study = studies.get_study()
    return render_template("/ev-aanvragen.html", study=study)

@app.route("/ev-profiel")
def ev_profiel():
    return render_template("/ev-profiel.html")


"""                                                     ### Organisaties ###                """
@app.route("/dashboard-org")
def dashboard_org():
    return render_template("dashboard-org.html")

@app.route("/org-aanvragen")
def org_aanvragen():
    forms = organizations.get_forms()
    return render_template("/org-aanvragen.html", forms=forms)

@app.route("/org-profiel")
def org_profiel():
    return render_template("/org-profiel.html")

@app.route("/org-aanvragen/<int:form_id>", methods=["GET", "POST"])
def org_aanvraag_edit(form_id):
    if request.method == "POST":
        title = request.form["title"]
        status = request.form["status"]
        description = request.form["description"]
        available = 1 if "available" in request.form else 0

        organizations.edit_form(
            form_id, title, status, description, available,
        )

        return redirect(url_for("org_aanvragen"))

    form = organizations.get_single_form(form_id)
    return render_template("/org-aanvraag-edit.html", form=form)

@app.route("/org-aanvragen/nieuw", methods=["GET", "POST"])
def org_aanvraag_nieuw():
    if request.method == "POST":
        title = request.form["title"]
        status = request.form["status"]
        description = request.form["description"]
        available = 1 if "available" in request.form else 0

        #tijdelijke hardcoded organisatie ivm latere sessies en inloggen etc
        organization_id = 1

        organizations.create_form(title, status, description, available, organization_id)
        return redirect(url_for("org_aanvragen"))
    return render_template("/org-nieuwe-aanvraag.html")



"""                                                     ### Beheerder ###                     """
@app.route("/dashboard-bhd")
def dashboard_bhd():
    return render_template("/dashboard-bhd.html")

@app.route("/bhd-org-detail")
def bhd_org_detail():
    organization = organizations.get_organization()
    return render_template("/bhd-org-detail.html", organization=organization)

@app.route("/bhd-ev-detail")
def bhd_ev_detail():
    profile = profiles.get_profile()
    return render_template("/bhd-ev-detail.html", profile=profile)




if __name__ == "__main__":
    app.run(debug=True)
