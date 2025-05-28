from flask import Flask, request, render_template_string, jsonify
import mysql.connector
import os
from mysql.connector import Error

app = Flask(__name__)

# Database configuration
DB_CONFIG = {
    'host': os.environ.get('DB_HOST'),
    'port': int(os.environ.get('DB_PORT', 11794)),
    'database': os.environ.get('DB_NAME'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'ssl_disabled': False,
    'ssl_verify_cert': False,
    'autocommit': True,
    'use_unicode': True,
    'charset': 'utf8mb4'
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def validate_user(username, password):
    connection = get_db_connection()
    if not connection:
        print("No database connection available")
        return False
    
    try:
        cursor = connection.cursor()
        print(f"Attempting to validate user: '{username}' with password: '{password}'")

        cursor.execute("SELECT user_name, password FROM User_info")
        all_users = cursor.fetchall()
        print(f"All users in database: {all_users}")

        query = "SELECT user_name, password FROM User_info WHERE user_name = %s AND password = %s"
        cursor.execute(query, (username, password))
        result = cursor.fetchone()

        print(f"Query result: {result}")
        if result:
            print("User validation successful!")
            return True
        else:
            query_case = "SELECT user_name, password FROM User_info WHERE LOWER(user_name) = LOWER(%s) AND password = %s"
            cursor.execute(query_case, (username, password))
            result_case = cursor.fetchone()

            if result_case:
                print("User validation successful (case-insensitive)!")
                return True
            else:
                print("No matching user found")
                return False
    except Error as e:
        print(f"Error validating user: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        connection.close()

# Updated login form UI
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>User Login</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f2f2f2;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .login-container {
            background: white;
            padding: 30px 40px;
            border-radius: 10px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            width: 100%;
            max-width: 400px;
        }
        h2 {
            text-align: center;
            margin-bottom: 25px;
            color: #333;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            font-weight: bold;
            display: block;
            margin-bottom: 5px;
            color: #555;
        }
        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 6px;
            font-size: 14px;
        }
        button {
            width: 100%;
            padding: 12px;
            background-color: #007bff;
            border: none;
            color: white;
            border-radius: 6px;
            font-size: 16px;
            cursor: pointer;
        }
        button:hover {
            background-color: #0056b3;
        }
        .message {
            margin-top: 15px;
            padding: 10px;
            border-radius: 6px;
        }
        .success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .note {
            text-align: center;
            margin-top: 15px;
            font-size: 13px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <h2>User Login</h2>

        {% if message %}
            <div class="message {{ message_type }}">{{ message }}</div>
        {% endif %}

        <form method="POST" action="/login">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" name="username" id="username" required>
            </div>

            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" name="password" id="password" required>
            </div>

            <button type="submit">Login</button>
        </form>

        <p class="note">Use your existing database credentials to test.</p>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username or not password:
        return render_template_string(LOGIN_TEMPLATE, message="Please enter both username and password", message_type="error")
    
    connection = get_db_connection()
    if not connection:
        return render_template_string(LOGIN_TEMPLATE, message="Database connection failed. Check your environment variables.", message_type="error")
    connection.close()
    
    try:
        if validate_user(username, password):
            return render_template_string(LOGIN_TEMPLATE, message=f"Login successful! Welcome, {username}!", message_type="success")
        else:
            return render_template_string(LOGIN_TEMPLATE, message="Invalid username or password. Visit /debug to see database contents.", message_type="error")
    except Exception as e:
        return render_template_string(LOGIN_TEMPLATE, message=f"Login error: {str(e)}", message_type="error")

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400

    username = data['username']
    password = data['password']

    if validate_user(username, password):
        return jsonify({'success': True, 'message': f'Login successful for {username}'})
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/debug')
def debug_info():
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'No database connection'}), 500
    
    try:
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        cursor.execute("DESCRIBE User_info")
        columns = cursor.fetchall()
        cursor.execute("SELECT user_name, 'HIDDEN' as password FROM User_info LIMIT 3")
        sample_data = cursor.fetchall()
        cursor.execute("SELECT COUNT(*) FROM User_info")
        user_count = cursor.fetchone()[0]
        cursor.close()
        connection.close()
        
        return jsonify({
            'database_connected': True,
            'tables': [table[0] for table in tables],
            'user_info_columns': [{'Field': col[0], 'Type': col[1]} for col in columns],
            'sample_users': [{'user_name': row[0], 'password': row[1]} for row in sample_data],
            'total_users': user_count,
            'db_config': {
                'host': os.environ.get('DB_HOST', 'Not set'),
                'port': os.environ.get('DB_PORT', 'Not set'),
                'database': os.environ.get('DB_NAME', 'Not set'),
                'user': os.environ.get('DB_USER', 'Not set')
            }
        })
    except Error as e:
        connection.close()
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM User_info")
            count = cursor.fetchone()[0]
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'healthy',
                'database': 'connected',
                'users_count': count
            })
        except Error as e:
            connection.close()
            return jsonify({
                'status': 'unhealthy',
                'database': 'connected but query failed',
                'error': str(e)
            }), 500
    else:
        return jsonify({'status': 'unhealthy', 'database': 'disconnected'}), 500

if __name__ == '__main__':
    print("Starting Flask application...")
    connection = get_db_connection()
    if connection:
        print("Database connection successful!")
        connection.close()
    else:
        print("Warning: Could not connect to database")

    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
