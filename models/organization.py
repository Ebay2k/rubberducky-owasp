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