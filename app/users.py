from decimal import Decimal
import os
from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from .models.user import User
from .models.productreviews import ProductReviews, ExtendedProductReviews
from .models.sellerreviews import SellerReviews
from sqlalchemy.exc import IntegrityError
import datetime as dt
from .models.purchase import Purchase


from flask import Blueprint
bp = Blueprint('users', __name__)
REVIEWS_PER_PAGE = 5

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_auth(form.email.data, form.password.data)
        if user is None:
            flash('Invalid email or password')
            return redirect(url_for('users.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index.index')

        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form, active_tab='login')


class RegistrationForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(),
                                       EqualTo('password')])
    address = StringField('Address')
    submit = SubmitField('Register')

    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError('Already a user with this email.')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.register(
            form.email.data,
            form.password.data,
            form.firstname.data,
            form.lastname.data,
            form.address.data  # Include the address data in the registration
        ):
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form, active_tab='login')



@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index.index'))

@bp.route('/public_profile/<int:user_id>')
def public_profile(user_id):
    # Get the user from the database using the provided user_id
    user = User.get_User(user_id)

    if user:
        # Render the public profile template with user information
        return render_template('userpublic.html', user_page=user, page = 1, sellerpage = 1,
                               uid=user_id, active_tab='public_profile')
    else:
        # Handle case where user with provided ID doesn't exist
        # You might want to redirect to an error page or show a message
        #return render_template('error.html', message='User not found')
        print("NOT FOUND")


class UserProfileForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(),
                                       EqualTo('password')])
    address = StringField('Address')
    submit = SubmitField('Update Profile')


@bp.route('/privateProfile')
def privateProfile():
    # print(current_user.email)  # Debugging statement
    # print(current_user.firstname)  # Debugging statement
    # print(current_user.lastname)  # Debugging statement
    page = request.args.get('page', default=1, type=int)
    reviews = ExtendedProductReviews.get_reviewsid(current_user.id, page, REVIEWS_PER_PAGE)
    sellerreviews = SellerReviews.get_reviewsuid(current_user.id)
    length = len(reviews)
    # Check if the profile picture exists
    profile_picture_path = f'/home/ubuntu/mini-amazon-skeleton/app/static/img/profilePics/{current_user.id}.png'
    profile_picture_exists = os.path.exists(profile_picture_path)

    return render_template('userprivate.html', reviews=reviews, 
                           page=page, profile_picture_exists=profile_picture_exists,
                           per_page= REVIEWS_PER_PAGE, length=length,
                           active_tab='profile', sellerreviews=sellerreviews)

@bp.route('/update_profile_picture', methods=['GET', 'POST'])
@login_required
def update_profile_picture():
    if 'profile_picture' not in request.files:
            flash('No file part', 'update')
            return redirect(url_for('users.privateProfile'))

    file = request.files['profile_picture']

    # If the user does not select a file, the browser submits an empty file without a filename
    if file.filename == '':
        flash('No selected file', 'update')
        return redirect(url_for('users.privateProfile'))

    # Save the uploaded file to the img/profilePics folder
    filename = f'{current_user.id}.png'
    file.save(os.path.join('app/static/img/profilePics/', filename))

    # Update the user's profile picture filename in the database
    current_user.profile_picture = filename

    flash('Profile picture updated successfully', 'updatePic')
    return redirect(url_for('users.privateProfile'))

@bp.route('/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    form = UserProfileForm()

    if form.validate_on_submit():
        #print("Updating")
        result =User.updateInfo(current_user,
            email = form.email.data,
            firstname = form.firstname.data,
            lastname = form.lastname.data,
            password = form.password.data,
            address = form.address.data)
        
        if(result==0):
            flash('Your profile has been updated.', 'update')
        else:
            flash('Failed to update information: The email you entered is associated with a different account. Please try again.','update')

        return redirect(url_for('users.privateProfile'))
    form.email.data = current_user.email
    form.firstname.data = current_user.firstname
    form.lastname.data = current_user.lastname
    form.address.data = current_user.address

    return render_template('updateProfile.html',title='Update', form=form, active_tab='')

@bp.route('/increaseBalance', methods=['POST'])
def increaseBalance():
    # get all k most expensive products for sale:
    if request.method == "POST": 
        addToBalance = Decimal(request.form["k"])
       
    # find the products current user has bought:
    if current_user.is_authenticated:        
        User.increaseBalance(current_user,addToBalance)
        flash(f'Successfully added ${addToBalance} to balance!','balance')

    return redirect(url_for('users.privateProfile'))

@bp.route('/withdrawBalance', methods=['POST'])
def withdrawBalance():
    # get all k most expensive products for sale:
    if request.method == "POST": 
        removeFromBalance = Decimal(request.form["k"])
    
    # find the products current user has bought:
    if current_user.is_authenticated:        
        passed = User.withdrawBalance(current_user,removeFromBalance)

    if passed == -1:
        flash('Insufficient funds. You cannot withdraw more than your current balance.', 'balance')
    else:
        flash(f'Success you have successfully withdrawn ${removeFromBalance}!', 'balance')

    return redirect(url_for('users.privateProfile'))

#Add seller review page
@bp.route('/addsellerreviewpage/<int:uid>/<int:sid>', methods=['GET'])
def addSellerReviewPage(uid, sid):
    return render_template('addsellerreview.html', uid=uid, sid=sid)

@bp.route('/addsellerreview/<int:uid>/<int:sid>', methods=['POST'])
def addSellerReview(uid, sid):
    if current_user.is_authenticated:
        if uid == sid:
            flash("You cannot review yourself!")
            return render_template('addsellerreview.html', uid=uid, sid=sid)
        if Purchase.is_valid_review(uid, sid) == False:
            flash("You have not purchased from this Seller!")
            return render_template('addsellerreview.html', uid=uid, sid=sid)
        try:
            review = request.form["reviewText"]
            rating = request.form["rating"]
            time = dt.datetime.now()
            formattedtime = time.strftime("%Y-%m-%d %H:%M:%S")
            SellerReviews.insert_seller_review(uid, sid, review, rating, formattedtime)
            return redirect(url_for('users.privateProfile'))
        except IntegrityError:
            flash("You have already reviewed this Seller!")
            return render_template('addsellerreview.html', uid=uid, sid=sid)
