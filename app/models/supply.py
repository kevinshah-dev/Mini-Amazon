from flask import current_app as app


class ItemforSale:
    def __init__(self, uid, pid, seller_inventory):
        self.uid = uid
        self.pid = pid
        self.seller_inventory = seller_inventory

    @staticmethod
    def get(uid,pid):
        rows = app.db.execute('''
SELECT uid, pid, seller_inventory
FROM Supply
WHERE uid = :uid
AND pid = :pid
''',
                              uid=uid,
                              pid=pid)
        return ItemforSale(*(rows[0])) if rows is not None else None


    @staticmethod
    def get_all_by_uid(uid):
        rows = app.db.execute('''
SELECT uid, pid, seller_inventory
FROM Supply
WHERE uid = :uid
''',
                              uid=uid)
        return [ItemforSale(*row) for row in rows]


    @staticmethod
    def addtoInv(uid, pid, seller_inventory):
        check = app.db.execute("""
SELECT uid, pid, seller_inventory
FROM Supply
WHERE uid = :uid AND pid = :pid
""",
                                  uid=uid,
                                  pid=pid)
        if check:
            row = app.db.execute("""
UPDATE Supply
SET seller_inventory = :seller_inventory + (SELECT seller_inventory FROM Supply WHERE uid = :uid AND pid = :pid)
WHERE uid = :uid AND pid = :pid
""",
                                  seller_inventory = seller_inventory, uid=uid,
                                  pid=pid)
            if row:
                return ItemforSale.get(uid,pid)
            else:
                return None
        else: 
            try:
                rows = app.db.execute("""
INSERT INTO Supply(uid, pid, seller_inventory)
VALUES(:uid, :pid, :seller_inventory)
RETURNING uid, pid
""",
                                  uid=uid,
                                  pid=pid,
                                  seller_inventory=seller_inventory)
                uid = rows[0][0]
                pid = rows[0][1]
                return ItemforSale.get(uid,pid)
            except Exception as e:
                # the following simply prints the error to the console:
                print(str(e))
                return None


    @staticmethod
    def get_all_by_uid_with_pagination(uid, page_selling, per_page):
        offset = max((page_selling - 1) * per_page, 0)#(page_selling - 1) * per_page
        rows = app.db.execute('''
            SELECT uid, pid, seller_inventory
            FROM Supply
            WHERE uid = :uid
            ORDER BY pid
            OFFSET :offset ROWS FETCH NEXT :per_page ROWS ONLY;
        ''',
            uid=uid,
            offset=offset,
            per_page=per_page
        )
        return [ItemforSale(*row) for row in rows]

    @staticmethod
    def delete_item(uid, pid):
        row = app.db.execute("""
            DELETE FROM Supply
            WHERE uid = :uid AND pid = :pid
            """,
            uid=uid,pid=pid)
        return row

    @staticmethod
    def update_q(uid, pid, new_q):
        check = app.db.execute("""
SELECT uid, pid
FROM Supply
WHERE uid = :uid AND pid = :pid
""",
                                  uid=uid,
                                  pid=pid)
        if check:
            row = app.db.execute("""
UPDATE Supply
SET seller_inventory = :new_q
WHERE uid = :uid AND pid = :pid
""",
                                  new_q=new_q, uid=uid,
                                  pid=pid)
            if row:
                return ItemforSale.get(uid,pid)
            else:
                return None
        else: 
            return None
    
    @staticmethod
    def decrease_inventory(uid, pid, quantity):
        row = app.db.execute("""
    UPDATE Supply
    SET seller_inventory = seller_inventory - :quantity
    WHERE uid = :uid AND pid = :pid
                             """, uid=uid, pid=pid, quantity=quantity)
        return row
        