from flask import render_template, request, flash
from flask import redirect, url_for
from flask_login import current_user
from datetime import datetime, timedelta
import datetime as dt
from flask import jsonify
from .models.cart import CartItem
from .models.user import User
from .models.purchase import Purchase
from .models.supply import ItemforSale
from .models.order import Order

from flask import Blueprint
bp = Blueprint('cart', __name__)

@bp.route('/cart')
def cart():
    # find the products the user has added in their cart:
    if not current_user.is_authenticated:
        print("in here")
        return redirect(url_for('users.login'))
    if current_user.is_authenticated:
        incart = CartItem.Cartforuid(current_user.id)
        total = 0
        for item in incart:
            total += item.price*item.quantity
        savedlist = CartItem.savedListforuid(current_user.id)
    else:
        incart = None
    
    return render_template('cart.html',
                      items=incart, totalprice= total, savedlist = savedlist, active_tab='cart')


@bp.route('/cart/add/<int:product_id>/<int:seller_id>', methods=['POST'])
def add(product_id, seller_id):
    if current_user.is_authenticated:
        quantity = int(request.form["quantity"])
        add = CartItem.addtoCart(current_user.id, product_id, seller_id, quantity)
        if add:
            return redirect(url_for('cart.cart'))
        else:
            return redirect(url_for('index.index'))

@bp.route('/cart/change/<int:product_id>/<int:seller_id>', methods = ['POST'])
def change(product_id,seller_id):
    if current_user.is_authenticated:
        quantity = int(request.form["quantity"])
        CartItem.changeinCart(current_user.id, product_id, seller_id, quantity)
        return redirect(url_for('cart.cart'))

@bp.route('/cart/change/<int:product_id>/<int:seller_id>', methods = ['POST', 'GET'])
def delete(product_id,seller_id):
    if current_user.is_authenticated:
        quantity =0
        CartItem.changeinCart(current_user.id, product_id, seller_id, quantity)
        return redirect(url_for('cart.cart'))

@bp.route('/cart/order', methods = ['POST', 'GET'])
def order():
    if current_user.is_authenticated:
        incart = CartItem.Cartforuid(current_user.id)
        total = 0
        for item in incart:
            total += item.price*item.quantity
        balance = (User.get(current_user.id)).balance
        if total <= balance:
            newtotal = 0
            purchase_count = 0
            old_num = Purchase.get_max_order_num()[0]
            if old_num:
                order_number = old_num + 1 
            else:
                order_number = 1
            for item in incart:
                amount_available = ItemforSale.get(item.sid, item.pid).seller_inventory
                if(amount_available >= item.quantity):
                    # print(item.name, amount_available, item.quantity)
                    purchase_item = Purchase.add_purchase(current_user.id, item.pid, item.sid, item.quantity, order_number)
                    decrease_supply = ItemforSale.decrease_inventory(item.sid, item.pid, item.quantity)
                    newtotal += item.price*item.quantity
                    delete_incart = CartItem.changeinCart(current_user.id, item.pid, item.sid,0)
                    increase_seller_balance = User.increase_seller_balance(item.sid, item.price*item.quantity)
                    purchase_count += 1
                else:
                    flash("{} of {} is/are not available from seller {} {}. Could not purchase in this order.".format(item.quantity, item.name, item.seller_firstname, item.seller_lastname))
            decrease_balance = User.withdrawBalance(current_user,newtotal)
            if purchase_count>0:
                return redirect(url_for('cart.orderpage', uid = current_user.id, ordernum = order_number))
            else:
                return redirect(url_for('cart.cart'))
        else:
            flash("Not enough money in balance for this purchase!")
            return redirect(url_for('cart.cart'))


@bp.route('/orderpage/<int:uid>/<int:ordernum>', methods = ['POST', 'GET'])
def orderpage(uid, ordernum):
    items = Order.get_order_items(uid, ordernum)
    fulfilled = 1
    total = 0
    for item in items:
        total += item.price*item.quantity
        if item.completed == False:
            fulfilled = 0
    return render_template('orderpage.html',
                           ordernum=ordernum, 
                           items = items, 
                           total = total, 
                           fulfilled=fulfilled,
                           active_tab='')

@bp.route('/cart/movetosaved/<int:product_id>/<int:seller_id>/<int:quantity>', methods = ['POST', 'GET'])
def movetoSavedList(product_id,seller_id, quantity):
    if current_user.is_authenticated:
        addtolist = CartItem.addtoSavedList(current_user.id, product_id, seller_id, quantity)
        removefromcart = CartItem.changeinCart(current_user.id, product_id, seller_id, 0)
    return redirect(url_for('cart.cart'))

@bp.route('/cart/changesaved/<int:product_id>/<int:seller_id>', methods = ['POST', 'GET'])
def changeinSavedList(product_id,seller_id):
    if current_user.is_authenticated:
        quantity = int(request.form["quantity"])
        CartItem.changeinSavedList(current_user.id, product_id, seller_id, quantity)
        return redirect(url_for('cart.cart'))

@bp.route('/cart/deletesaved/<int:product_id>/<int:seller_id>', methods = ['POST', 'GET'])
def deleteinSavedList(product_id,seller_id):
    if current_user.is_authenticated:
        quantity =0
        CartItem.changeinSavedList(current_user.id, product_id, seller_id, quantity)
        return redirect(url_for('cart.cart'))

@bp.route('/cart/movetocart/<int:product_id>/<int:seller_id>/<int:quantity>', methods = ['POST', 'GET'])
def movetoCart(product_id,seller_id, quantity):
    if current_user.is_authenticated:
        addtolist = CartItem.addtoCart(current_user.id, product_id, seller_id, quantity)
        removefromcart = CartItem.changeinSavedList(current_user.id, product_id, seller_id, 0)
    return redirect(url_for('cart.cart'))

@bp.route('/cart/addsaved/<int:product_id>/<int:seller_id>', methods=['POST', 'GET'])
def addtoSavedList(product_id, seller_id):
    if current_user.is_authenticated:
        quantity = 1
        add = CartItem.addtoSavedList(current_user.id, product_id, seller_id, quantity)
        if add:
            return redirect(url_for('cart.cart'))
        else:
            return redirect(url_for('index.index'))