from flask import Flask, request, render_template_string, jsonify
import mysql.connector
import os
from mysql.connector import Error
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration - Using environment variables for Render
DB_CONFIG = {
    'host': os.environ.get('DB_HOST'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'database': os.environ.get('DB_NAME', 'defaultdb'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'ssl_disabled': False,
    'ssl_verify_cert': False,
    'autocommit': True,
    'use_unicode': True,
    'charset': 'utf8mb4',
    'connect_timeout': 60,
    'sql_mode': 'STRICT_TRANS_TABLES'
}

def get_db_connection():
    """Create and return a database connection with improved error handling"""
    try:
        config = {k: v for k, v in DB_CONFIG.items() if v is not None}
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            logger.info("Database connection established successfully")
            return connection
        else:
            logger.error("Database connection failed")
            return None
            
    except Error as e:
        logger.error(f"Error connecting to MySQL: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during database connection: {e}")
        return None

def add_user(username, password, email=None, phone=None):
    """Add a new user to the database with provided information"""
    connection = get_db_connection()
    if not connection:
        logger.error("No database connection available")
        return False, "Database connection failed"
    
    cursor = None
    try:
        cursor = connection.cursor(buffered=True)
        
        # Log addition attempt (without password for security)
        logger.info(f"Attempting to add user: '{username}'")
        if email:
            logger.info(f"Email provided: '{email}'")
        if phone:
            logger.info(f"Phone provided: '{phone}'")
        
        # Check if username already exists
        cursor.execute("SELECT user_id FROM User_info WHERE user_name = %s", (username,))
        if cursor.fetchone():
            logger.warning(f"Username '{username}' already exists")
            return False, "Username already exists"
        
        # Check if email exists (if provided)
        if email and email.strip():
            cursor.execute("SELECT user_id FROM User_info WHERE email = %s", (email.strip(),))
            if cursor.fetchone():
                logger.warning(f"Email '{email}' already exists")
                return False, "Email already exists"
        
        # Check if phone exists (if provided)
        if phone and phone.strip():
            cursor.execute("SELECT user_id FROM User_info WHERE phone = %s", (phone.strip(),))
            if cursor.fetchone():
                logger.warning(f"Phone '{phone}' already exists")
                return False, "Phone number already exists"
        
        # Build insert query
        base_query = "INSERT INTO User_info (user_name, password"
        values = [username, password]
        placeholders = ["%s", "%s"]
        
        if email and email.strip():
            base_query += ", email"
            values.append(email.strip())
            placeholders.append("%s")
        
        if phone and phone.strip():
            base_query += ", phone"
            values.append(phone.strip())
            placeholders.append("%s")
        
        base_query += ") VALUES (" + ", ".join(placeholders) + ")"
        
        logger.info(f"Executing insert query with {len(values)} parameters")
        cursor.execute(base_query, values)
        
        logger.info(f"User '{username}' added successfully")
        return True, "User added successfully"
                
    except Error as e:
        logger.error(f"Database error adding user: {e}")
        return False, f"Database error: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error adding user: {e}")
        return False, f"Unexpected error: {str(e)}"
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

# HTML template for user registration form
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>User Registration</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="min-h-screen bg-gray-100 flex items-center justify-center p-4">
    <div class="w-full max-w-md bg-white rounded-2xl shadow-xl p-8">
        <h2 class="text-2xl font-bold text-center text-gray-800 mb-8">Create Your Account</h2>
        
        <div class="bg-blue-50 border-l-4 border-blue-500 p-4 mb-8 rounded-r-lg">
            <p class="text-sm text-blue-800">
                <span class="font-semibold">Secure Registration:</span> Enter your username and password. 
                Optionally provide email and/or phone number for account recovery.
            </p>
        </div>
        
        {% if message %}
            <div class="mb-6 p-4 rounded-lg {{ 'bg-green-100 text-green-800 border border-green-300' if message_type == 'success' else 'bg-red-100 text-red-800 border border-red-300' }}">
                {{ message }}
            </div>
        {% endif %}
        
        <form method="POST" action="/login" class="space-y-6">
            <div>
                <label for="username" class="block text-sm font-medium text-gray-700 mb-2">
                    Username <span class="text-red-500">*</span>
                </label>
                <input type="text" id="username" name="username" required
                       value="{{ request.form.username if request.form.username else '' }}"
                       placeholder="Choose a username"
                       class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200">
            </div>
            
            <div>
                <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
                    Password <span class="text-red-500">*</span>
                </label>
                <input type="password" id="password" name="password" required
                       placeholder="Create a password"
                       class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200">
            </div>
            
            <div class="pt-4 border-t border-gray-200">
                <p class="text-sm font-semibold text-gray-700 mb-2">Additional Information</p>
                <p class="text-xs text-gray-500 italic mb-4">Optional - helps with account recovery</p>
            </div>
            
            <div>
                <label for="email" class="block text-sm font-medium text-gray-700 mb-2">Email Address</label>
                <input type="email" id="email" name="email"
                       placeholder="your.email@example.com"
                       value="{{ request.form.email if request.form.email else '' }}"
                       class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200">
                <p class="text-xs text-gray-500 mt-1 italic">Leave blank if not providing email</p>
            </div>
            
            <div>
                <label for="phone" class="block text-sm font-medium text-gray-700 mb-2">Phone Number</label>
                <input type="tel" id="phone" name="phone"
                       placeholder="e.g., +1234567890"
                       value="{{ request.form.phone if request.form.phone else '' }}"
                       class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200">
                <p class="text-xs text-gray-500 mt-1 italic">Leave blank if not providing phone</p>
            </div>
            
            <button type="submit"
                    class="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-200">
                Register Account
            </button>
        </form>
        
        <div class="mt-8 pt-6 border-t border-gray-200 text-center text-sm text-gray-600">
            <p class="font-medium">Create a new account with your details</p>
            <p class="mt-2"><span class="text-red-500">*</span> Required fields | Additional fields are optional</p>
            <p class="mt-2">Visit <a href="/debug" class="text-blue-600 hover:underline">/debug</a> for database details</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """Display registration form"""
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/login', methods=['POST'])
def login():
    """Handle registration form submission with improved error handling"""
    try:
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        
        # Validate required fields
        if not username or not password:
            return render_template_string(LOGIN_TEMPLATE, 
                                        message="Please provide both username and password", 
                                        message_type="error",
                                        request=request)
        
        # Check database connection first
        connection = get_db_connection()
        if not connection:
            logger.error("Database connection failed during registration attempt")
            return render_template_string(LOGIN_TEMPLATE, 
                                        message="Database connection failed. Please check your environment variables and try again.", 
                                        message_type="error",
                                        request=request)
        connection.close()
        
        # Attempt to add user
        success, message = add_user(username, password, email, phone)
        if success:
            logger.info(f"Successful registration for user: {username}")
            return render_template_string(LOGIN_TEMPLATE, 
                                        message=f"Registration successful! Welcome, {username}!", 
                                        message_type="success",
                                        request=request)
        else:
            logger.warning(f"Failed registration attempt for user: {username} - {message}")
            return render_template_string(LOGIN_TEMPLATE, 
                                        message=message, 
                                        message_type="error",
                                        request=request)
            
    except Exception as e:
        logger.error(f"Unexpected error during registration: {e}")
        return render_template_string(LOGIN_TEMPLATE, 
                                    message=f"An unexpected error occurred. Please try again.", 
                                    message_type="error",
                                    request=request)

@app.route('/api/login', methods=['POST'])
def api_login():
    """API endpoint for user registration with improved error handling"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No JSON data provided'}), 400
            
        if 'username' not in data or 'password' not in data:
            return jsonify({'success': False, 'message': 'Username and password required'}), 400
        
        username = data['username'].strip()
        password = data['password'].strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password cannot be empty'}), 400
        
        success, message = add_user(username, password, email, phone)
        if success:
            logger.info(f"API registration successful for user: {username}")
            return jsonify({'success': True, 'message': f'Registration successful for {username}'})
        else:
            logger.warning(f"API registration failed for user: {username} - {message}")
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        logger.error(f"API registration error: {e}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

def safe_convert_to_json(value):
    """Safely convert database values to JSON-serializable format"""
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return f"<binary data: {len(value)} bytes>"
    elif isinstance(value, (int, float, str, bool)) or value is None:
        return value
    else:
        return str(value)

@app.route('/debug')
def debug_info():
    """Debug endpoint to check database connection and data"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'No database connection', 'db_config': {
            'host': os.environ.get('DB_HOST', 'Not set'),
            'port': os.environ.get('DB_PORT', 'Not set'),
            'database': os.environ.get('DB_NAME', 'Not set'),
            'user': os.environ.get('DB_USER', 'Not set')
        }}), 500
    
    cursor = None
    try:
        cursor = connection.cursor(buffered=True)
        
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        cursor.execute("DESCRIBE User_info")
        columns = cursor.fetchall()
        
        cursor.execute("SELECT user_id, user_name, 'HIDDEN' as password, email, phone FROM User_info LIMIT 5")
        sample_data = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) FROM User_info")
        user_count = cursor.fetchone()[0]
        
        safe_tables = [safe_convert_to_json(table[0]) for table in tables]
        safe_columns = [{'Field': safe_convert_to_json(col[0]), 
                        'Type': safe_convert_to_json(col[1]), 
                        'Null': safe_convert_to_json(col[2]), 
                        'Key': safe_convert_to_json(col[3])} for col in columns]
        safe_users = [{'user_id': safe_convert_to_json(row[0]), 
                      'user_name': safe_convert_to_json(row[1]), 
                      'password': safe_convert_to_json(row[2]), 
                      'email': safe_convert_to_json(row[3]), 
                      'phone': safe_convert_to_json(row[4])} for row in sample_data]
        
        return jsonify({
            'database_connected': True,
            'tables': safe_tables,
            'user_info_columns': safe_columns,
            'sample_users': safe_users,
            'total_users': safe_convert_to_json(user_count),
            'db_config': {
                'host': os.environ.get('DB_HOST', 'Not set'),
                'port': os.environ.get('DB_PORT', 'Not set'),
                'database': os.environ.get('DB_NAME', 'Not set'),
                'user': os.environ.get('DB_USER', 'Not set')
            }
        })
        
    except Error as e:
        logger.error(f"Debug endpoint database error: {e}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        logger.error(f"Debug endpoint unexpected error: {e}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

@app.route('/health')
def health_check():
    """Health check endpoint with improved error handling"""
    connection = get_db_connection()
    if connection:
        cursor = None
        try:
            cursor = connection.cursor(buffered=True)
            cursor.execute("SELECT COUNT(*) FROM User_info")
            count = cursor.fetchone()[0]
            
            return jsonify({
                'status': 'healthy', 
                'database': 'connected',
                'users_count': safe_convert_to_json(count),
                'timestamp': safe_convert_to_json(request.environ.get('REQUEST_TIME', 'unknown'))
            })
        except Error as e:
            logger.error(f"Health check database error: {e}")
            return jsonify({
                'status': 'unhealthy', 
                'database': 'connected but query failed',
                'error': str(e)
            }), 500
        except Exception as e:
            logger.error(f"Health check unexpected error: {e}")
            return jsonify({
                'status': 'unhealthy', 
                'database': 'connected but unexpected error',
                'error': str(e)
            }), 500
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
    else:
        return jsonify({
            'status': 'unhealthy', 
            'database': 'disconnected',
            'message': 'Could not establish database connection'
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("Starting Flask application...")
    
    required_env_vars = ['DB_HOST', 'DB_USER', 'DB_PASSWORD']
    missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.warning(f"Missing environment variables: {missing_vars}")
        logger.warning("Application may not function properly without proper database configuration")
    
    connection = get_db_connection()
    if connection:
        logger.info("Database connection successful!")
        connection.close()
    else:
        logger.warning("Warning: Could not connect to database")
        logger.warning("Please check your environment variables:")
        logger.warning(f"DB_HOST: {os.environ.get('DB_HOST', 'Not set')}")
        logger.warning(f"DB_PORT: {os.environ.get('DB_PORT', 'Not set')}")
        logger.warning(f"DB_NAME: {os.environ.get('DB_NAME', 'Not set')}")
        logger.warning(f"DB_USER: {os.environ.get('DB_USER', 'Not set')}")
    
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting server on port {port}")
    app.run(debug=True, host='0.0.0.0', port=port)
