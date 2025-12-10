import os

from flask import Flask, render_template
from data.database import Database
from models.user import User
from models.organization import Organization
from models.study import Study
from models.enrollment import Enrollment

app = Flask(__name__)

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "data", "data/app.db")

_db = Database(DB_PATH)
users = User(DB_PATH)
organizations = Organization(DB_PATH)
studies = Study(DB_PATH)
enrollments = Enrollment(DB_PATH)

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/dashboard-ev.html")
def dashboard_ev():
    return render_template("dashboard-ev.html")


@app.route("/dashboard-org.html")
def dashboard_org():
    return render_template("dashboard-org.html")

@app.route("/dashboard-bhd.html")
def dashboard_bhd():
    return render_template("/dashboard-bhd.html")

@app.route("/ev-aanvragen.html")
def ev_aanvragen():
    study = studies.get_study()
    return render_template("/ev-aanvragen.html", study=study)

@app.route("/org-aanvragen.html")
def org_aanvragen():
    return render_template("/org-aanvragen.html")

@app.route("/org-profiel.html")
def org_profiel():
    return render_template("/org-profiel.html")

@app.route("/ev-profiel.html")
def ev_profiel():
    return render_template("/ev-profiel.html")

@app.route("/bhd-org-detail.html")
def bhd_org_detail():
    return render_template("/bhd-org-detail.html")


if __name__ == "__main__":
    app.run(debug=True)
