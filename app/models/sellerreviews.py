from flask import current_app as app


class SellerReviews:
    def __init__(self, uid, sid, review, rating, review_time):
        self.uid = uid #user who the review is about
        self.sid = sid #user who is doing the review
        self.review = review
        self.rating = rating
        self.review_time = review_time if review_time is not None else datetime.datetime.utcnow()

    @staticmethod
    def get_reviewsid(id, page, per_page):
        offset = (page - 1) * per_page
        rows = app.db.execute('''
SELECT *
FROM SellerReviews
WHERE sid = :id
ORDER BY review_time DESC
OFFSET :offset ROWS FETCH NEXT :per_page ROWS ONLY;
''',
                              id=id,
                              offset=offset,
                              per_page=per_page)
        return [SellerReviews(*row) for row in rows]
    @staticmethod
    def get_reviewsuid(id):
        rows = app.db.execute('''
SELECT *
FROM SellerReviews
WHERE uid = :id
''',
                              id=id)
        return [SellerReviews(*row) for row in rows]

    @staticmethod
    def getspecificreviewseller(uid, sid):
        rows = app.db.execute('''
SELECT *
FROM SellerReviews
WHERE uid = :uid AND sid = :sid
''',
                              uid=uid,
                              sid=sid)
        return [SellerReviews(*row) for row in rows]
    
    @staticmethod
    def get_seller_avg(sid):
        result = app.db.execute('''
SELECT AVG(rating)
FROM SellerReviews
WHERE sid = :sid
''',
                              sid=sid)
        avg = result[0][0]
        if avg is None: 
            return 0
        else:
            return int(100*(result[0][0])/5)
    
    @staticmethod
    def insert_seller_review(uid, sid, review, rating, review_time):
        app.db.execute('''
INSERT INTO SellerReviews (uid, sid, review, rating, review_time)
VALUES (:uid, :sid, :review, :rating, :review_time)
''',
                       uid=uid,
                       sid=sid,
                       review=review,
                       rating=rating,
                       review_time=review_time)
        return True

class SellerReviewsWithName(SellerReviews):
    def __init__(self, uid, sid, review, rating, review_time, fname, lname):
        super().__init__(uid, sid, review, rating, review_time)
        self.fname = fname
        self.lname = lname

    @staticmethod
    def get_reviewsid(id, page, per_page):
        offset = (page - 1) * per_page
        rows = app.db.execute('''
SELECT sr.*, u.firstname, u.lastname
FROM SellerReviews sr, Users u
WHERE sid = :id AND sr.uid = u.id
ORDER BY review_time DESC
OFFSET :offset ROWS FETCH NEXT :per_page ROWS ONLY;
''',
                              id=id,
                              offset=offset,
                              per_page=per_page)
        return [SellerReviewsWithName(*row) for row in rows]