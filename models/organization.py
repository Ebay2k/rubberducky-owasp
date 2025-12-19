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

    def get_forms(self):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM studies ORDER BY organization_id ASC")
            return cur.fetchall()

    def get_single_form(self, form_id):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM studies WHERE id = ?", (form_id,))
            return cur.fetchone()

    def edit_form(self, form_id, title, status, description, available, start_date, end_date, study_type, location, has_reward, reward, age_min, age_max):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute(f"UPDATE studies SET title = ?, status = ?, description = ?, available = ?,"
                        f" start_date = ?, end_date = ?, study_type = ?, location = ?, has_reward = ?,"
                        f" reward = ?, age_min = ?, age_max = ? WHERE id = ?",
                        (title, status, description, available, start_date, end_date, study_type, location, has_reward, reward, age_min, age_max, form_id))
            con.commit()