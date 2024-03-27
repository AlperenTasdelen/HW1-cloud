from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_pymongo import PyMongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

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

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    
    user = users_collection.find_one({'username': username})
    return render_template('profile.html', user=user)

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
        password = request.form['password']
        # Add user to the users array
        if users_collection.find_one({'$or': [{'username': username}, {'password': password}]}):
            return redirect(url_for('register'))
        
        user_data = {
            'username': username,
            'password': password
        }
        users_collection.insert_one(user_data)
        # Redirect or render another page
        return redirect(url_for('signin'))
    else:
        # Render the registration form (GET request)
        return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = users_collection.find_one({'username': username, 'password': password})
    if user:
        # User found, redirect to homepage or dashboard
        session['username'] = username
        return redirect(url_for('index'))
    else:
        # User not found or incorrect password, redirect back to sign-in page
        return redirect(url_for('signin'))

@app.route('/')
def index():
    username = session.get('username')
    session['username'] = username
    return render_template('index.html')

@app.route('/products')
def products():
    #products = mongo.db.products.find()  # Retrieve products from the database
    products = client.db.products.find()
    return render_template('products.html', products=products)

@app.route('/new_item', methods=['GET', 'POST'])
def new_item():
    username = request.args.get('username')
    if not username:
        # Handle the case where username is not provided
        # You may redirect to the login page or display an error message
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

@app.route('/add_vehicle', methods=['POST'])
def add_vehicle():
    if request.method == 'POST':
        # Retrieve form data
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

        # Prepare item data
        vehicle_data = {
            'owner': session.get('username'),
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
            'description': description
        }

        # Insert item into MongoDB
        db.vehicles.insert_one(vehicle_data)

        # Redirect to the profile page or any other page as needed
        return redirect(url_for('profile'))

@app.route('/add_computer', methods=['POST'])
def add_computer():
    if request.method == 'POST':
        # Retrieve form data
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

        # Prepare item data
        computer_data = {
            'owner': session.get('username'),
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
            'description': description
        }

        # Insert item into MongoDB
        db.computers.insert_one(computer_data)

        # Redirect to the profile page or any other page as needed
        return redirect(url_for('profile'))

@app.route('/add_phone', methods=['POST'])
def add_phone():
    if request.method == 'POST':
        # Retrieve form data
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

        # Prepare item data
        phone_data = {
            'owner': session.get('username'),
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
            'description': description
        }

        # Insert item into MongoDB
        db.phones.insert_one(phone_data)

        # Redirect to the profile page or any other page as needed
        return redirect(url_for('profile'))

@app.route('/add_private_lesson', methods=['POST'])
def add_private_lesson():
    if request.method == 'POST':
        # Retrieve form data
        title = request.form['title_private_lesson']
        tutor_name = request.form['tutor_name_private_lesson']
        lessons = request.form['lessons_private_lesson']
        location = request.form['location_private_lesson']
        duration = request.form['duration_private_lesson']
        price = float(request.form['price_private_lesson'])
        image = request.form['image_private_lesson']
        description = request.form['description_private_lesson']

        # Prepare item data
        private_lesson_data = {
            'owner': session.get('username'),
            'title': title,
            'tutor_name': tutor_name,
            'lessons': lessons,
            'location': location,
            'duration': duration,
            'price': price,
            'image': image,
            'description': description
        }

        # Insert item into MongoDB
        db.private_lessons.insert_one(private_lesson_data)

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

# Route for adding a new vehicle
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

if __name__ == '__main__':
    app.run()