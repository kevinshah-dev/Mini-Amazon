from flask import render_template, jsonify, request, redirect, url_for
from flask_login import current_user
from .models.product import Product
from .models.purchase import Purchase
from flask import Blueprint

bp = Blueprint('purchases', __name__)

@bp.route('/purchases', methods=['GET'])
def purchases():
    page = request.args.get('page', default=1, type=int)
    per_page = 10  # Number of records per page, adjust as needed

    if current_user.is_authenticated:

        # Retrieve the sorting option from the query parameters
        sort_by = request.args.get('sort_by', 'default')  # Default to 'order_numberA' if not provided

        # Use the sort_by value to modify your query accordingly
        if sort_by == 'default' or sort_by == "dateD":
            # Retrieve the user's purchase history with pagination
            purchases = Purchase.get_all_by_uid_with_pagination(current_user.id, page, per_page)
        elif sort_by == 'order_numberA':
            # Sort by order number in ascending order
            purchases = Purchase.get_order_number_ascending(current_user.id, page, per_page)
        elif sort_by == 'order_numberD':
            # Sort by order number in descending order
            purchases = Purchase.get_order_number_descending(current_user.id, page, per_page)
        elif sort_by == 'purchase_idA':
            # Sort by purchase ID in ascending order
            purchases = Purchase.get_purchase_id_ascending(current_user.id, page, per_page)
        elif sort_by == 'purchase_idD':
            # Sort by purchase ID in descending order
            purchases = Purchase.get_purchase_id_descending(current_user.id, page, per_page)
        elif sort_by == 'dateA':
            # Sort by product price in ascending order
            purchases =  Purchase.get_date_ascending(current_user.id, page, per_page)
        elif sort_by == 'completedF':
            # Sort by order completed status (False first)
            purchases =  Purchase.get_completed_status_false_first(current_user.id, page, per_page)
        elif sort_by == 'completedT':
            # Sort by order completed status (True first)
            purchases =  Purchase.get_completed_status_true_first(current_user.id, page, per_page)

        # if(len(purchases)==0):
        #     if page>1:
        #         return redirect(url_for('purchases.purchases', page=page - 1))
        length = len(purchases)
        # Create a list to store purchase details
        purchase_details = []

        for purchase in purchases:
            product = Product.get(purchase.pid)
            if product:
                purchase_detail = {
                    'order_number': purchase.order_number,
                    'purchase_id': purchase.id,
                    'product_name': product.name,
                    'product_price': product.price,
                    'quantity': purchase.quantity,
                    'completed': purchase.completed,
                    'purchase_date': purchase.time_purchased,
                    'product_id':product.id
                }
                purchase_details.append(purchase_detail)

        return render_template('purchases.html', 
                               purchase_history=purchase_details, 
                               page=page, length=length, 
                               per_page=per_page, 
                               active_tab='purchases', sort_by=sort_by)
    else:
        return jsonify({}), 404


@bp.route('/mystorefront/mark/<int:id>', methods=['POST'])
def mark_complete(id):
    if current_user.is_authenticated:
        marked = Purchase.mark_complete(id)
        if marked:
            return redirect(url_for('supply.mystorefront'))
        else:
            return None
