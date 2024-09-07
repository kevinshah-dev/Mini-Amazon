from flask import current_app as app
import datetime
from sqlalchemy import text


class Purchase:
    def __init__(self, id, uid, pid, time_purchased, sid, quantity,completed,order_number):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.time_purchased = time_purchased
        self.sid = sid
        self.quantity = quantity
        self.completed = completed
        self.order_number = order_number

## CHANGED SELECT id, uid, pid, time_purchased
#     @staticmethod
#     def get(id):
#         rows = app.db.execute('''
# SELECT *
# FROM Purchases
# WHERE id = :id
# ''',
#                               id=id)
#         return Purchase(*(rows[0])) if rows else None

    @staticmethod
    def get_all_by_uid_since(uid, since):
        rows = app.db.execute('''
SELECT *
FROM Purchases
WHERE uid = :uid
AND time_purchased >= :since
ORDER BY time_purchased DESC
''',
                              uid=uid,
                              since=since)
        return [Purchase(*row) for row in rows]

#     @staticmethod
#     def get_all_by_uid(uid):
#         rows = app.db.execute('''
# SELECT *
# FROM Purchases
# WHERE uid = :uid
# ORDER BY time_purchased DESC
# ''',
#                               uid=uid)
#         return [Purchase(*row) for row in rows]

    @staticmethod
    def get_all_by_uid_with_pagination(uid, page, per_page):
        offset = (page - 1) * per_page
        rows = app.db.execute('''
            SELECT *
            FROM Purchases
            WHERE uid = :uid
            ORDER BY time_purchased DESC
            OFFSET :offset ROWS FETCH NEXT :per_page ROWS ONLY;
        ''',
            uid=uid,
            offset=offset,
            per_page=per_page
        )
        return [Purchase(*row) for row in rows]

    @staticmethod
    def get_all_by_sid(sid):
        rows = app.db.execute('''
SELECT *
FROM Purchases
WHERE sid = :sid;
''',
                              sid=sid)
        return [Purchase(*row) for row in rows]
    # Get all by seller with pagination
    @staticmethod
    def get_all_by_sid_page(sid, page_order, per_page):
        offset = (page_order - 1) * per_page
        rows = app.db.execute('''
SELECT *
FROM Purchases
WHERE sid = :sid
ORDER BY time_purchased DESC
OFFSET :offset ROWS FETCH NEXT :per_page ROWS ONLY;

''',
                              sid=sid,
                              offset=offset,per_page=per_page)
        return [Purchase(*row) for row in rows]

    @staticmethod
    def get_sid_search_page(sid, page_order, per_page, fulfilled=None, search_str=''):
        offset = (page_order - 1) * per_page
        search_query = text('''
SELECT p.id, p.uid, p.pid, p.time_purchased, p.sid, p.quantity,p.completed,p.order_number
FROM Purchases p
JOIN Users ON p.uid = Users.id
WHERE sid = :sid                                             
''')
        if search_str:
            search_query = str(search_query) + f" AND LOWER(Users.firstname) LIKE LOWER(:search_str)"
        if fulfilled:
            if len(fulfilled)==1 and fulfilled[0]=='unfulfilled':
                search_query = str(search_query) + f" AND completed = false"
            if len(fulfilled)==1 and fulfilled[0]=='fulfilled':
                search_query = str(search_query) + f" AND completed = true"
        search_query = str(search_query) + ' ORDER BY time_purchased DESC OFFSET :offset ROWS FETCH NEXT :per_page ROWS ONLY'
        params = {'offset': offset, 'per_page': per_page, 'sid': sid}
        if search_str:
            params['search_str'] = f'%{search_str}%'
        print(search_query)
        rows = app.db.execute(search_query, **params)
        return [Purchase(*row) for row in rows]

    @staticmethod
    def get_sid_search_all(sid, fulfilled=None, search_str=''):
        search_query = text('''
SELECT p.id, p.uid, p.pid, p.time_purchased, p.sid, p.quantity,p.completed,p.order_number
FROM Purchases p
JOIN Users ON p.uid = Users.id
WHERE sid = :sid                                             
''')
        if search_str:
            search_query = str(search_query) + f" AND LOWER(Users.firstname) LIKE LOWER(:search_str)"
        if fulfilled:
            if len(fulfilled)==1 and fulfilled[0]=='unfulfilled':
                search_query = str(search_query) + f" AND completed = false"
            if len(fulfilled)==1 and fulfilled[0]=='fulfilled':
                search_query = str(search_query) + f" AND completed = true"
        search_query = str(search_query) + ' ORDER BY time_purchased DESC'
        params = {'sid': sid}
        if search_str:
            params['search_str'] = f'%{search_str}%'
        print("get_sid_search_all:",search_query)
        rows = app.db.execute(search_query, **params)
        return [Purchase(*row) for row in rows]

    @staticmethod
    def mark_complete(id):
        row = app.db.execute("""
            UPDATE Purchases
            SET completed = true
            WHERE id = :id
            """,
            id=id)
        return row
    
    @staticmethod
    def add_purchase(uid, pid, sid, quantity, order_number):
        
        row = app.db.execute("""
        INSERT INTO Purchases(uid,pid,sid,quantity,order_number)
        VALUES (:uid, :pid, :sid, :quantity, :order_number)
                             """, uid=uid, pid=pid, sid=sid, quantity=quantity, order_number=order_number)
    @staticmethod
    def get_order_number_ascending(uid, page, per_page):
        offset = (page - 1) * per_page
        rows = app.db.execute('''
            SELECT *
            FROM Purchases
            WHERE uid = :uid
            ORDER BY order_number ASC
            OFFSET :offset ROWS FETCH NEXT :per_page ROWS ONLY;
        ''',
            uid=uid,
            offset=offset,
            per_page=per_page
        )
        return [Purchase(*row) for row in rows]
    
    @staticmethod
    def get_order_number_descending(uid, page, per_page):
        offset = (page - 1) * per_page
        rows = app.db.execute('''
            SELECT *
            FROM Purchases
            WHERE uid = :uid
            ORDER BY order_number DESC
            OFFSET :offset ROWS FETCH NEXT :per_page ROWS ONLY;
        ''',
            uid=uid,
            offset=offset,
            per_page=per_page
        )
        return [Purchase(*row) for row in rows]


    @staticmethod
    def get_purchase_id_ascending(uid, page, per_page):
        offset = (page - 1) * per_page
        rows = app.db.execute('''
            SELECT *
            FROM Purchases
            WHERE uid = :uid
            ORDER BY id ASC
            OFFSET :offset ROWS FETCH NEXT :per_page ROWS ONLY;
        ''',
            uid=uid,
            offset=offset,
            per_page=per_page
        )
        return [Purchase(*row) for row in rows]
    
    @staticmethod
    def get_purchase_id_descending(uid, page, per_page):
        offset = (page - 1) * per_page
        rows = app.db.execute('''
            SELECT *
            FROM Purchases
            WHERE uid = :uid
            ORDER BY id DESC
            OFFSET :offset ROWS FETCH NEXT :per_page ROWS ONLY;
        ''',
            uid=uid,
            offset=offset,
            per_page=per_page
        )
        return [Purchase(*row) for row in rows]

    @staticmethod
    def get_completed_status_false_first(uid, page, per_page):
        offset = (page - 1) * per_page
        rows = app.db.execute('''
            SELECT *
            FROM Purchases
            WHERE uid = :uid
            ORDER BY completed ASC
            OFFSET :offset ROWS FETCH NEXT :per_page ROWS ONLY;
        ''',
            uid=uid,
            offset=offset,
            per_page=per_page
        )
        return [Purchase(*row) for row in rows]
    
    @staticmethod
    def get_completed_status_true_first(uid, page, per_page):
        offset = (page - 1) * per_page
        rows = app.db.execute('''
            SELECT *
            FROM Purchases
            WHERE uid = :uid
            ORDER BY completed DESC
            OFFSET :offset ROWS FETCH NEXT :per_page ROWS ONLY;
        ''',
            uid=uid,
            offset=offset,
            per_page=per_page
        )
        return [Purchase(*row) for row in rows]

    @staticmethod
    def get_date_ascending(uid, page, per_page):
        offset = (page - 1) * per_page
        rows = app.db.execute('''
            SELECT *
            FROM Purchases
            WHERE uid = :uid
            ORDER BY time_purchased ASC
            OFFSET :offset ROWS FETCH NEXT :per_page ROWS ONLY;
        ''',
            uid=uid,
            offset=offset,
            per_page=per_page
        )
        return [Purchase(*row) for row in rows]


    @staticmethod
    def get_five_pop(sid):
        rows = app.db.execute('''
SELECT pid, count(pid) as purchase_count
FROM Purchases
WHERE sid = :sid
GROUP BY pid
ORDER BY purchase_count DESC
LIMIT 5;
''',
                              sid=sid)
        # print(rows)
        return rows
    
    @staticmethod
    def get_max_order_num():
        maxnum = app.db.execute("""
    SELECT MAX(order_number)
    FROM Purchases
                             """)
        if maxnum:
            print("maxnum", type(maxnum), maxnum)
            print("maxnum2", type(maxnum[0]), maxnum[0])
            return maxnum[0]
        else:
            return 0
    
    @staticmethod
    def is_valid_review(uid, sid):
        rows = app.db.execute("""
SELECT *
FROM Purchases
WHERE uid = :uid AND sid = :sid
                             """, uid=uid, sid=sid)
        if rows:
            return True
        else:
            return False