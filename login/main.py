from flask import Flask, request, render_template_string, jsonify
import mysql.connector
import os
from mysql.connector import Error

app = Flask(__name__)

# Database configuration - Using environment variables for Render
DB_CONFIG = {
    'host': os.environ.get('DB_HOST'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'database': os.environ.get('DB_NAME'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'ssl_disabled': False
}

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def validate_user(username, password):
    """Validate user credentials against existing database"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        # Query your exact table and column names
        query = "SELECT * FROM User_info WHERE user_name = %s AND password = %s"
        cursor.execute(query, (username, password))
        result = cursor.fetchone()
        return result is not None
    except Error as e:
        print(f"Error validating user: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        connection.close()

# HTML template for login form
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>User Login Validation</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 400px; margin: 50px auto; padding: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="text"], input[type="password"] { 
            width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; 
        }
        button { 
            background-color: #4CAF50; color: white; padding: 10px 20px; 
            border: none; border-radius: 4px; cursor: pointer; width: 100%; 
        }
        button:hover { background-color: #45a049; }
        .message { padding: 10px; margin: 10px 0; border-radius: 4px; }
        .success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    </style>
</head>
<body>
    <h2>User Login Validation</h2>
    
    {% if message %}
        <div class="message {{ message_type }}">{{ message }}</div>
    {% endif %}
    
    <form method="POST" action="/login">
        <div class="form-group">
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" required>
        </div>
        
        <div class="form-group">
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required>
        </div>
        
        <button type="submit">Login</button>
    </form>
    
    <hr>
    <p><strong>Use your existing database credentials to test</strong></p>
</body>
</html>
"""

@app.route('/')
def index():
    """Display login form"""
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/login', methods=['POST'])
def login():
    """Handle login form submission"""
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username or not password:
        return render_template_string(LOGIN_TEMPLATE, 
                                    message="Please enter both username and password", 
                                    message_type="error")
    
    if validate_user(username, password):
        return render_template_string(LOGIN_TEMPLATE, 
                                    message=f"Login successful! Welcome, {username}!", 
                                    message_type="success")
    else:
        return render_template_string(LOGIN_TEMPLATE, 
                                    message="Invalid username or password", 
                                    message_type="error")

@app.route('/api/login', methods=['POST'])
def api_login():
    """API endpoint for login validation"""
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400
    
    username = data['username']
    password = data['password']
    
    if validate_user(username, password):
        return jsonify({'success': True, 'message': f'Login successful for {username}'})
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/health')
def health_check():
    """Health check endpoint"""
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

# Initialize database connection check on startup
if __name__ == '__main__':
    print("Starting Flask application...")
    connection = get_db_connection()
    if connection:
        print("Database connection successful!")
        connection.close()
    else:
        print("Warning: Could not connect to database")
    
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
