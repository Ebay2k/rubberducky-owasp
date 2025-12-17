from data.database import Database


class Profiles:
    def __init__(self, db_path: str):
        self.db = Database(db_path)

    def get_profile(self):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM profiles")
            con.commit()
            return cur.fetchall()
