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

def validate_user(username, password, email=None, phone=None):
    """Validate user credentials against existing database with additional info"""
    connection = get_db_connection()
    if not connection:
        print("No database connection available")
        return False
    
    try:
        cursor = connection.cursor()
        
        # First, let's see what's actually in the database
        print(f"Attempting to validate user: '{username}' with password: '{password}'")
        if email:
            print(f"Email: '{email}'")
        if phone:
            print(f"Phone: '{phone}'")
        
        # Debug: Check all users in the table
        cursor.execute("SELECT user_name, password, email, phone FROM User_info")
        all_users = cursor.fetchall()
        print(f"All users in database: {all_users}")
        
        # Build dynamic query based on provided information
        base_query = "SELECT user_name, password, email, phone FROM User_info WHERE user_name = %s AND password = %s"
        params = [username, password]
        
        # Add email check if provided
        if email and email.strip():
            base_query += " AND email = %s"
            params.append(email.strip())
        
        # Add phone check if provided
        if phone and phone.strip():
            base_query += " AND phone = %s"
            params.append(phone.strip())
        
        print(f"Executing query: {base_query}")
        print(f"With parameters: {params}")
        
        cursor.execute(base_query, params)
        result = cursor.fetchone()
        
        print(f"Query result: {result}")
        
        if result:
            print("User validation successful!")
            return True
        else:
            # Try case-insensitive search for username and email
            case_query = "SELECT user_name, password, email, phone FROM User_info WHERE LOWER(user_name) = LOWER(%s) AND password = %s"
            case_params = [username, password]
            
            if email and email.strip():
                case_query += " AND LOWER(email) = LOWER(%s)"
                case_params.append(email.strip())
            
            if phone and phone.strip():
                case_query += " AND phone = %s"
                case_params.append(phone.strip())
            
            cursor.execute(case_query, case_params)
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

# HTML template for login form
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Enhanced User Login Validation</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 500px; margin: 50px auto; padding: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="text"], input[type="password"], input[type="email"], input[type="tel"] { 
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
        .optional { color: #666; font-size: 0.9em; font-style: italic; }
        .divider { margin: 20px 0; border-top: 1px solid #ddd; padding-top: 15px; }
        .info-box { 
            background-color: #e3f2fd; color: #1565c0; padding: 15px; 
            border-radius: 4px; margin-bottom: 20px; border-left: 4px solid #2196f3; 
        }
    </style>
</head>
<body>
    <h2>Enhanced User Login Validation</h2>
    
    <div class="info-box">
        <strong>Multi-Factor Validation:</strong> Enter your username and password. 
        Optionally provide email and/or phone number for additional security verification.
    </div>
    
    {% if message %}
        <div class="message {{ message_type }}">{{ message }}</div>
    {% endif %}
    
    <form method="POST" action="/login">
        <div class="form-group">
            <label for="username">Username: <span style="color: red;">*</span></label>
            <input type="text" id="username" name="username" required 
                   value="{{ request.form.username if request.form.username else '' }}">
        </div>
        
        <div class="form-group">
            <label for="password">Password: <span style="color: red;">*</span></label>
            <input type="password" id="password" name="password" required>
        </div>
        
        <div class="divider">
            <strong>Additional Verification</strong> <span class="optional">(Optional - but increases security)</span>
        </div>
        
        <div class="form-group">
            <label for="email">Email Address:</label>
            <input type="email" id="email" name="email" placeholder="your.email@example.com"
                   value="{{ request.form.email if request.form.email else '' }}">
            <small class="optional">Leave blank if you don't want to verify email</small>
        </div>
        
        <div class="form-group">
            <label for="phone">Phone Number:</label>
            <input type="tel" id="phone" name="phone" placeholder="e.g., +1234567890"
                   value="{{ request.form.phone if request.form.phone else '' }}">
            <small class="optional">Leave blank if you don't want to verify phone</small>
        </div>
        
        <button type="submit">Validate Login</button>
    </form>
    
    <hr>
    <p><strong>Use your existing database credentials to test</strong></p>
    <p><small>* Required fields | Additional fields are optional but provide extra security</small></p>
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
    email = request.form.get('email')
    phone = request.form.get('phone')
    
    if not username or not password:
        return render_template_string(LOGIN_TEMPLATE, 
                                    message="Please enter both username and password", 
                                    message_type="error",
                                    request=request)
    
    # First check if we can connect to database
    connection = get_db_connection()
    if not connection:
        return render_template_string(LOGIN_TEMPLATE, 
                                    message="Database connection failed. Check your environment variables.", 
                                    message_type="error",
                                    request=request)
    connection.close()
    
    # Try to validate user
    try:
        if validate_user(username, password, email, phone):
            verification_details = []
            if email and email.strip():
                verification_details.append(f"email ({email})")
            if phone and phone.strip():
                verification_details.append(f"phone ({phone})")
            
            success_message = f"Login successful! Welcome, {username}!"
            if verification_details:
                success_message += f" Additional verification passed for: {', '.join(verification_details)}"
            
            return render_template_string(LOGIN_TEMPLATE, 
                                        message=success_message, 
                                        message_type="success",
                                        request=request)
        else:
            error_message = "Invalid credentials."
            if email and email.strip():
                error_message += " Email verification failed."
            if phone and phone.strip():
                error_message += " Phone verification failed."
            error_message += " Visit /debug to see database contents."
            
            return render_template_string(LOGIN_TEMPLATE, 
                                        message=error_message, 
                                        message_type="error",
                                        request=request)
    except Exception as e:
        return render_template_string(LOGIN_TEMPLATE, 
                                    message=f"Login error: {str(e)}", 
                                    message_type="error",
                                    request=request)

@app.route('/api/login', methods=['POST'])
def api_login():
    """API endpoint for login validation"""
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400
    
    username = data['username']
    password = data['password']
    email = data.get('email')
    phone = data.get('phone')
    
    if validate_user(username, password, email, phone):
        verification_info = []
        if email:
            verification_info.append('email')
        if phone:
            verification_info.append('phone')
        
        message = f'Login successful for {username}'
        if verification_info:
            message += f' with additional verification: {", ".join(verification_info)}'
        
        return jsonify({'success': True, 'message': message})
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
        cursor.execute("SELECT user_name, 'HIDDEN' as password, email, phone FROM User_info LIMIT 3")
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
            'sample_users': [{'user_name': row[0], 'password': row[1], 'email': row[2], 'phone': row[3]} for row in sample_data],
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
