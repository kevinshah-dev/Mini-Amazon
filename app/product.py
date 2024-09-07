from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user
from datetime import datetime, timedelta
import datetime as dt
import os
from sqlalchemy.exc import IntegrityError
from .models.product import Product
from .models.purchase import Purchase
from .models.productreviews import ProductReviews, NameProductReviews
from .models.sellerreviews import SellerReviews

from .models.user import User

from flask import Blueprint
bp = Blueprint('product', __name__)
REVIEWS_PER_PAGE = 5

# specific product page result
@bp.route('/productid/<int:id>', methods=['POST', 'GET'])
def product(id):
    # get this product id:
    product = Product.get(id)
    # check if product image exists
    image_name = f'{id}.png'
    image_path = os.path.join('/home/ubuntu/mini-amazon-skeleton/app/static/img/products', image_name)
    if os.path.exists(image_path):
        image_url = url_for('static', filename=f'img/products/{id}.png')
    else: 
        image_url = url_for('static', filename=f'img/products/{id%20}.png') # chooses one of the default 20 images
    # find the products current user has bought:
    if current_user.is_authenticated:
        purchases = Purchase.get_all_by_uid_since(
            current_user.id, (datetime.now()- timedelta(weeks=4)))
    else:
        purchases = None
    # find the reviews for this product:
    page = request.args.get('page', default=1, type=int)
    reviews = NameProductReviews.get_reviews_name(id, page, REVIEWS_PER_PAGE)
    avgRating = round(ProductReviews.get_product_average_kevin(id), 1)
    total_reviews = ProductReviews.get_product_review_count(id)
    # get sellers for this product
    sellers = Product.get_sellers(product.id)
    # get profile pics and seller ratings
    seller_ids = Product.get_seller_ids(product.id)
    length_s = len(seller_ids)
    profile_urls = []
    seller_ratings = []
    for id in seller_ids:
        # get image
        profile_picture_path = f'/home/ubuntu/mini-amazon-skeleton/app/static/img/profilePics/{id}.png'
        if os.path.exists(profile_picture_path):
            profile_urls.append(f'img/profilePics/{id}.png')
        else:
            profile_urls.append(f'img/profilePics/defaultPic.png')
        # get average rating
        seller_ratings.append(SellerReviews.get_seller_avg(id))
    length_r = len(reviews)
    combined_sellers = zip(sellers, profile_urls, seller_ratings)
    # render the product page
    return render_template('product.html',
                           product=product,
                           image_url=image_url,
                           purchase_history=purchases,
                           reviews=reviews,
                           page=page, 
                           combined_sellers=combined_sellers,
                           avgRating=avgRating,
                           total_reviews=total_reviews,
                           length_s=length_s,
                           length_r=length_r,
                           per_page=REVIEWS_PER_PAGE,
                           active_tab='')

@bp.route('/productid/<int:id>/addreview', methods=['GET'])
def addproductreview(id):
    return render_template('addreview.html',
                           productid=id,
                           active_tab='')

@bp.route('/reviewsuccess/<int:id>', methods=['POST'])
def insertreview(id):
    if current_user.is_authenticated: 
        try:
            review = request.form["reviewText"]
            rating = request.form["rating"]
            time = dt.datetime.now()
            formattedtime = time.strftime("%Y-%m-%d %H:%M:%S")
            Product.add_review(current_user.id, id, review, rating, formattedtime)
            return redirect(url_for('product.product', id=id))
        except IntegrityError:
            flash("You have already reviewed this product!")
            return render_template('addreview.html', productid=id, active_tab='')

@bp.route('/updatereviewpage/<int:id>/<int:pid>', methods=['GET'])
def updatereviewpage(id, pid):
    review = ProductReviews.getspecificreview(id, pid)
    return render_template('updatereview.html', id=id, pid=pid, active_tab='', review=review)

@bp.route('/updatereview/<int:id>/<int:pid>', methods=['POST'])
def updatereview(id, pid):
    if current_user.is_authenticated:
        try:
            review = request.form["reviewText"]
            rating = request.form["rating"]
            time = dt.datetime.now()
            formattedtime = time.strftime("%Y-%m-%d %H:%M:%S")
            Product.update_review(id, pid, review, rating, formattedtime)
            return redirect(url_for('users.privateProfile'))
        except IntegrityError:
            flash("You have already reviewed this product!")
            return render_template('updatereview.html', id=id, pid=pid)

@bp.route('/deletereview/<int:uid>/<int:pid>', methods=['POST', 'GET'])
def deletereview(uid, pid):
    if current_user.is_authenticated:
        Product.delete_review(uid, pid)
        return redirect(url_for('users.privateProfile'))

@bp.route('/updatesellerreviewpage/<int:id>/<int:sid>', methods=['GET', 'POST'])
def updatesellerreviewpage(id, sid):
    return render_template('updatesellerreview.html', id=id, sid=sid)

@bp.route('/updatesellerreview/<int:id>/<int:sid>', methods=['POST'])
def updatesellerreview(id, sid):
    if current_user.is_authenticated:
        try:
            review = request.form["reviewText"]
            rating = request.form["rating"]
            time = dt.datetime.now()
            formattedtime = time.strftime("%Y-%m-%d %H:%M:%S")
            Product.update_review_seller(current_user.id, sid, review, rating, formattedtime)
            return redirect(url_for('users.privateProfile'))
        except IntegrityError:
            return render_template('updatereview.html', id=id, pid=pid)

@bp.route('/deletesellerreview/<int:uid>/<int:sid>', methods=['POST', 'GET'])
def deletesellerreview(uid, sid):
    if current_user.is_authenticated:
        Product.delete_seller_review(uid, sid)
        return redirect(url_for('users.privateProfile'))
