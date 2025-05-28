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

def validate_user(username, password, email=None, phone=None):
    """Validate user credentials against existing database with additional info"""
    connection = get_db_connection()
    if not connection:
        logger.error("No database connection available")
        return False
    
    cursor = None
    try:
        cursor = connection.cursor(buffered=True)
        
        logger.info(f"Attempting to validate user: '{username}'")
        if email:
            logger.info(f"Email provided: '{email}'")
        if phone:
            logger.info(f"Phone provided: '{phone}'")
        
        try:
            cursor.execute("DESCRIBE User_info")
            columns = cursor.fetchall()
            logger.info(f"Table structure: {columns}")
        except Error as e:
            logger.error(f"Error checking table structure: {e}")
        
        base_query = "SELECT user_id, user_name, password, email, phone FROM User_info WHERE user_name = %s AND password = %s"
        params = [username, password]
        
        if email and email.strip():
            base_query += " AND email = %s"
            params.append(email.strip())
        
        if phone and phone.strip():
            base_query += " AND phone = %s"
            params.append(phone.strip())
        
        logger.info(f"Executing query with {len(params)} parameters")
        
        cursor.execute(base_query, params)
        result = cursor.fetchone()
        
        if result:
            logger.info("User validation successful!")
            return True
        else:
            logger.info("Trying case-insensitive search")
            case_query = "SELECT user_id, user_name, password, email, phone FROM User_info WHERE LOWER(user_name) = LOWER(%s) AND password = %s"
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
                logger.info("User validation successful (case-insensitive)!")
                return True
            else:
                logger.info("No matching user found")
                return False
                
    except Error as e:
        logger.error(f"Database error validating user: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error validating user: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

# HTML template for login form with updated interface
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced User Login Validation</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="min-h-screen bg-gray-100 flex items-center justify-center p-4">
    <div class="w-full max-w-md bg-white rounded-2xl shadow-xl p-8">
        <h2 class="text-2xl font-bold text-center text-gray-800 mb-8">Secure Login</h2>
        
        <div class="bg-blue-50 border-l-4 border-blue-500 p-4 mb-8 rounded-r-lg">
            <p class="text-sm text-blue-800">
                <span class="font-semibold">Multi-Factor Validation:</span> Enter your username and password. 
                Optionally provide email and/or phone number for enhanced security.
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
                       placeholder="Enter your username"
                       class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200">
            </div>
            
            <div>
                <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
                    Password <span class="text-red-500">*</span>
                </label>
                <input type="password" id="password" name="password" required
                       placeholder="Enter your password"
                       class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200">
            </div>
            
            <div class="pt-4 border-t border-gray-200">
                <p class="text-sm font-semibold text-gray-700 mb-2">Additional Verification</p>
                <p class="text-xs text-gray-500 italic mb-4">Optional - enhances security</p>
            </div>
            
            <div>
                <label for="email" class="block text-sm font-medium text-gray-700 mb-2">Email Address</label>
                <input type="email" id="email" name="email"
                       placeholder="your.email@example.com"
                       value="{{ request.form.email if request.form.email else '' }}"
                       class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200">
                <p class="text-xs text-gray-500 mt-1 italic">Leave blank if not verifying email</p>
            </div>
            
            <div>
                <label for="phone" class="block text-sm font-medium text-gray-700 mb-2">Phone Number</label>
                <input type="tel" id="phone" name="phone"
                       placeholder="e.g., +1234567890"
                       value="{{ request.form.phone if request.form.phone else '' }}"
                       class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200">
                <p class="text-xs text-gray-500 mt-1 italic">Leave blank if not verifying phone</p>
            </div>
            
            <button type="submit"
                    class="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-200">
                Validate Login
            </button>
        </form>
        
        <div class="mt-8 pt-6 border-t border-gray-200 text-center text-sm text-gray-600">
            <p class="font-medium">Test with your existing database credentials</p>
            <p class="mt-2"><span class="text-red-500">*</span> Required fields | Additional fields are optional</p>
            <p class="mt-2">Visit <a href="/debug" class="text-blue-600 hover:underline">/debug</a> for database details</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """Display login form"""
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/login', methods=['POST'])
def login():
    """Handle login form submission with improved error handling"""
    try:
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        
        if not username or not password:
            return render_template_string(LOGIN_TEMPLATE, 
                                        message="Please enter both username and password", 
                                        message_type="error",
                                        request=request)
        
        connection = get_db_connection()
        if not connection:
            logger.error("Database connection failed during login attempt")
            return render_template_string(LOGIN_TEMPLATE, 
                                        message="Database connection failed. Please check your environment variables and try again.", 
                                        message_type="error",
                                        request=request)
        connection.close()
        
        if validate_user(username, password, email, phone):
            verification_details = []
            if email:
                verification_details.append(f"email ({email})")
            if phone:
                verification_details.append(f"phone ({phone})")
            
            success_message = f"Login successful! Welcome, {username}!"
            if verification_details:
                success_message += f" Additional verification passed for: {', '.join(verification_details)}"
            
            logger.info(f"Successful login for user: {username}")
            return render_template_string(LOGIN_TEMPLATE, 
                                        message=success_message, 
                                        message_type="success",
                                        request=request)
        else:
            error_message = "Invalid credentials. Please check your username and password."
            if email:
                error_message += " Email verification also failed."
            if phone:
                error_message += " Phone verification also failed."
            
            logger.warning(f"Failed login attempt for user: {username}")
            return render_template_string(LOGIN_TEMPLATE, 
                                        message=error_message, 
                                        message_type="error",
                                        request=request)
            
    except Exception as e:
        logger.error(f"Unexpected error during login: {e}")
        return render_template_string(LOGIN_TEMPLATE, 
                                    message=f"An unexpected error occurred. Please try again.", 
                                    message_type="error",
                                    request=request)

@app.route('/api/login', methods=['POST'])
def api_login():
    """API endpoint for login validation with improved error handling"""
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
        
        if validate_user(username, password, email, phone):
            verification_info = []
            if email:
                verification_info.append('email')
            if phone:
                verification_info.append('phone')
            
            message = f'Login successful for {username}'
            if verification_info:
                message += f' with additional verification: {", ".join(verification_info)}'
            
            logger.info(f"API login successful for user: {username}")
            return jsonify({'success': True, 'message': message})
        else:
            logger.warning(f"API login failed for user: {username}")
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
            
    except Exception as e:
        logger.error(f"API login error: {e}")
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
