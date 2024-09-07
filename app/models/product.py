from flask import current_app as app
import os
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

class Product:
    def __init__(self, id, name, price, available, category, description):
        self.id = id
        self.name = name
        self.price = price
        self.available = available
        self.category = category
        self.description = description

### Adding/Updating Product ###
    @staticmethod
    def add_product(uid, name, price, category, description):
        exists = app.db.execute('''
SELECT *
FROM Products                            
WHERE name = :name
''',
                                  name=name) # check that product doesn't already exist
        if exists:       
            print(str(Exception))
            return None #  failure, already exists
        
        else: 
            new_pid = app.db.execute('''
SELECT MAX(id)+1 FROM Products''') 
            pid = new_pid[0][0] # pid for new product
            new_row = app.db.execute('''
INSERT INTO Products
VALUES (:pid, :name, :price, :available, :category, :description)
''',
                                  pid=pid,
                                  name=name,
                                  price=price,
                                  available=True, # assuming if adding it is avaliable
                                  category=category,
                                  description=description)
            new_prod = app.db.execute('''
INSERT INTO AddedProducts
VALUES (:uid, :pid)
''',
                                  uid=uid,
                                  pid=pid) # tracks that this user was the one who added this product
            return pid # success, return pid for newly added product 

    @staticmethod
    def get_added(uid):
        rows = app.db.execute('''
SELECT Products.id AS id, name, price, available, category, description
FROM Products INNER JOIN AddedProducts ON Products.id = AddedProducts.pid
WHERE AddedProducts.uid = :uid
''',
                              uid=uid)
        return [Product(*row) for row in rows]

    @staticmethod
    def update_product(pid, name, price, category, description):
        # since the button only appears on a user's mystorefront for products they added, don't need to check they have permission
        try:
            rows = app.db.execute('''
UPDATE Products
SET name=:name, price=:price, category=:category, description=:description
WHERE id=:pid
''',   
                                  pid=pid,
                                  name=name,
                                  price=price,
                                  category=category,
                                  description=description)
        except SQLAlchemyError as e:
            print(f"Error: {e}")
        return rows # success if greater than 0 (in this case should be 1)
        
    @staticmethod # WORK IN PROGRESS, TO DISPLAY SELLERS ON PRODUCT PAGE
    def get_sellers(pid):
        rows = app.db.execute('''
SELECT *
FROM Supply
WHERE pid = :pid
AND seller_inventory > 0                                                           
''', 
                                  pid=pid)
        if rows:
            return rows # probably not correct...
        else: # set avaliability of product to false
#             rows = app.db.execute('''
# UPDATE Products
# SET avaliable = FALSE
# WHERE pid = :pid                                                          
# ''', 
#                                   pid=pid)
            return -1



### Getting Products ###
    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT *
FROM Products
WHERE id = :id
''',
                              id=id)
        return Product(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all_paginate(page, per_page):
        offset = (page - 1) * per_page
        rows = app.db.execute('''
SELECT *
FROM Products
WHERE available = :available
OFFSET :offset ROWS FETCH NEXT :per_page ROWS ONLY;
''',
                              available=True,
                              offset=offset,
                              per_page=per_page)
        return [Product(*row) for row in rows]


### Filtering ###
    @staticmethod
    def get_search_paginate(page, per_page, categories_selected=None, filter=None, sort=None, search_str=''):
        offset = (page - 1) * per_page
        my_query = text('''
SELECT p.id, p.name, p.price, p.available, p.category, p.description
FROM Products p
LEFT JOIN (
    SELECT pid, AVG(rating) as rating, COUNT(*) as reviews
    FROM ProductReviews
    GROUP BY pid
) pr ON p.id = pr.pid                        
WHERE 1=1                                                
''')    # 1=1 to start the WHERE clause
        
        # apply filters
        if search_str:
            my_query = str(my_query) + f" AND lower(name) LIKE :search_str"
        if categories_selected:
            if len(categories_selected) == 1:
                my_query = str(my_query) + f" AND category = '{categories_selected[0]}'"
            else:
                categories_selected = tuple(categories_selected)
                my_query = str(my_query) + f' AND category IN {categories_selected}'
        if filter:
            for field, values in filter.items():
                print(f'Field: {field}, Values: {values}')
                if not values:
                    print('no value')
                elif field == 'p.available':
                    # if none are chosen just pretend it's both...
                    # if both selected, do nothing
                    if len(values) == 1 and 'false' in values:
                        my_query = str(my_query) + f' AND p.available = FALSE'
                    if len(values) == 1 and 'true' in values:
                        my_query = str(my_query) + f' AND p.available = TRUE'
                elif field == 'min_rating':
                    my_query = str(my_query) + ' AND pr.rating >= :min_rating'
                elif field == 'min_reviews':
                    my_query = str(my_query) + ' AND pr.reviews >= :min_reviews'
                elif field == 'max_price':
                    my_query = str(my_query) + ' AND price <= :max_price'                       
        
        # apply sorting in order from first to last in dictionary sort
        if sort:
            order_by = []
            for field, order in sort.items():
                order_by.append(f'{field} {"DESC" if order == "DESC" else "ASC"}')
            order_by = ', '.join(order_by)    
            my_query = str(my_query) + f' ORDER BY {order_by}'

        # pagination
        my_query = str(my_query) + ' OFFSET :offset ROWS FETCH NEXT :per_page ROWS ONLY'
        
        # parameters for execution
        params = {'offset': offset, 'per_page': per_page}
        if search_str:
            params['search_str'] = f'%{search_str}%'
        if filter:
            params.update(filter)

        # execution
        print(my_query)
        rows = app.db.execute(my_query, **params)
        return [Product(*row) for row in rows]

### Kevin ###
    @staticmethod
    def add_review(uid, pid, review, rating, time):
        app.db.execute('''
INSERT INTO ProductReviews(uid, pid, review, rating, review_time)
VALUES(:uid, :pid, :review, :rating, :time)
''',
                       uid=uid,
                       pid=pid,
                       rating=rating,
                       review=review,
                       time=time)
        return True
    
    @staticmethod
    def update_review(uid, pid, review, rating, time):
        app.db.execute('''
UPDATE ProductReviews
SET review=:review, rating=:rating, review_time=:time
WHERE uid=:uid AND pid=:pid
''',
                       uid=uid,
                       pid=pid,
                       rating=rating,
                       review=review,
                       time=time)
        return True
    
    @staticmethod
    def get_sellers(pid):
        sellers = app.db.execute("""
SELECT supply.uid AS sid, users.firstname AS firstname, users.lastname AS lastname, Products.price AS price
FROM Supply, Users, Products
WHERE supply.uid = users.id AND supply.pid = :pid AND Products.id = :pid
                                 """, pid = pid)

        return sellers
    
    @staticmethod
    def get_seller_ids(pid):
        ids = app.db.execute("""
SELECT supply.uid
FROM Supply, Users
WHERE supply.uid = users.id AND supply.pid = :pid
                                 """, pid = pid)

        return [row[0] for row in ids]

    @staticmethod
    def delete_review(uid, pid):
        app.db.execute('''
DELETE FROM ProductReviews
WHERE uid=:uid AND pid=:pid
''',
                       uid=uid,
                       pid=pid)
        return True


    @staticmethod
    def get_max_pid():
        maxnum = app.db.execute("""
SELECT MAX(id)
FROM Products
                             """)
        if maxnum:
            return maxnum[0]
        else:
            return 0
    
    @staticmethod
    def delete_seller_review(uid, sid):
        app.db.execute('''
DELETE FROM SellerReviews
WHERE uid=:uid AND sid=:sid
''',
                       uid=uid,
                       sid=sid)
        return True

    @staticmethod
    def update_review_seller(uid, sid, review, rating, time):
        app.db.execute('''
UPDATE SellerReviews
SET review=:review, rating=:rating, review_time=:time
WHERE uid=:uid AND sid=:sid
''',
                       uid=uid,
                       sid=sid,
                       rating=rating,
                       review=review,
                       time=time)
        return True
