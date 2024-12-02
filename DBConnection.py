import mysql.connector

class Db:
    def __init__(self):
        self.cnx = mysql.connector.connect(host="localhost", user="root", password="", database="examportal", port=3306)
        self.cur = self.cnx.cursor(dictionary=True,buffered=True)


    def select(self, q):
        self.cur.execute(q)
        return self.cur.fetchall()

    def login(self, q, username, password):
        self.cur.execute(q, (username, password,))
        return self.cur.fetchone()

    def selectOne(self, q):
        self.cur.execute(q)
        return self.cur.fetchone()


    def insert(self, q):
        self.cur.execute(q)
        self.cnx.commit()
        return self.cur.lastrowid

    def update(self, q):
        self.cur.execute(q)
        self.cnx.commit()
        return self.cur.rowcount

    def delete(self, q):
        self.cur.execute(q)
        self.cnx.commit()
        return self.cur.rowcount
