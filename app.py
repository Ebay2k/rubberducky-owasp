import os
from flask import Flask, render_template
from data.database import Database
from models.user import User
from models.organization import Organization
from models.study import Study
from models.enrollment import Enrollment

app = Flask(__name__)

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "data", "app.db")

_db = Database(DB_PATH)
users = User(DB_PATH)
organizations = Organization(DB_PATH)
studies = Study(DB_PATH)
enrollments = Enrollment(DB_PATH)
@app.route("/")
def index():
    counts = {
        "experts": users.count_all()[0],
        "organizations": organizations.count_all()[0],
        "studies": studies.count_all()[0],
        "enrollments": enrollments.count_all()[0],
    }
    return render_template("home.html", counts=counts)

@app.route("/dashboard-ev.html")
def dashboard_ev():
    return render_template("dashboard-ev.html")


@app.route("/dashboard-org.html")
def dashboard_org():
    return render_template("dashboard-org.html")

@app.route("/dashboard-bhd.html")
def dashboard_bhd():
    return render_template("/dashboard-bhd.html")

@app.route("/org-aanvragen.html")
def org_aanvragen():
    return render_template("/org-aanvragen.html")


if __name__ == "__main__":
    app.run(debug=True)
