from flask import render_template, request, session, redirect, url_for
from flask_login import current_user
from datetime import datetime, timedelta
import os

from .models.product import Product
from .models.purchase import Purchase
from .models.productreviews import ProductReviews
from .models.category import Category

from flask import Blueprint
bp = Blueprint('index', __name__)
bp.secret_key = '532THxOtd^UoA#iSeuw87FWP@r$fsN9'
ITEMS_PER_PAGE = 20

def get_image(pid):
    filename = f"{pid}.png"
    if os.path.exists(filename):
        return filename
    else:
        return f"{(pid % 20)}.png"
    
@bp.route('/', methods=['POST', 'GET'])
def index():
    page = request.args.get('page', default=1, type=int)
    # default page is get all available products for sale:
    products = Product.get_all_paginate(page, ITEMS_PER_PAGE)
    # get product ratings
    ratings = []
    for product in products:
        ratings.append(ProductReviews.get_product_avg(product.id))
    # combine product with rating data
    combined_products = zip(products, ratings)
    # get categories
    categories = Category.get_category_names()
    # find the products current user has bought:
    if current_user.is_authenticated:
        purchases = Purchase.get_all_by_uid_since(
            current_user.id, (datetime.now()- timedelta(weeks=4)))
    else:
        purchases = None
    # disable next if less than 20 on this page
    length = len(products)
    # render the page by adding information to the index.html file
    return render_template('index.html',
                           avail_products=combined_products,
                           get_image=get_image,
                           page=page,
                           purchase_history=purchases,
                           categories=categories,
                           length=length,
                           per_page=ITEMS_PER_PAGE,
                           active_tab='index')

# Search
@bp.route('/search', methods=['POST', 'GET'])
def search():
    page = request.args.get('page', default=1, type=int)
    categories_selected = None
    availability = None
    min_rating = None
    min_reviews = None
    max_price = None
    sort1 = None
    sort2 = None
    sort3 = None
    sort4 = None
    search_str = None
    session['categories_selected'] = None
    # Update values if form submission
    if request.method == 'POST':
        session['categories_selected'] = request.form.getlist('category')
        session['availability'] = request.form.getlist('availability')
        session['min_rating'] = request.form.get('min_rating')
        session['min_reviews'] = request.form.get('min_reviews')
        session['max_price'] = request.form.get('max_price')
        session['sort1'] = request.form.get('sort1')
        session['sort2'] = request.form.get('sort2')
        session['sort3'] = request.form.get('sort3')
        session['sort4'] = request.form.get('sort4')
        session['search_str'] = request.form.get('search_str')
    
    categories_selected = session.get('categories_selected')
    availability = session.get('availability')
    min_rating = session.get('min_rating')
    min_reviews = session.get('min_reviews')
    max_price = session.get('max_price')
    sort1 = session.get('sort1')
    sort2 = session.get('sort2')
    sort3 = session.get('sort3')
    sort4 = session.get('sort4')
    search_str = session.get('search_str')

    filter = {}
    filter['p.available'] = availability # required field (theoretically)
    if min_rating and not None:
        filter['min_rating'] = min_rating
    if min_reviews and not None:
        filter['min_reviews'] = min_reviews
    if max_price and not None:
        filter['max_price'] = max_price

    sort = {}
    if sort1 and not None:
        sort_by = sort1.split()
        # modifications to work with SQL query
        if sort_by[0]=='rating': 
            sort_by[0] = 'pr.rating'
        if sort_by[0]=='reviews':
            sort_by[0] = 'pr.reviews'
        sort[sort_by[0]] = sort_by[1]
    if sort2 and not None:
        sort_by = sort2.split()
        if sort_by[0]=='rating': 
            sort_by[0] = 'pr.rating'
        if sort_by[0]=='reviews':
            sort_by[0] = 'pr.reviews'
        sort[sort_by[0]] = sort_by[1]
    if sort3 and not None:
        sort_by = sort3.split()
        if sort_by[0]=='rating': 
            sort_by[0] = 'pr.rating'
        if sort_by[0]=='reviews':
            sort_by[0] = 'pr.reviews'
        sort[sort_by[0]] = sort_by[1]
    if sort4 and not None:
        sort_by = sort4.split()
        if sort_by[0]=='rating': 
            sort_by[0] = 'pr.rating'
        if sort_by[0]=='reviews':
            sort_by[0] = 'pr.reviews'
        sort[sort_by[0]] = sort_by[1]

    # If arriving here from categories page (POST)
    category_param = request.args.get('category')
    if request.method == 'POST' and category_param:
        # If a category parameter is present, filter products by category
        categories_selected.append(category_param)
        session['categories_selected'] = category_param

    products = Product.get_search_paginate(page, ITEMS_PER_PAGE, categories_selected, 
                                           filter, sort, search_str)
    # get product ratings
    ratings = []
    for product in products:
        ratings.append(ProductReviews.get_product_avg(product.id))
    # combine product with rating data
    combined_products = zip(products, ratings)
    # get categories
    categories = Category.get_category_names()
    # find the products current user has bought:
    if current_user.is_authenticated:
        purchases = Purchase.get_all_by_uid_since(
            current_user.id, (datetime.now()- timedelta(weeks=4)))
    else:
        purchases = None
    length = len(products)
    return render_template('index.html',
                           avail_products=combined_products,
                           get_image=get_image,
                           page=page,
                           purchase_history=purchases,
                           categories=categories,
                           clicked_category=category_param,
                           categories_selected=categories_selected,
                           availability=availability,
                           min_rating=min_rating,
                           min_reviews=min_reviews,
                           max_price=max_price,
                           sort1=sort1,
                           sort2=sort2,
                           sort3=sort3,
                           sort4=sort4,
                           search_str=search_str,
                           length=length,
                           per_page=ITEMS_PER_PAGE,
                           active_tab='index')
    # clicked_category corresponds to registering a click from categories page
