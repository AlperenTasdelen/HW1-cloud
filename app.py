from flask import Flask, render_template, request, redirect, url_for, jsonify, session
#from flask_pymongo import PyMongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from werkzeug.security import generate_password_hash
from bson.objectid import ObjectId

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

#app.config["MONGO_URI"] = "mongodb://e2521987:Alper.4551@cengdencluster.jvmzjb0.mongodb.net/?retryWrites=true&w=majority&appName=CENGdenCluster"
#mongo = PyMongo(app)

#users = [{'username': 'user1', 'password': 'password1'}, {'username': 'user2', 'password': 'password2'}]

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
""""
@app.route('/logout')
def logout():
    # Perform logout actions if needed
    return redirect(url_for('index'))
"""
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

if __name__ == '__main__':
    app.run()