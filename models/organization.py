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

    def edit_form(self, form_id, title, status, description, available):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("""
            UPDATE studies SET title = ?,
                 status = ?,
                 description = ?, 
                 available = ? 
                 WHERE id = ?""",
                 (title, status, description, available, form_id))
            con.commit()

    def create_form(self, title, status, description, available, organization_id):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("""
            INSERT INTO studies (title, status, description, available, organization_id) VALUES (?, ?, ?, ?, ?)""",
                 (title, status, description, available, organization_id))
            con.commit()