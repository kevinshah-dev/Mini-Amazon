from flask import current_app as app

class CartItem:
    def __init__(self, uid, pid, name, price, sid, seller_firstname, seller_lastname, quantity, savedforlater):
        self.uid = uid
        self.pid = pid
        self.name = name
        self.price = price
        self.sid = sid
        self.seller_firstname = seller_firstname
        self.seller_lastname = seller_lastname
        self.quantity = quantity
        self.savedforlater = savedforlater
    
    @staticmethod 
    def Cartforuid(uid):
        rows = app.db.execute('''
SELECT c.uid as uid, p.id AS pid, p.name AS name, p.price AS price, c.sid AS sid, u.firstname AS seller_firstname, u.lastname AS seller_lastname, c.quantity AS quantity, c.savedforlater AS savedforlater
FROM Carts AS c, Products AS p, Users AS u
WHERE c.pid = p.id AND c.uid = :uid AND u.id = c.sid AND c.savedforlater = FALSE
''', uid=uid)
        return [CartItem(*row) for row in rows]

    @staticmethod 
    def get(uid, pid,sid):
        row = app.db.execute('''
SELECT c.uid as uid, p.id AS pid, p.name AS name, p.price AS price, c.sid AS sid, u.firstname AS seller_firstname, u.lastname AS seller_lastname, c.quantity AS quantity, c.savedforlater AS savedforlater
FROM Carts AS c, Products AS p, Users AS u
WHERE c.pid = p.id AND c.uid = :uid AND c.pid = :pid AND c.sid=:sid AND u.id = c.sid AND c.savedforlater = FALSE
''',
                              uid=uid, pid = pid, sid=sid)
        return CartItem(*(row[0])) if row else None
    
    @staticmethod
    def addtoCart(uid, pid, sid, quantity):
        check = app.db.execute("""
SELECT uid, pid, sid, quantity 
FROM Carts
WHERE uid = :uid AND pid = :pid AND sid=:sid AND savedforlater = FALSE
""",
                                  uid=uid,
                                  pid=pid,sid=sid)
        if check:
            row = app.db.execute("""
UPDATE Carts
SET quantity = :quantity + (SELECT quantity FROM Carts WHERE uid = :uid AND pid = :pid AND sid=:sid AND savedforlater = FALSE)
WHERE uid = :uid AND pid = :pid AND sid=:sid AND savedforlater = FALSE
""",
                                  quantity = quantity, uid=uid,
                                  pid=pid, sid=sid)
            return CartItem.get(uid,pid,sid)
            
        else: 

            try:
                rows = app.db.execute("""
INSERT INTO Carts(uid, pid, sid, quantity)
VALUES(:uid, :pid, :sid, :quantity)
RETURNING uid
""",
                                  uid=uid,
                                  pid=pid,
                                  sid=sid,
                                  quantity=quantity)
                
#                 row = app.db.execute("""
# SELECT uid, pid, quantity
# FROM Carts
# WHERE uid = :uid AND pid= :pid
#                                      """, uid=uid, pid=pid)
                return CartItem.get(uid, pid,sid)
        
            except Exception as e:
                # the following simply prints the error to the console:
                print(str(e))
                return None
            
    @staticmethod
    def changeinCart (uid, pid, sid, quantity):
        if quantity> 0:
            row = app.db.execute("""
UPDATE Carts
SET quantity = :quantity 
WHERE uid = :uid and pid = :pid and sid = :sid AND savedforlater = FALSE
                              """, uid=uid, pid=pid, quantity=quantity, sid=sid)
            return CartItem.get(uid, pid, sid)
         
        else:
            row = app.db.execute("""
DELETE FROM Carts
WHERE uid = :uid and pid = :pid and savedforlater = FALSE
                                     """, uid=uid, pid=pid)
            return None
    
    @staticmethod
    def get_savedlistitem(uid, pid, sid):
        row = app.db.execute('''
SELECT c.uid as uid, p.id AS pid, p.name AS name, p.price AS price, c.sid AS sid, u.firstname AS seller_firstname, u.lastname AS seller_lastname, c.quantity AS quantity, c.savedforlater AS savedforlater
FROM Carts AS c, Products AS p, Users AS u
WHERE c.pid = p.id AND c.uid = :uid AND c.pid = :pid AND c.sid=:sid AND u.id = c.sid AND c.savedforlater = TRUE
''',
                              uid=uid, pid = pid, sid=sid)
        return CartItem(*(row[0])) if row else None
    
    @staticmethod
    def savedListforuid(uid):
        rows = app.db.execute('''
SELECT c.uid as uid, p.id AS pid, p.name AS name, p.price AS price, c.sid AS sid, u.firstname AS seller_firstname, u.lastname AS seller_lastname, c.quantity AS quantity, c.savedforlater AS savedforlater
FROM Carts AS c, Products AS p, Users AS u
WHERE c.pid = p.id AND c.uid = :uid AND u.id = c.sid AND c.savedforlater = TRUE
''', uid=uid)
        return [CartItem(*row) for row in rows]
    
    @staticmethod
    def addtoSavedList(uid, pid, sid, quantity):
        check = app.db.execute("""
SELECT uid, pid, sid, quantity 
FROM Carts
WHERE uid = :uid AND pid = :pid AND sid=:sid AND savedforlater = TRUE
""",
                                  uid=uid,
                                  pid=pid,sid=sid,quantity=quantity)
        if check:
            row = app.db.execute("""
UPDATE Carts
SET quantity = :quantity + (SELECT quantity FROM Carts WHERE uid = :uid AND pid = :pid AND sid=:sid AND savedforlater = TRUE)
WHERE uid = :uid AND pid = :pid AND sid=:sid AND savedforlater = TRUE
""",
                                  quantity = quantity, uid=uid,
                                  pid=pid, sid=sid)
            return CartItem.get_savedlistitem(uid,pid,sid)
            
        else: 
            try:
                rows = app.db.execute("""
INSERT INTO Carts(uid, pid, sid, quantity, savedforlater)
VALUES(:uid, :pid, :sid, :quantity, TRUE)
RETURNING uid
""",
                                  uid=uid,
                                  pid=pid,
                                  sid=sid,
                                  quantity=quantity)
                
                return CartItem.get_savedlistitem(uid, pid,sid)
            except Exception as e:
                # the following simply prints the error to the console:
                print(str(e))
                return None
    
    @staticmethod
    def changeinSavedList (uid, pid, sid, quantity):
        if quantity> 0:
            row = app.db.execute("""
UPDATE Carts
SET quantity = :quantity 
WHERE uid = :uid and pid = :pid and sid = :sid AND savedforlater = TRUE
                              """, uid=uid, pid=pid, quantity=quantity, sid=sid)
            return CartItem.get_savedlistitem(uid, pid, sid)
         
        else:
            row = app.db.execute("""
DELETE FROM Carts
WHERE uid = :uid and pid = :pid and savedforlater = TRUE
                                     """, uid=uid, pid=pid)
            return None