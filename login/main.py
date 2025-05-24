from flask import Flask, request, render_template_string
import mysql.connector

app = Flask(__name__)

# MySQL config
db = mysql.connector.connect(
    host="sql.freesqldatabase.com",
    user=" sql12780952",
    password="idW6YYeIFq",
    database=" sql12780952"
)

@app.route('/', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cursor = db.cursor()
        cursor.execute("SELECT * FROM User_Information WHERE user_name=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        
        if user:
            message = f"✅ Welcome, {user[3]}!"
        else:
            message = "❌ Invalid username or password."

    return render_template_string('''
        <h2>Login</h2>
        <form method="POST">
            Username: <input type="text" name="username"><br>
            Password: <input type="password" name="password"><br>
            <input type="submit" value="Login">
        </form>
        <p>{{ message }}</p>
    ''', message=message)

