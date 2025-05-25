from flask import Flask, request, render_template_string, jsonify
import mysql.connector
import os
from mysql.connector import Error

app = Flask(__name__)

# Database configuration - Using environment variables for Render
DB_CONFIG = {
    'host': os.environ.get('DB_HOST'),
    'port': int(os.environ.get('DB_PORT', 11794)),
    'database': os.environ.get('DB_NAME'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'ssl_disabled': False,
    'ssl_verify_cert': False,  # Aiven compatibility
    'autocommit': True,
    'use_unicode': True,
    'charset': 'utf8mb4'
}

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def validate_user(username, password, email=None, role=None):
    """Validate user credentials against existing database including email and role"""
    connection = get_db_connection()
    if not connection:
        print("No database connection available")
        return False, None
    
    try:
        cursor = connection.cursor()
        
        # First, let's see what's actually in the database
        print(f"Attempting to validate user: '{username}' with password: '{password}'")
        if email:
            print(f"Email: '{email}'")
        if role:
            print(f"Role: '{role}'")
        
        # Debug: Check all users in the table
        cursor.execute("SELECT user_name, password, email, role FROM User_info")
        all_users = cursor.fetchall()
        print(f"All users in database: {all_users}")
        
        # Build query based on provided parameters
        base_query = "SELECT user_name, password, email, role FROM User_info WHERE user_name = %s AND password = %s"
        params = [username, password]
        
        if email:
            base_query += " AND email = %s"
            params.append(email)
        
        if role:
            base_query += " AND role = %s"
            params.append(role)
        
        cursor.execute(base_query, params)
        result = cursor.fetchone()
        
        print(f"Query result: {result}")
        
        if result:
            user_data = {
                'username': result[0],
                'email': result[2] if len(result) > 2 else None,
                'role': result[3] if len(result) > 3 else None
            }
            print("User validation successful!")
            return True, user_data
        else:
            # Try case-insensitive search for username and email
            case_query = "SELECT user_name, password, email, role FROM User_info WHERE LOWER(user_name) = LOWER(%s) AND password = %s"
            case_params = [username, password]
            
            if email:
                case_query += " AND LOWER(email) = LOWER(%s)"
                case_params.append(email)
            
            if role:
                case_query += " AND role = %s"
                case_params.append(role)
            
            cursor.execute(case_query, case_params)
            result_case = cursor.fetchone()
            
            if result_case:
                user_data = {
                    'username': result_case[0],
                    'email': result_case[2] if len(result_case) > 2 else None,
                    'role': result_case[3] if len(result_case) > 3 else None
                }
                print("User validation successful (case-insensitive)!")
                return True, user_data
            else:
                print("No matching user found")
                return False, None
                
    except Error as e:
        print(f"Error validating user: {e}")
        return False, None
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
        body { font-family: Arial, sans-serif; max-width: 500px; margin: 50px auto; padding: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="text"], input[type="password"], input[type="email"], select { 
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
        .user-info { background-color: #e7f3ff; padding: 15px; border-radius: 4px; margin-top: 10px; }
        .optional { font-size: 0.9em; color: #666; }
    </style>
</head>
<body>
    <h2>User Login Validation</h2>
    
    {% if message %}
        <div class="message {{ message_type }}">{{ message }}</div>
    {% endif %}
    
    {% if user_data %}
        <div class="user-info">
            <h3>Login Successful!</h3>
            <p><strong>Username:</strong> {{ user_data.username }}</p>
            {% if user_data.email %}
                <p><strong>Email:</strong> {{ user_data.email }}</p>
            {% endif %}
            {% if user_data.role %}
                <p><strong>Role:</strong> {{ user_data.role }}</p>
            {% endif %}
        </div>
    {% endif %}
    
    <form method="POST" action="/login">
        <div class="form-group">
            <label for="username">Username: <span style="color: red;">*</span></label>
            <input type="text" id="username" name="username" required>
        </div>
        
        <div class="form-group">
            <label for="password">Password: <span style="color: red;">*</span></label>
            <input type="password" id="password" name="password" required>
        </div>
        
        <div class="form-group">
            <label for="email">Email: <span class="optional">(optional)</span></label>
            <input type="email" id="email" name="email" placeholder="Optional - for additional verification">
        </div>
        
        <div class="form-group">
            <label for="role">Role: <span class="optional">(optional)</span></label>
            <select id="role" name="role">
                <option value="">Select role (optional)</option>
                <option value="admin">Admin</option>
                <option value="user">User</option>
                <option value="manager">Manager</option>
                <option value="employee">Employee</option>
                <option value="guest">Guest</option>
            </select>
        </div>
        
        <button type="submit">Login</button>
    </form>
    
    <hr>
    <p><strong>Required fields:</strong> Username and Password</p>
    <p><strong>Optional fields:</strong> Email and Role (for additional verification)</p>
    <p><em>If you provide email or role, they must match your database record.</em></p>
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
    email = request.form.get('email')  # Optional
    role = request.form.get('role')    # Optional
    
    # Clean up empty strings
    email = email.strip() if email else None
    role = role.strip() if role else None
    
    if not username or not password:
        return render_template_string(LOGIN_TEMPLATE, 
                                    message="Please enter both username and password", 
                                    message_type="error")
    
    # First check if we can connect to database
    connection = get_db_connection()
    if not connection:
        return render_template_string(LOGIN_TEMPLATE, 
                                    message="Database connection failed. Check your environment variables.", 
                                    message_type="error")
    connection.close()
    
    # Try to validate user
    try:
        is_valid, user_data = validate_user(username, password, email, role)
        if is_valid:
            return render_template_string(LOGIN_TEMPLATE, 
                                        message=f"Login successful! Welcome, {username}!", 
                                        message_type="success",
                                        user_data=user_data)
        else:
            error_msg = "Invalid credentials."
            if email and role:
                error_msg += " Username, password, email, and role must all match."
            elif email:
                error_msg += " Username, password, and email must all match."
            elif role:
                error_msg += " Username, password, and role must all match."
            else:
                error_msg += " Username and password must match."
            error_msg += " Visit /debug to see database contents."
            
            return render_template_string(LOGIN_TEMPLATE, 
                                        message=error_msg, 
                                        message_type="error")
    except Exception as e:
        return render_template_string(LOGIN_TEMPLATE, 
                                    message=f"Login error: {str(e)}", 
                                    message_type="error")

@app.route('/api/login', methods=['POST'])
def api_login():
    """API endpoint for login validation"""
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400
    
    username = data['username']
    password = data['password']
    email = data.get('email')  # Optional
    role = data.get('role')    # Optional
    
    is_valid, user_data = validate_user(username, password, email, role)
    if is_valid:
        return jsonify({
            'success': True, 
            'message': f'Login successful for {username}',
            'user_data': user_data
        })
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/debug')
def debug_info():
    """Debug endpoint to check database connection and data"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'No database connection'}), 500
    
    try:
        cursor = connection.cursor()
        
        # Check if table exists
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        # Get table structure
        cursor.execute("DESCRIBE User_info")
        columns = cursor.fetchall()
        
        # Get sample data (first 3 rows, hiding passwords)
        cursor.execute("SELECT user_name, 'HIDDEN' as password, email, role FROM User_info LIMIT 3")
        sample_data = cursor.fetchall()
        
        # Count total users
        cursor.execute("SELECT COUNT(*) FROM User_info")
        user_count = cursor.fetchone()[0]
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'database_connected': True,
            'tables': [table[0] for table in tables],
            'user_info_columns': [{'Field': col[0], 'Type': col[1]} for col in columns],
            'sample_users': [{'user_name': row[0], 'password': row[1], 'email': row[2], 'role': row[3]} for row in sample_data],
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
