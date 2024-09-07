from flask import render_template, request
from flask_login import current_user
import datetime

from .models.productreviews import ProductReviews

from flask import Blueprint
bp = Blueprint('productreviews', __name__)

@bp.route('/reviewsbyuser', methods=['POST'])
def reviews_by_uid():
    uid = int(request.form["uid"])
    recentreviews = ProductReviews.get_five_recent(uid)
    return render_template('productreviews.html',
                      reviews=recentreviews,
                      active_tab='index')



