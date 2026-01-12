from data.database import Database

class Organization:
    def __init__(self, db_path: str):
        self.db = Database(db_path)

    def count_all(self):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT COUNT() FROM organizations")
            con.commit()
            return cur.fetchone()

    def get_organization(self):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM organizations")
            con.commit()
            return cur.fetchall()

    def get_organization_by_id(self, organization_id):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM organizations WHERE id = ?", (organization_id,))
            return cur.fetchone()

    def update_organization(self, organization_id, type, website, description, contact_person, email, phone):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("""
            UPDATE organizations SET
                 type = ?, 
                 website = ?, 
                 description = ?, 
                 contact_person = ?, 
                 email = ?, 
                 phone = ? 
                    WHERE id = ?
            """, (type, website, description, contact_person, email, phone, organization_id))
            con.commit()

    def get_forms(self):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM studies ORDER BY organization_id ASC")
            return cur.fetchall()

    def get_single_form(self, form_id, organization_id):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM studies WHERE id = ? AND organization_id = ?", (form_id, organization_id))
            return cur.fetchone()

    def get_form_by_org(self, organization_id):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM studies WHERE organization_id = ? ORDER BY id desc", (organization_id,))
            return cur.fetchall()

    def edit_form(self, form_id, organization_id, title, status, description, available):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("""
            UPDATE studies SET 
                 title = ?,
                 status = ?,
                 description = ?, 
                 available = ? 
                    WHERE id = ? AND organization_id = ?""",
                 (title, status, description, available, form_id, organization_id))
            con.commit()

    def create_form(self, title, description, reward, organization_id):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("""
            INSERT INTO studies (title, description, reward, organization_id) VALUES (?, ?, ?, ?)""",
                 (title, description, reward, organization_id))
            con.commit()

    def get_enrollments_for_study(self, study_id):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("""
                SELECT
                    e.profile_id AS enrollment_id,
                    e.status AS enrollment_status,
                    p.first_name,
                    p.last_name,
                    d.name AS disability_id,
                    p.phone,
                    u.email
                FROM enrollments e
                JOIN profiles p ON e.profile_id = p.id
                JOIN users u ON e.profile_id = u.id
                JOIN profile_disabilities pd ON e.profile_id = pd.profile_id
                JOIN disabilities d ON pd.disability_id = d.id
                WHERE e.study_id = ?
            """, (study_id,))
            return cur.fetchall()