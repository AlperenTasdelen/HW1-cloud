from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_pymongo import PyMongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
from datetime import datetime
from pymongo import DESCENDING
from flask import flash
import smtplib
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import random

import json

app = Flask(__name__)

app.secret_key = 'mysecret'

uri = "mongodb+srv://regular_user:regular_user@cengdencluster.jvmzjb0.mongodb.net/?retryWrites=true&w=majority&appName=CENGdenCluster"
client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client['CENGDENdatabase']
users_collection = db['users']
products_collection = db['products']

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    username = session.get('username')
    if not username:
        flash('You must be logged in to view your profile', 'error')
        return render_template('signin.html')
    
    user = users_collection.find_one({'username': username})
    products = products_collection.find()
    products2 = products_collection.find()
    return render_template('profile.html', user=user, products=products, products2=products2, username = session.get('username'))

@app.route('/signin')
def signin():
    return render_template('signin.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Handle form submission (registration logic)
        # This is where you would process the submitted form data and register the user
        # Once registered, you may redirect the user to another page (e.g., the sign-in page)
        # Process form submission
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        # Add user to the users array

        if not email.endswith('@ceng.metu.edu.tr'):
            flash('Email must be in the format example@ceng.metu.edu.tr', 'error')
            return redirect(url_for('register'))

        if users_collection.find_one({'$or': [{'email': email}]}):
            flash('Email already exists, please use a different email', 'error')
            return redirect(url_for('register'))
        
        #TODO: send email to user for verification

        verification_code = random.randint(100000, 999999)

        message = Mail(
            from_email = 'e2521987@ceng.metu.edu.tr',
            to_emails = email,
            subject = 'CENGden Registration',
            html_content = f'Your verification code is {verification_code}. Please enter this code to complete your registration.')
        
        try:
            sg = SendGridAPIClient('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')
            response = sg.send(message)
            # print(response.status_code)
            # print(response.body)
            # print(response.headers)
        except Exception as e:
            print(e)

        return render_template('verification.html',username=username, password=password, phone=phone, email=email, verification_code=verification_code, methods = ['POST'])
        # return redirect(url_for('verify', email=email, verification_code=verification_code))
    return render_template('register.html')

@app.route('/verify/<string:username>/<string:password>/<string:email>/<string:phone>/<string:verification_code>', methods=['POST'])
def verify(username, password, email, phone, verification_code):
    if request.method == 'POST':
        code = request.form['verification']
        if code == verification_code:
            user_data = {
                'username': username,
                'password': password,
                'email': email,
                'phone': phone,
                'isAdmin': False
            }
            users_collection.insert_one(user_data)
            return redirect(url_for('signin'))
        else:
            flash('Invalid verification code', 'error')
            return redirect(url_for('register'))


@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    user = users_collection.find_one({'email': email, 'password': password})
    if user:
        # User found, redirect to homepage or dashboard
        session['username'] = user['username']
        return redirect(url_for('index'))
    else:
        flash('Invalid email or password', 'error')
        return redirect(url_for('signin'))

@app.route('/')
def index():
    username = session.get('username')
    session['username'] = username
    return render_template('index.html')

@app.route('/products')
def products():
    category = request.args.get('category')
    query = {}  # Define a query to filter products based on category

    if category:
        if category != 'all':
            query['product_type'] = category

    products = products_collection.find(query).sort('created_at', DESCENDING)
    return render_template('products.html', products=products, username = session.get('username'))

@app.route('/user_list')
def user_list():
    users = users_collection.find({'isAdmin': False})
    return render_template('user_list.html', users=users)

@app.route('/display_user/<string:username>', methods=['GET'])
def display_user(username):
    user = users_collection.find_one({'username': username})
    return render_template('display_user.html', user=user)

@app.route('/edit_user/<string:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if request.method == 'POST':
        # Retrieve form data
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Update user data
        users_collection.update_one({'username': username}, {'$set': {
            'username': username,
            'email': email,
            'password': password
        }})

        return redirect(url_for('/user_list'))

    user = users_collection.find_one({'username': username})
    return render_template('edit_user.html', user=user)

@app.route('/edit_user_own/<string:user_id>', methods=['GET', 'POST'])
def edit_user_own(user_id):
    if request.method == 'POST':
        # Retrieve form data
        # user = users_collection.find_one({'_id': ObjectId(user_id)})
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Update user data
        users_collection.update_one({'_id': ObjectId(user_id)}, {'$set': {
            'username': username,
            'email': email,
            'password': password
        }})

        return redirect(url_for('signin'))

    return redirect(url_for('index'))

@app.route('/delete_user/<string:username>', methods=['POST'])
def delete_user(username):
    users_collection.delete_one({'username': username})
    products_collection.delete_many({'owner': username})
    return redirect(url_for('user_list'))

@app.route('/delete_user_own/<string:username>', methods=['POST'])
def delete_user_own(username):
    users_collection.delete_one({'username': username})
    products_collection.delete_many({'owner': username})
    return redirect(url_for('logout'))

@app.route('/new_item', methods=['GET', 'POST'])
def new_item():
    username = request.args.get('username')
    if not username:
        pass
    
    if request.method == 'POST':
        # Retrieve item information from the form
        item_name = request.form['item_name']
        description = request.form['description']
        price = float(request.form['price'])  # Convert to float if necessary
        
        # Insert the new item into the database
        item_data = {
            'username': username,
            'item_name': item_name,
            'description': description,
            'price': price
        }
        db.items.insert_one(item_data)
        
        # Redirect to the profile page after adding the item
        return redirect(url_for('profile'))
    
    return render_template('new_item.html', username=username)

@app.route('/edit_item', methods=['GET', 'POST'])
def edit_item():
    username = request.args.get('username')
    
    if not username:
        pass
    
    products = products_collection.find({'owner': username})
    return render_template('edit_item.html', username=username, products=products)

@app.route('/add_vehicle', methods=['POST'])
def add_vehicle():
    if request.method == 'POST':
        # Retrieve form data
        product_type = "vehicle"
        title = request.form['title_vehicle']
        vehicle_type = request.form['type_vehicle']
        brand = request.form['brand_vehicle']
        model = request.form['model_vehicle']
        year = int(request.form['year_vehicle'])
        color = request.form['color_vehicle']
        engine_displacement = request.form['engine_displacement_vehicle']
        fuel_type = request.form['fuel_type_vehicle']
        transmission_type = request.form['transmission_type_vehicle']
        mileage = float(request.form['mileage_vehicle'])
        price = float(request.form['price_vehicle'])
        image = request.form['image_vehicle']
        description = request.form['description_vehicle']
        isRegularAllowed = request.form.get('visible_vehicle')

        if not isRegularAllowed:
            isRegularAllowed = False
        else:
            isRegularAllowed = True

        if(vehicle_type == 'Electric Car'):
            battery_capacity = request.form['battery_capacity']
            range = request.form['range']

        if(vehicle_type == 'Caravan'):
            bed_capacity = request.form['bed_capacity']
            water_tank_capacity = request.form['water_tank_capacity']

        if(vehicle_type == 'Truck'):
            payload_capacity = request.form['payload_capacity']
        
        # Prepare item data
        vehicle_data = {
            'owner': session.get('username'),
            'product_type': product_type,
            'title': title,
            'type': vehicle_type,
            'brand': brand,
            'model': model,
            'year': year,
            'color': color,
            'engine_displacement': engine_displacement,
            'fuel_type': fuel_type,
            'transmission_type': transmission_type,
            'mileage': mileage,
            'price': price,
            'image': image,
            'description': description,
            'isRegularAllowed': isRegularAllowed,
            'isFeatured': False,
            'favoriteList': [],
            'isActivated': True,
            'created_at': datetime.now(),
            'battery_capacity': battery_capacity if vehicle_type == 'Electric Car' else '',
            'range': range if vehicle_type == 'Electric Car' else '',
            'bed_capacity': bed_capacity if vehicle_type == 'Caravan' else '',
            'water_tank_capacity': water_tank_capacity if vehicle_type == 'Caravan' else '',
            'payload_capacity': payload_capacity if vehicle_type == 'Truck' else ''
        }
        
        # Insert item into MongoDB
        db.products.insert_one(vehicle_data)

        # Redirect to the profile page or any other page as needed
        return redirect(url_for('profile'))

@app.route('/add_computer', methods=['POST'])
def add_computer():
    if request.method == 'POST':
        # Retrieve form data
        product_type = "computer"
        title = request.form['title_computer']
        computer_type = request.form['type_computer']
        brand = request.form['brand_computer']
        model = request.form['model_computer']
        year = int(request.form['year_computer'])
        processor = request.form['processor_computer']
        ram = request.form['ram_computer']
        storage = request.form['storage_computer']
        graphics_card = request.form['graphics_card_computer']
        operating_system = request.form['operating_system_computer']
        price = float(request.form['price_computer'])
        image = request.form['image_computer']
        description = request.form['description_computer']
        isRegularAllowed = request.form.get('visible_computer')

        if not isRegularAllowed:
            isRegularAllowed = False
        else:
            isRegularAllowed = True

        # Prepare item data
        computer_data = {
            'owner': session.get('username'),
            'product_type': product_type,
            'title': title,
            'type': computer_type,
            'brand': brand,
            'model': model,
            'year': year,
            'processor': processor,
            'ram': ram,
            'storage': storage,
            'graphics_card': graphics_card,
            'operating_system': operating_system,
            'price': price,
            'image': image,
            'description': description,
            'isRegularAllowed': isRegularAllowed,
            'isFeatured': False,
            'favoriteList': [],
            'isActivated': True,
            'created_at': datetime.now()
        }

        # Insert item into MongoDB
        db.products.insert_one(computer_data)

        # Redirect to the profile page or any other page as needed
        return redirect(url_for('profile'))

@app.route('/add_phone', methods=['POST'])
def add_phone():
    if request.method == 'POST':
        # Retrieve form data
        product_type = "phone"
        title = request.form['title_phone']
        brand = request.form['brand_phone']
        model = request.form['model_phone']
        year = int(request.form['year_phone'])
        operating_system = request.form['operating_system_phone']
        processor = request.form['processor_phone']
        ram = request.form['ram_phone']
        storage = request.form['storage_phone']
        camera_specifications = request.form['camera_specifications_phone']
        battery_capacity = request.form['battery_capacity_phone']
        price = float(request.form['price_phone'])
        image = request.form['image_phone']
        description = request.form['description_phone']
        isRegularAllowed = request.form.get('visible_phone')

        if not isRegularAllowed:
            isRegularAllowed = False
        else:
            isRegularAllowed = True

        # Prepare item data
        phone_data = {
            'owner': session.get('username'),
            'product_type': product_type,
            'title': title,
            'brand': brand,
            'model': model,
            'year': year,
            'operating_system': operating_system,
            'processor': processor,
            'ram': ram,
            'storage': storage,
            'camera_specifications': camera_specifications,
            'battery_capacity': battery_capacity,
            'price': price,
            'image': image,
            'description': description,
            'isRegularAllowed': isRegularAllowed,
            'isFeatured': False,
            'favoriteList': [],
            'isActivated': True,
            'created_at': datetime.now()
        }

        # Insert item into MongoDB
        db.products.insert_one(phone_data)

        # Redirect to the profile page or any other page as needed
        return redirect(url_for('profile'))

@app.route('/add_private_lesson', methods=['POST'])
def add_private_lesson():
    if request.method == 'POST':
        # Retrieve form data
        product_type = "private-lesson"
        title = request.form['title_private_lesson']
        tutor_name = request.form['tutor_name_private_lesson']
        lessons = request.form['lessons_private_lesson']
        location = request.form['location_private_lesson']
        duration = request.form['duration_private_lesson']
        price = float(request.form['price_private_lesson'])
        image = request.form['image_private_lesson']
        description = request.form['description_private_lesson']
        isRegularAllowed = request.form.get('visible_private_lesson')
        
        if not isRegularAllowed:
            isRegularAllowed = False
        else:
            isRegularAllowed = True

        # Prepare item data
        private_lesson_data = {
            'owner': session.get('username'),
            'product_type': product_type,
            'title': title,
            'tutor_name': tutor_name,
            'lessons': lessons,
            'location': location,
            'duration': duration,
            'price': price,
            'image': image,
            'description': description,
            'isRegularAllowed': isRegularAllowed,
            'isFeatured': False,
            'favoriteList': [],
            'isActivated': True,
            'created_at': datetime.now()
        }

        # Insert item into MongoDB
        db.products.insert_one(private_lesson_data)

        # Redirect to the profile page or any other page as needed
        return redirect(url_for('profile'))

@app.route('/choose_item_type', methods=['POST'])
def choose_item_type():
    item_type = request.form['item_type']
    if item_type == 'vehicle':
        return redirect(url_for('new_vehicle'))
    elif item_type == 'computer':
        return redirect(url_for('new_computer'))
    elif item_type == 'phone':
        return redirect(url_for('new_phone'))
    elif item_type == 'private_lesson':
        return redirect(url_for('new_private_lesson'))
    else:
        # Handle invalid input
        return "Invalid item type selected"

# Route for adding a new product
@app.route('/new_vehicle')
def new_vehicle():
    return render_template('new_vehicle.html')

@app.route('/new_computer')
def new_computer():
    return render_template('new_computer.html')

@app.route('/new_phone')
def new_phone():
    return render_template('new_phone.html')

@app.route('/new_private_lesson')
def new_private_lesson():
    return render_template('new_private_lesson.html')

# Route for editing a product
@app.route('/edit_vehicle/<string:product_id>', methods=['GET', 'POST'])
def edit_vehicle(product_id):
    if(request.method == 'POST'):
        title = request.form['title_vehicle']
        vehicle_type = request.form['type_vehicle']
        brand = request.form['brand_vehicle']
        model = request.form['model_vehicle']
        year = int(request.form['year_vehicle'])
        color = request.form['color_vehicle']
        engine_displacement = request.form['engine_displacement_vehicle']
        fuel_type = request.form['fuel_type_vehicle']
        transmission_type = request.form['transmission_type_vehicle']
        mileage = float(request.form['mileage_vehicle'])
        price = float(request.form['price_vehicle'])
        image = request.form['image_vehicle']
        description = request.form['description_vehicle']
        isRegularAllowed = request.form.get('visible_vehicle')

        if not isRegularAllowed:
            isRegularAllowed = False
        else:
            isRegularAllowed = True
        
        old_price = products_collection.find_one({'_id': ObjectId(product_id)}).get('price')

        products_collection.update_one({'_id': ObjectId(product_id)}, {'$set': {
            'title': title,
            'type': vehicle_type,
            'brand': brand,
            'model': model,
            'year': year,
            'color': color,
            'engine_displacement': engine_displacement,
            'fuel_type': fuel_type,
            'transmission_type': transmission_type,
            'mileage': mileage,
            'price': price,
            'image': image,
            'description': description,
            'isRegularAllowed': isRegularAllowed
        }})

        if(price < old_price):
            favoriteList = products_collection.find_one({'_id': ObjectId(product_id)}).get('favoriteList', [])
            #TODO: Send email to users in favoriteList
            for user in favoriteList:
                user_email = users_collection.find_one({'username': user}).get('email', '')
                message = Mail(
                    from_email = 'e2521987@ceng.metu.edu.tr',
                    to_emails = user_email,
                    subject = 'Price Reduction Alert',
                    html_content = f'The price of the product {title} has been reduced. Check it out on CENGden!')
                try:
                    sg = SendGridAPIClient('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')
                    response = sg.send(message)
                    # print(response.status_code)
                    # print(response.body)
                    # print(response.headers)
                except Exception as e:
                    print(e)
            
        return redirect(url_for('profile'))
    
    vehicle = products_collection.find_one({'_id': ObjectId(product_id)})
    return render_template('edit_vehicle.html', vehicle=vehicle)

@app.route('/edit_computer/<string:product_id>', methods=['GET', 'POST'])
def edit_computer(product_id):
    if(request.method == 'POST'):
        title = request.form['title_computer']
        computer_type = request.form['type_computer']
        brand = request.form['brand_computer']
        model = request.form['model_computer']
        year = int(request.form['year_computer'])
        processor = request.form['processor_computer']
        ram = request.form['ram_computer']
        storage = request.form['storage_computer']
        graphics_card = request.form['graphics_card_computer']
        operating_system = request.form['operating_system_computer']
        price = float(request.form['price_computer'])
        image = request.form['image_computer']
        description = request.form['description_computer']
        isRegularAllowed = request.form.get('visible_computer')

        if not isRegularAllowed:
            isRegularAllowed = False
        else:
            isRegularAllowed = True

        old_price = products_collection.find_one({'_id': ObjectId(product_id)}).get('price', 0)

        products_collection.update_one({'_id': ObjectId(product_id)}, {'$set': {
            'title': title,
            'type': computer_type,
            'brand': brand,
            'model': model,
            'year': year,
            'processor': processor,
            'ram': ram,
            'storage': storage,
            'graphics_card': graphics_card,
            'operating_system': operating_system,
            'price': price,
            'image': image,
            'description': description,
            'isRegularAllowed': isRegularAllowed
        }})

        if(price < old_price):
            favoriteList = products_collection.find_one({'_id': ObjectId(product_id)}).get('favoriteList', [])
            for user in favoriteList:
                user_email = users_collection.find_one({'username': user}).get('email', '')
                message = Mail(
                    from_email = 'e2521987@ceng.metu.edu.tr',
                    to_emails = user_email,
                    subject = 'Price Reduction Alert',
                    html_content = f'The price of the product {title} has been reduced. Check it out on CENGden!')
                try:
                    sg = SendGridAPIClient('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')
                    response = sg.send(message)
                    # print(response.status_code)
                    # print(response.body)
                    # print(response.headers)
                except Exception as e:
                    print(e)

        return redirect(url_for('profile'))
    computer = products_collection.find_one({'_id': ObjectId(product_id)})
    return render_template('edit_computer.html', computer=computer)

@app.route('/edit_phone/<string:product_id>', methods=['GET', 'POST'])
def edit_phone(product_id):
    if(request.method == 'POST'):
        title = request.form['title_phone']
        brand = request.form['brand_phone']
        model = request.form['model_phone']
        year = int(request.form['year_phone'])
        operating_system = request.form['operating_system_phone']
        processor = request.form['processor_phone']
        ram = request.form['ram_phone']
        storage = request.form['storage_phone']
        camera_specifications = request.form['camera_specifications_phone']
        battery_capacity = request.form['battery_capacity_phone']
        price = float(request.form['price_phone'])
        image = request.form['image_phone']
        description = request.form['description_phone']
        isRegularAllowed = request.form.get('visible_phone')

        if not isRegularAllowed:
            isRegularAllowed = False
        else:
            isRegularAllowed = True

        old_price = products_collection.find_one({'_id': ObjectId(product_id)}).get('price', 0)

        products_collection.update_one({'_id': ObjectId(product_id)}, {'$set': {
            'title': title,
            'brand': brand,
            'model': model,
            'year': year,
            'operating_system': operating_system,
            'processor': processor,
            'ram': ram,
            'storage': storage,
            'camera_specifications': camera_specifications,
            'battery_capacity': battery_capacity,
            'price': price,
            'image': image,
            'description': description,
            'isRegularAllowed': isRegularAllowed
        }})

        if(price < old_price):
            favoriteList = products_collection.find_one({'_id': ObjectId(product_id)}).get('favoriteList', [])
            for user in favoriteList:
                user_email = users_collection.find_one({'username': user}).get('email', '')
                message = Mail(
                    from_email = 'e2521987@ceng.metu.edu.tr',
                    to_emails = user_email,
                    subject = 'Price Reduction Alert',
                    html_content = f'The price of the product {title} has been reduced. Check it out on CENGden!')
                try:
                    sg = SendGridAPIClient('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')
                    response = sg.send(message)
                    # print(response.status_code)
                    # print(response.body)
                    # print(response.headers)
                except Exception as e:
                    print(e)

        return redirect(url_for('profile'))
    phone = products_collection.find_one({'_id': ObjectId(product_id)})
    return render_template('edit_phone.html', phone=phone)

@app.route('/edit_private-lesson/<string:product_id>', methods=['GET', 'POST'])
def edit_private_lesson(product_id):
    if(request.method == 'POST'):
        title = request.form['title_private_lesson']
        tutor_name = request.form['tutor_name_private_lesson']
        lessons = request.form['lessons_private_lesson']
        location = request.form['location_private_lesson']
        duration = request.form['duration_private_lesson']
        price = float(request.form['price_private_lesson'])
        image = request.form['image_private_lesson']
        description = request.form['description_private_lesson']
        isRegularAllowed = request.form.get('visible_private_lesson')

        if not isRegularAllowed:
            isRegularAllowed = False
        else:
            isRegularAllowed = True

        old_price = products_collection.find_one({'_id': ObjectId(product_id)}).get('price', 0)

        products_collection.update_one({'_id': ObjectId(product_id)}, {'$set': {
            'title': title,
            'tutor_name': tutor_name,
            'lessons': lessons,
            'location': location,
            'duration': duration,
            'price': price,
            'image': image,
            'description': description,
            'isRegularAllowed': isRegularAllowed
        }})

        if(price < old_price):
            favoriteList = products_collection.find_one({'_id': ObjectId(product_id)}).get('favoriteList', [])
            for user in favoriteList:
                user_email = users_collection.find_one({'username': user}).get('email', '')
                message = Mail(
                    from_email = 'e2521987@ceng.metu.edu.tr',
                    to_emails = user_email,
                    subject = 'Price Reduction Alert',
                    html_content = f'The price of the product {title} has been reduced. Check it out on CENGden!')
                try:
                    sg = SendGridAPIClient('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')
                    response = sg.send(message)
                    # print(response.status_code)
                    # print(response.body)
                    # print(response.headers)
                except Exception as e:
                    print(e)
                
        return redirect(url_for('profile'))
    private_lesson = products_collection.find_one({'_id': ObjectId(product_id)})
    return render_template('edit_private_lesson.html', private_lesson=private_lesson)

@app.route('/display_vehicle/<string:product_id>')
def display_vehicle(product_id):
    # Logic to fetch vehicle information from the database
    # You can use MongoDB to retrieve information about the product with the given product_id
    # Replace this with your actual logic
    user = users_collection.find_one({'username': session.get('username')})
    if (user): 
        is_admin = user.get('isAdmin', False)
    else:
        is_admin = False
    product = products_collection.find_one({'_id': ObjectId(product_id)})
    owner = users_collection.find_one({'username': product.get('owner')})
    return render_template('display_vehicle.html', product = product, username = session.get('username'), is_admin = is_admin, owner = owner)

@app.route('/display_computer/<string:product_id>')
def display_computer(product_id):
    # Logic to fetch computer information from the database
    # Replace this with your actual logic
    user = users_collection.find_one({'username': session.get('username')})
    if (user): 
        is_admin = user.get('isAdmin', False)
    else:
        is_admin = False
    product = products_collection.find_one({'_id': ObjectId(product_id)})
    owner = users_collection.find_one({'username': product.get('owner')})
    return render_template('display_computer.html', product=product, username = session.get('username'), is_admin = is_admin, owner = owner)

@app.route('/display_phone/<string:product_id>')
def display_phone(product_id):
    # Logic to fetch phone information from the database
    # Replace this with your actual logic
    user = users_collection.find_one({'username': session.get('username')})
    if (user): 
        is_admin = user.get('isAdmin', False)
    else:
        is_admin = False
    product = products_collection.find_one({'_id': ObjectId(product_id)})
    owner = users_collection.find_one({'username': product.get('owner')})
    return render_template('display_phone.html', product=product, username = session.get('username'), is_admin = is_admin, owner = owner)

@app.route('/display_private-lesson/<string:product_id>')
def display_private_lesson(product_id):
    # Logic to fetch private lesson information from the database
    # Replace this with your actual logic
    user = users_collection.find_one({'username': session.get('username')})
    if (user): 
        is_admin = user.get('isAdmin', False)
    else:
        is_admin = False
    product = products_collection.find_one({'_id': ObjectId(product_id)})
    owner = users_collection.find_one({'username': product.get('owner')})
    return render_template('display_private_lesson.html', product=product, username = session.get('username'), is_admin = is_admin, owner = owner) 

@app.route('/add_to_favorites/<string:product_id>', methods=['POST'])
def add_to_favorites(product_id):
    product = products_collection.find_one({'_id': ObjectId(product_id)})
    if product:
        favoriteList = product.get('favoriteList', [])
        username = session.get('username')
        if username not in favoriteList:
            favoriteList.append(username)
            products_collection.update_one({'_id': ObjectId(product_id)}, {'$set': {'favoriteList': favoriteList}})
    return redirect(url_for('index'))

@app.route('/remove_from_favorites/<string:product_id>', methods=['POST'])
def remove_from_favorites(product_id):
    product = products_collection.find_one({'_id': ObjectId(product_id)})
    if product:
        favoriteList = product.get('favoriteList', [])
        username = session.get('username')
        if username in favoriteList:
            favoriteList.remove(username)
            products_collection.update_one({'_id': ObjectId(product_id)}, {'$set': {'favoriteList': favoriteList}})
    return redirect(url_for('index'))

@app.route('/delete_product/<string:product_id>', methods=['POST'])
def delete_product(product_id):
    products_collection.delete_one({'_id': ObjectId(product_id)})
    return redirect(url_for('profile'))

@app.route('/activate_product/<string:product_id>', methods=['POST'])
def activate_product(product_id):
    products_collection.update_one({'_id': ObjectId(product_id)}, {'$set': {'isActivated': True}})
    return redirect(url_for('profile'))

@app.route('/deactivate_product/<string:product_id>', methods=['POST'])
def deactivate_product(product_id):
    products_collection.update_one({'_id': ObjectId(product_id)}, {'$set': {'isActivated': False}})
    return redirect(url_for('profile'))

@app.route('/rotate_edit/<string:user_id>', methods=['GET', 'POST'])
def rotate_edit(user_id):
    user = users_collection.find_one({'_id': ObjectId(user_id)})
    return render_template('edit_user_own.html', user=user)

@app.route('/rotate_vehicle/<string:product_id>', methods=['GET', 'POST'])
def rotate_vehicle(product_id):
    product = products_collection.find_one({'_id': ObjectId(product_id)})
    return render_template('edit_vehicle.html', vehicle=product)

@app.route('/rotate_computer/<string:product_id>', methods=['GET', 'POST'])
def rotate_computer(product_id):
    product = products_collection.find_one({'_id': ObjectId(product_id)})
    return render_template('edit_computer.html', computer=product)

@app.route('/rotate_phone/<string:product_id>', methods=['GET', 'POST'])
def rotate_phone(product_id):
    product = products_collection.find_one({'_id': ObjectId(product_id)})
    return render_template('edit_phone.html', phone=product)

@app.route('/rotate_private_lesson/<string:product_id>', methods=['GET', 'POST'])
def rotate_private_lesson(product_id):
    product = products_collection.find_one({'_id': ObjectId(product_id)})
    return render_template('edit_private_lesson.html', private_lesson=product)

@app.route('/item_list', methods=['GET'])
def item_list():
    products = products_collection.find()
    return render_template('item_list.html', products=products)

if __name__ == '__main__':
    app.run(debug=True)