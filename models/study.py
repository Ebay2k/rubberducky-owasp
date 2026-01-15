from data.database import Database


class Study:
    def __init__(self, db_path: str):
        self.db = Database(db_path)

    def count_all(self):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT COUNT() FROM studies")
            con.commit()
            return cur.fetchone()

    def get_study(self):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM studies ORDER BY id")
            con.commit()
            return cur.fetchall()

    def get_studies_org(self):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM studies")
            return cur.fetchall()

    def update_studies(self, status, id):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("UPDATE studies SET status = ? WHERE id = ?", (status, id))
            con.commit()

    def get_org_id(self):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT id FROM studies")
            return cur.fetchone()