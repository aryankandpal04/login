from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this to a secret key for session management

# Function to create a connection to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Function to create the database table if it doesn't exist
def create_table():
    try:
        conn = get_db_connection()
        conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error creating table: {e}")

# Function to check if a user exists in the database
def user_exists(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user is not None

# Function to add a new user to the database
def add_user(username, password):
    try:
        conn = get_db_connection()
        hashed_password = generate_password_hash(password)
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        print(f"User '{username}' added to the database.")
        conn.close()
    except Exception as e:
        print(f"Error adding user '{username}' to the database: {e}")

# Route for the home page
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'login' in request.form:
            return redirect(url_for('login'))
        elif 'signup' in request.form:
            return redirect(url_for('signup'))
    return render_template('index.html')

# Route for the signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not user_exists(username):
            add_user(username, password)
            return redirect(url_for('login'))
        else:
            return "Username already exists. Please choose a different username."
    return redirect(url_for('index'))

# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            # You can add session management here
            return "Login successful!"
        else:
            if not user_exists(username):
                return "Username doesn't exist. Please sign up."
            else:
                return "Invalid username or password."
    return redirect(url_for('index'))

if __name__ == '__main__':
    create_table()  # Create the users table if it doesn't exist
    app.run(debug=True)
