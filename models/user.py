from data.database import Database

class User:
    def __init__(self, db_path: str):
        self.db = Database(db_path)

    def count_all(self):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT COUNT() FROM users")
            con.commit()
            return cur.fetchone()

    def get_user_by_email(self, email):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE email = ?", (email,))
            return cur.fetchone()

    def get_user_ervaringsdeskundige(self):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE role = 'expert'")
            return cur.fetchall()

    def update_users(self, status, id):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("UPDATE users SET status = ? WHERE id = ?", (status, id))
            con.commit()

    def get_ev_id(self):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT id FROM users")
            return cur.fetchone()