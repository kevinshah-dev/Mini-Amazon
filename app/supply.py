from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange
import datetime
import os

from .models.product import Product
from .models.purchase import Purchase
from .models.supply import ItemforSale
from .models.user import User
from .models.sellerreviews import SellerReviews, SellerReviewsWithName
from .models.category import Category
from flask import flash

from flask import Blueprint
bp = Blueprint('supply', __name__)

PER_PAGE = 5

'''ON PUBLIC PROFILE'''
@bp.route('/public/<int:user_id>', methods=['GET'])
def storefront_by_uid(user_id):
    page = request.args.get('page', default=1, type=int)
    selling = ItemforSale.get_all_by_uid_with_pagination(user_id, page, PER_PAGE) #selling = ItemforSale.get_all_by_uid(user_id)
    total_selling = ItemforSale.get_all_by_uid(user_id)

    product_details = []
    for item in selling:
        product_details.append(Product.get(item.pid))
    detailed_selling = zip(selling, product_details)

    user_page = User.get_User(user_id)
    seller_reviews = SellerReviewsWithName.get_reviewsid(user_id, page, PER_PAGE)
    sellerpage = request.args.get('sellerpage', default=1, type=int)

    profile_picture_path = f'/home/ubuntu/mini-amazon-skeleton/app/static/img/profilePics/{user_id}.png'
    profile_picture_exists = os.path.exists(profile_picture_path)

    if(not profile_picture_exists):
        profile_picture_path = f'img/profilePics/defaultPic.png'
    else:
        profile_picture_path = f'img/profilePics/{user_id}.png'

    #visualization
    pop_prods = Purchase.get_five_pop(user_id)
    Ydata = []
    Xdata = []
    for prod in pop_prods:
        Ydata.append(prod.purchase_count)
        Xdata.append(Product.get(prod.pid).name.capitalize())
    chart_info = zip(Xdata,Ydata)
    
    # for navbar
    active_tab=''
    if current_user.is_authenticated and user_id == current_user.id:
        active_tab='public_profile'
    return render_template('userpublic.html',
                            user_page=user_page,
                            items_for_sale=detailed_selling,
                            page=page, seller_reviews=seller_reviews,
                            sellerpage=sellerpage, 
                            profile_picture_path= profile_picture_path,
                            per_page=PER_PAGE,total_selling=len(total_selling),
                            chart_info=chart_info, active_tab=active_tab)

@bp.route('/mystorefront', methods=['GET', 'POST'])
def mystorefront():
    # find the products current user is selling:
    if current_user.is_authenticated:

        page_selling = request.args.get('page_selling', default=1, type=int)
        page_order = request.args.get('page_order', default=1, type=int)
        selling = ItemforSale.get_all_by_uid_with_pagination(current_user.id, page_selling, PER_PAGE) #selling = ItemforSale.get_all_by_uid(user_id)
        orders = Purchase.get_all_by_sid_page(current_user.id, page_order, PER_PAGE)

        total_selling = ItemforSale.get_all_by_uid(current_user.id)
        total_orders = Purchase.get_all_by_sid(current_user.id)

        product_details = []
        for item in selling: 
            product_details.append(Product.get(item.pid))
        detailed_selling = zip(selling, product_details)

        buyer = []
        item_details = []
        for order in orders:
            buyer.append(User.get(order.uid))
            item_details.append(Product.get(order.pid))
        detailed_order = zip(orders,buyer,item_details)
         
        #to get products added by this user
        added_products = Product.get_added(current_user.id)
        categories = Category.get_category_names()
        return render_template('supply.html', orders=detailed_order,
            items_for_sale=detailed_selling, page_selling=page_selling, page_order=page_order,
            added_products=added_products, categories=categories,
            per_page=PER_PAGE,total_selling=len(total_selling),
            total_orders=len(total_orders), active_tab='storefront')

# STOREFRONT IF FILTERING ORDERS !!!!!!!
@bp.route('/ordersearch', methods=['POST','GET'])
def ordersearch():
    # get from URL
    if current_user.is_authenticated:
        page_selling = request.args.get('page_selling', default=1, type=int)
        page_order = request.args.get('page_order', default=1, type=int)

        selling = ItemforSale.get_all_by_uid_with_pagination(current_user.id, page_selling, PER_PAGE)

        # get from form
        fulfilled = request.form.getlist('fulfilled')
        search_str = request.form.get('search_str')
        if request.args.getlist('fulfilled'):
            fulfilled = request.args.getlist('fulfilled')
        if request.args.get('search_str'):
            search_str = request.args.get('search_str')

        orders = Purchase.get_sid_search_page(current_user.id, page_order, PER_PAGE, fulfilled, search_str)
        all_filtered_orders = Purchase.get_sid_search_all(current_user.id,fulfilled, search_str)
        num_filt_orders = len(all_filtered_orders)

        product_details = []
        for item in selling:
            product_details.append(Product.get(item.pid))
        detailed_selling = zip(selling, product_details)

        buyer = []
        item_details = []
        for order in orders:
            buyer.append(User.get(order.uid))
            item_details.append(Product.get(order.pid))
        detailed_order = zip(orders,buyer,item_details)

        total_selling = ItemforSale.get_all_by_uid(current_user.id)
        total_orders = Purchase.get_all_by_sid(current_user.id)

        #to get products added by this user
        added_products = Product.get_added(current_user.id)
        categories = Category.get_category_names()
        
        return render_template('supply.html', orders=detailed_order,
            items_for_sale=detailed_selling, page_selling=page_selling, page_order=page_order, 
            added_products=added_products, categories=categories,
            per_page=PER_PAGE, total_orders=num_filt_orders,
            total_selling=len(total_selling), active_tab='storefront')


@bp.route('/mystorefront/addinv', methods=['POST'])
def addInv():
    #page = request.args.get('page', default=1, type=int)
    if current_user.is_authenticated:
        new_pid = int(request.form["pid"])
        quantity = int(request.form["quantity"])
        try:
            Product.get(new_pid)
            price = Product.get(new_pid).price 
            add = ItemforSale.addtoInv(current_user.id, new_pid, quantity)
            prod_name = Product.get(new_pid).name
            flash(f'Successfully added {prod_name} to inventory', 'add_inv_success')
        except Exception as e:
            flash('Not a valid PID', 'add_inv')
        return redirect(url_for('supply.mystorefront'))
        #return render_template('supply.html', items_for_sale=selling, page=page)


@bp.route('/mystorefront/edit/<int:pid>', methods=['POST'])
def updateQ(pid):
    page = request.args.get('page', default=1, type=int)
    if current_user.is_authenticated:
        new_q = int(request.form["new_q"])
        edit = ItemforSale.update_q(current_user.id, pid, new_q)
        return redirect(url_for('supply.mystorefront', page=page))

@bp.route('/mystorefront/delete/<int:pid>', methods=['POST'])
def deleteInv(pid):
    if current_user.is_authenticated:
        page = request.args.get('page', default=1, type=int)
        success = ItemforSale.delete_item(current_user.id, pid)
        if success:
            prod_name = Product.get(pid).name
            flash(f'Successfully deleted {prod_name} from inventory', 'delete_success')
            return redirect(url_for('supply.mystorefront', page=page))
        else:
            return None


@bp.route('/addproduct', methods=['POST'])
def add_product():
    name = request.form["name"]
    price = float(request.form["price"])
    category = request.form["category"]
    description = request.form["description"]
    image = request.files['file']
    if image and allowed_file(image.filename):
        new_product = Product.add_product(current_user.id, name, price, category, description)
        if new_product != None:
            filename = str(new_product) + ".png"
            directory = '/home/ubuntu/mini-amazon-skeleton/app/static/img/products'
            try:
                image.save(os.path.join(directory, filename))
                print(f"Image saved successfully at {os.path.join(directory, filename)}")
            except Exception as e:
                print(f"Error while saving the image: {str(e)}")
            return redirect(url_for('product.product', id=new_product))
        else: return redirect(url_for('index.index'))
    else:
        return redirect(url_for('index.index'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png'}

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()]) 
    price = DecimalField('Price', validators=[DataRequired(), NumberRange(min=0, max=None, message='Price must be a non-negative number with up to 2 decimal places')])
    category = SelectField('Category', choices=[], validators=[DataRequired()]) 
    description = StringField('Product Description', validators=[DataRequired()]) 
    submit = SubmitField('Update Product')


@bp.route('/editproduct/<int:pid>', methods=['POST'])
def edit_product(pid):
    current_product = Product.get(pid)
    form = ProductForm()
    # populate category options
    form.category.choices = [(category, category) for category in Category.get_category_names()]
    cat_height = len(Category.get_category_names())
    if form.validate_on_submit():
        result = Product.update_product(pid,
            name = form.name.data,
            price =  form.price.data, 
            category = form.category.data, 
            description = form.description.data)        
        return redirect(url_for('supply.mystorefront'))
    
    # populate current product info
    current_product = Product.get(pid)
    form.name.data = current_product.name
    form.price.data = current_product.price
    form.category.data = current_product.category
    form.description.data = current_product.description
    return render_template('updateProduct.html',
                           title='Update', 
                           form=form, 
                           pid=pid, 
                           cat_height=cat_height,
                           active_tab='')