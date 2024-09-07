from werkzeug.security import generate_password_hash
import csv
from faker import Faker
from datetime import datetime

num_users = 100
max_balance = 100

num_categories = 10
num_products = 2000
num_added_products = 100

num_purchases = 2500
max_quanity_bought = 10

num_supply = 2000
max_supply = 100
max_price = 500

num_carts = 50
max_quanity_cart = 10

# number of reviews is same as number of users for simplicity
# num_product_reviews = 100
# num_seller_reviews = 100
start_date = datetime(2000,1,1)

Faker.seed(0)
fake = Faker()

def get_csv_writer(f):
    return csv.writer(f, dialect='unix')

def gen_users(num_users):
    with open('Users.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Users...', end=' ', flush=True)
        for uid in range(num_users):
            if uid % 10 == 0:
                print(f'{uid}', end=' ', flush=True)
            profile = fake.profile()
            email = profile['mail']
            plain_password = f'pass{uid}'
            password = generate_password_hash(plain_password)
            name_components = profile['name'].split(' ')
            firstname = name_components[0]
            lastname = name_components[-1]
            address = fake.address()
            balance = f'{str(fake.random_int(max=max_balance))}.{fake.random_int(max=99):02}'
            writer.writerow([uid, email, password, firstname, lastname, address, balance])
        print(f'{num_users} generated')
    return

# constraint, category names should be unique
unique_categories = set()
def gen_categories(num_categories):
    categories = []
    with open('Categories.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Categories...', end=' ', flush=True) 
        for category in range(num_categories):
            name = fake.word()
            while name in unique_categories:
                name = fake.word()
            unique_categories.add(name)
            description = fake.sentence()
            categories.append(name)
            writer.writerow([name, description])
        print(f'{num_categories} generated')
    return categories

def gen_products(num_products, categories_list):
    available_pids = []
    with open('Products.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Products...', end=' ', flush=True)
        for pid in range(1, num_products+1):
            if pid % 100 == 0:
                print(f'{pid}', end=' ', flush=True)
            name = fake.sentence(nb_words=4)[:-1]
            price = f'{str(fake.random_int(max=max_price))}.{fake.random_int(max=99):02}'
            available = fake.random_element(elements=('true', 'false'))
            if available == 'true':
                available_pids.append(pid)
            category = fake.random_element(elements=categories_list)
            description = fake.sentence()                               
            writer.writerow([pid, name, price, available, category, description])
        print(f'{num_products} generated; {len(available_pids)} available')
    return available_pids

# Constraint: can't have multiple people adding the same product
unique_pid = set()
def gen_added_products(num_added_products, available_pids):
    with open('AddedProducts.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('AddedProducts...', end=' ', flush=True)
        for id in range(num_added_products):
            uid = fake.random_int(min=0, max=num_users-1)
            pid = fake.random_element(elements=available_pids)
            while pid in unique_pid:
                pid = fake.random_element(elements=available_pids)
            unique_pid.add(pid)
            writer.writerow([uid, pid])
        print(f'{num_added_products} generated')
    return

def gen_purchases(num_purchases, available_pids):
    with open('Purchases.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Purchases...', end=' ', flush=True)
        for id in range(num_purchases):
            if id % 100 == 0:
                print(f'{id}', end=' ', flush=True)
            uid = fake.random_int(min=0, max=num_users-1)
            pid = fake.random_element(elements=available_pids)

            #specified time frame
            start_date = datetime(2020, 1, 1)
            end_date = datetime.now()

            # Generate a random date and time within the specified range
            time_purchased = fake.date_time_between(start_date=start_date, end_date=end_date)

            sid = fake.random_int(min=0, max=num_users-1)
            same_id = (sid == uid)
            while same_id: # ensure that the buyer and seller aren't the same
                sid = fake.random_int(min=0, max=num_users-1)
                same_id = (sid == uid)
            quantity = fake.random_int(min=1, max=max_quanity_bought)
            completed = fake.random_element(elements=('true', 'false'))
            order_number = fake.random_int(min=0, max=999) # just for ordering purposes
            writer.writerow([id, uid, pid, time_purchased, sid, quantity, completed, order_number])
        print(f'{num_purchases} generated')
    return

# Constraint, cannot have the same (uid, pid) pair
unique_pairs_supply = set()
def gen_supply(num_supply, available_pids):
    with open('Supply.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Supply...', end=' ', flush=True)
        for i in range (num_supply):
            uid = fake.random_int(min=0, max=num_users-1)
            pid = fake.random_element(elements=available_pids)
            pair = (uid, pid)
            while pair in unique_pairs_supply:
                uid = fake.random_int(min=0, max=(num_users-1))
                pid = fake.random_element(elements=available_pids)
                pair = (uid, pid)
            unique_pairs_supply.add(pair)
            #seller_price = f'{str(fake.random_int(max=max_price))}.{fake.random_int(max=99):02}'
            seller_inventory = fake.random_int(min=1, max=max_supply)
            writer.writerow([uid, pid, seller_inventory])
        print(f'{num_supply} generated')
    return

def gen_carts(num_carts, available_pids): 
    with open('Carts.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Carts...', end=' ', flush=True)
        for i in range(num_carts):
            if i % 10 == 0:
                print(f'{i}', end=' ', flush=True)
            uid = fake.random_int(min=0, max=num_users-1)
            pid = fake.random_element(elements=available_pids)
            sid = fake.random_int(min=0, max=num_users-1)
            quantity = fake.random_int(min=1, max=max_quanity_cart)
            savedforlater = fake.random_element(elements=('true', 'false'))
            writer.writerow([uid, pid, sid, quantity,savedforlater])
        print(f'{num_carts} generated')
    return 

# Need to ensure a user only reviews any given product once
def gen_product_reviews(available_pids):
    with open('ProductReviews.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('ProductReviews...', end=' ', flush=True)
        for i in range(num_users): # easy workaround is to only generate one product review per user
            if i % 10 == 0:
                print(f'{i}', end=' ', flush=True)
            uid = fake.random_int(min=0, max=num_users-1)
            pid = fake.random_element(elements=available_pids)
            review = fake.sentence()
            rating = fake.random_int(min=1, max=5)
            review_time = fake.date_time_between(start_date=start_date, end_date=datetime.now())
            writer.writerow([uid, pid, review, rating, review_time])
        print(f'{num_users} generated')  
    return

# Need to ensure a user only reviews any given seller once
def gen_seller_reviews(num_users):
    with open('SellerReviews.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('SellerReviews...', end=' ', flush=True)
        for i in range(num_users): # easy workaround is to only generate one seller review per user
            if i % 10 == 0:
                print(f'{i}', end=' ', flush=True)
            uid = fake.random_int(min=0, max=num_users-1)
            sid = i
            review = fake.sentence()
            rating = fake.random_int(min=1, max=5)
            review_time = fake.date_time_between(start_date=start_date, end_date=datetime.now())
            writer.writerow([uid, sid, review, rating, review_time])
        print(f'{num_users} generated')  
    return

gen_users(num_users)
categories_list = gen_categories(num_categories)
available_pids = gen_products(num_products, categories_list)
gen_added_products(num_added_products, available_pids)
gen_purchases(num_purchases, available_pids)
gen_supply(num_supply, available_pids)
gen_carts(num_carts, available_pids)
gen_product_reviews(available_pids)
gen_seller_reviews(num_users)
