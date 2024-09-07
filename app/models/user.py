from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash
from psycopg2 import errors

from .. import login


class User(UserMixin):
    def __init__(self, id, email, firstname, lastname, address, balance):
        self.id = id
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.address = address
        self.balance = balance

    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
SELECT password, id, email, firstname, lastname, address, balance
FROM Users
WHERE email = :email
""",
                              email=email)
        if not rows:  # email not found
            return None
        elif not check_password_hash(rows[0][0], password):
            # incorrect password
            return None
        else:
            return User(*(rows[0][1:]))

    @staticmethod
    def email_exists(email):
        rows = app.db.execute("""
SELECT email
FROM Users
WHERE email = :email
""",
                              email=email)
        return len(rows) > 0

    @staticmethod
    def register(email, password, firstname, lastname, address):
        try:
            rows = app.db.execute("""
INSERT INTO Users(email, password, firstname, lastname, address)
VALUES(:email, :password, :firstname, :lastname, :address)
RETURNING id
""",
                                  email=email,
                                  password=generate_password_hash(password),
                                  firstname=firstname, lastname=lastname, address = address)
            id = rows[0][0]
            return User.get(id)
        except Exception as e:
            # likely email already in use; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None
    @staticmethod
    def get_User(id):

        rows = app.db.execute("""
SELECT id, email, firstname, lastname, address, balance
FROM Users
WHERE id = :id
""",
                              id=id)
        return User(*(rows[0])) if rows else None
    @staticmethod
    @login.user_loader
    def get(id):
        rows = app.db.execute("""
SELECT id, email, firstname, lastname, address, balance
FROM Users
WHERE id = :id
""",
                              id=id)
        return User(*(rows[0])) if rows else None

    def updateInfo(self, email, firstname, lastname, password, address):
        try:
            app.db.execute("""
                UPDATE Users
                SET email = :email, firstname = :firstname, lastname = :lastname, password = :password, address = :address
                WHERE id = :id
            """, email=email, firstname=firstname, lastname=lastname, password = password, address=address, id=self.id)
            self.email = email
            self.firstname = firstname
            self.lastname = lastname
            self.password = password
            self.address = address
            return 0
        except Exception as e:
            if isinstance(e.orig, errors.UniqueViolation):
                # Handle the unique violation error here
                return "Error: Email address already exists."
            else:
                # Handle other exceptions
                return "An error occurred during update."

    def increaseBalance(self,balance):
        try:
            newB = self.balance + balance
            app.db.execute("""
                UPDATE Users
                SET balance = :balance
                WHERE id = :id
            """, balance=newB, id=self.id)
            self.balance = newB
        except Exception as e:
            print(e)

    def withdrawBalance(self,balance):
        try:
            newB = self.balance - balance
            print(newB)
            if(newB>=0):
                
                app.db.execute("""
                    UPDATE Users
                    SET balance = :balance
                    WHERE id = :id
                """, balance=newB, id=self.id)
                self.balance = newB
                return 0
            else:
                return -1
        except Exception as e:
            print(e)
            
    def get_reviews(id, page, per_page):
        offset = (page - 1) * per_page
        rows = app.db.execute('''
SELECT *
FROM ProductReviews
WHERE uid = :id
OFFSET :offset ROWS FETCH NEXT :per_page ROWS ONLY;
''',
                              id=id,
                              offset=offset,
                              per_page=per_page)
        return [ProductReviews(*row) for row in rows]
    
    @staticmethod
    def increase_seller_balance(id, amount):
        rows = app.db.execute('''
                    UPDATE Users
                    SET balance = :amount + (SELECT balance FROM Users WHERE id=:id)
                    WHERE id = :id
                              ''', id=id, amount=amount)
        return rows