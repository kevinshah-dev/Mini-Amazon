from flask import render_template, request, session, redirect, url_for
from flask_login import current_user
import os

from .models.product import Product
from .models.productreviews import ProductReviews
from .models.category import Category

from flask import Blueprint
bp = Blueprint('category', __name__)
ITEMS_PER_PAGE = 20

def get_image(pid):
    filename = f"{pid}.png"
    if os.path.exists(filename):
        return filename
    else:
        return f"{(pid % 20)}.png"
    
@bp.route('/categories')
def categories():
    # assuming no pagination is needed
    categories = Category.get_categories()
    # render the page by adding information to the categories.html file
    return render_template('categories.html',
                           categories=categories,
                           active_tab='categories')