from flask import current_app as app


class ProductReviews:
    def __init__(self, uid, pid, review, rating, review_time):
        self.uid = uid
        self.pid = pid
        self.review = review
        self.rating = rating
        self.review_time = review_time if review_time is not None else datetime.datetime.utcnow()


    
    @staticmethod
    def get_five_recent(uid):
        rows = app.db.execute('''
SELECT *
FROM ProductReviews
WHERE uid = :uid
ORDER BY review_time DESC
LIMIT 5
''',
                              uid=uid)
        # print(rows)
        return [(ProductReviews(*row)) for row in rows]

    @staticmethod
    def get_product_avg(pid):
        result = app.db.execute('''
SELECT AVG(rating)
FROM ProductReviews
WHERE pid = :pid                                                            
''',
                              pid=pid)
        avg = result[0][0]
        if avg is None: 
            return 0
        else:
            return int(100*(result[0][0])/5)

    @staticmethod
    def get_reviews(id, page, per_page):
        offset = (page - 1) * per_page
        rows = app.db.execute('''
SELECT *
FROM ProductReviews
WHERE pid = :id
ORDER BY review_time DESC
OFFSET :offset ROWS FETCH NEXT :per_page ROWS ONLY;
''',
                              id=id,
                              offset=offset,
                              per_page=per_page)
        return [ProductReviews(*row) for row in rows]

    @staticmethod
    def get_reviewsid(id, page, per_page):
        offset = (page - 1) * per_page
        rows = app.db.execute('''
SELECT *
FROM ProductReviews
WHERE uid = :id
ORDER BY review_time DESC
OFFSET :offset ROWS FETCH NEXT :per_page ROWS ONLY;
''',
                              id=id,
                              offset=offset,
                              per_page=per_page)
        return [ProductReviews(*row) for row in rows]
    
    @staticmethod
    def get_product_average_kevin(pid):
        result = app.db.execute('''
SELECT AVG(rating)
FROM ProductReviews
WHERE pid = :pid                                                            
''',
                              pid=pid)
        avg = result[0][0]
        if avg is None: 
            return 0
        else:
            return avg
    
    @staticmethod
    def get_product_review_count(pid):
        result = app.db.execute('''
SELECT COUNT(*)
FROM ProductReviews
WHERE pid = :pid                                                            
''',
                              pid=pid)
        count = result[0][0]
        if count is None: 
            return 0
        else:
            return count
    
    @staticmethod
    def getspecificreview(uid, pid):
        rows = app.db.execute('''
SELECT *
FROM ProductReviews
WHERE uid = :uid AND pid = :pid
''',
                              uid=uid,
                              pid=pid)
        print(rows)
        return [ProductReviews(*row) for row in rows]


class ExtendedProductReviews(ProductReviews):
    def __init__(self, uid, pid, review, rating, review_time, pname):
        super().__init__(uid, pid, review, rating, review_time)
        self.pname = pname
    

    @staticmethod
    def get_reviewsid(id, page, per_page):
        offset = (page - 1) * per_page
        rows = app.db.execute('''
SELECT pr.uid, pr.pid, pr.review, pr.rating, pr.review_time, p.name
FROM ProductReviews pr, Products p
WHERE uid = :id AND pr.pid = p.id
ORDER BY review_time DESC
OFFSET :offset ROWS FETCH NEXT :per_page ROWS ONLY;
''',
                              id=id,
                              offset=offset,
                              per_page=per_page)
        return [ExtendedProductReviews(*row) for row in rows]
    

class NameProductReviews(ProductReviews):
    def __init__(self, uid, pid, review, rating, review_time, uname, lname):
        super().__init__(uid, pid, review, rating, review_time)
        self.uname = uname
        self.lname = lname
    
    @staticmethod
    def get_reviews_name(id, page, per_page):
        offset = (page - 1) * per_page
        rows = app.db.execute('''
SELECT pr.uid AS uid, pr.pid AS pid, pr.review AS review, pr.rating AS rating, pr.review_time AS review_time, u.firstname AS uname, u.lastname AS lname
FROM ProductReviews pr, Users u
WHERE pr.pid = :id AND pr.uid = u.id
ORDER BY review_time DESC
OFFSET :offset ROWS FETCH NEXT :per_page ROWS ONLY;
''',
                              id=id,
                              offset=offset,
                              per_page=per_page)
        return [NameProductReviews(*row) for row in rows]