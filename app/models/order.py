from flask import current_app as app

class Order:
    def __init__(self, id, uid, pid, name, price, time_purchased, sid, seller_firstname, seller_lastname, quantity,completed,order_number):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.name = name
        self.price = price
        self.time_purchased = time_purchased
        self.sid = sid
        self.seller_firstname = seller_firstname
        self.seller_lastname = seller_lastname
        self.quantity = quantity
        self.completed = completed
        self.order_number = order_number
    
    @staticmethod
    def get_order_items(uid, ordernum):
        items = app.db.execute("""
        SELECT a.id AS id, a.uid AS uid, a.pid AS pid, b.name AS name, b.price AS price, 
                               a.time_purchased AS time_purchased, a.sid AS sid, u.firstname AS seller_firstname,
                               u.lastname AS seller_lastname, a.quantity AS quantity, a.completed AS completed,
                               a.order_number AS order_number
        FROM Purchases as a, Products as b, Users as u
        WHERE a.order_number = :ordernum AND a.uid = :uid AND a.pid = b.id AND a.sid = u.id
                               """, ordernum=ordernum, uid=uid)
        return [Order(*item) for item in items]