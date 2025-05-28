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
    'port': int(os.environ.get('DB_PORT', 3306)),  # Changed default port to standard MySQL
    'database': os.environ.get('DB_NAME', 'defaultdb'),  # Set default database name
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'ssl_disabled': False,
    'ssl_verify_cert': False,  # Aiven compatibility
    'autocommit': True,
    'use_unicode': True,
    'charset': 'utf8mb4',
    'connect_timeout': 60,  # Added connection timeout
    'sql_mode': 'STRICT_TRANS_TABLES'  # Added for better data integrity
}

def get_db_connection():
    """Create and return a database connection with improved error handling"""
    try:
        # Remove None values from config to avoid connection issues
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
        cursor = connection.cursor(buffered=True)  # Use buffered cursor
        
        # Log validation attempt (without password for security)
        logger.info(f"Attempting to validate user: '{username}'")
        if email:
            logger.info(f"Email provided: '{email}'")
        if phone:
            logger.info(f"Phone provided: '{phone}'")
        
        # Debug: Check table structure first
        try:
            cursor.execute("DESCRIBE User_info")
            columns = cursor.fetchall()
            logger.info(f"Table structure: {columns}")
        except Error as e:
            logger.error(f"Error checking table structure: {e}")
        
        # Build dynamic query based on provided information
        base_query = "SELECT user_id, user_name, password, email, phone FROM User_info WHERE user_name = %s AND password = %s"
        params = [username, password]
        
        # Add email check if provided and not empty
        if email and email.strip():
            base_query += " AND email = %s"
            params.append(email.strip())
        
        # Add phone check if provided and not empty
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
            # Try case-insensitive search for username and email
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

# HTML template for login form
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced User Login Validation</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            max-width: 500px; 
            margin: 50px auto; 
            padding: 20px; 
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .form-group { margin-bottom: 20px; }
        label { 
            display: block; 
            margin-bottom: 8px; 
            font-weight: bold; 
            color: #333;
        }
        input[type="text"], input[type="password"], input[type="email"], input[type="tel"] { 
            width: 100%; 
            padding: 12px; 
            border: 2px solid #ddd; 
            border-radius: 6px; 
            font-size: 16px;
            box-sizing: border-box;
            transition: border-color 0.3s;
        }
        input:focus {
            outline: none;
            border-color: #4CAF50;
        }
        button { 
            background-color: #4CAF50; 
            color: white; 
            padding: 12px 20px; 
            border: none; 
            border-radius: 6px; 
            cursor: pointer; 
            width: 100%; 
            font-size: 16px;
            font-weight: bold;
            transition: background-color 0.3s;
        }
        button:hover { background-color: #45a049; }
        button:active { background-color: #3d8b40; }
        .message { 
            padding: 15px; 
            margin: 15px 0; 
            border-radius: 6px; 
            font-weight: bold;
        }
        .success { 
            background-color: #d4edda; 
            color: #155724; 
            border: 2px solid #c3e6cb; 
        }
        .error { 
            background-color: #f8d7da; 
            color: #721c24; 
            border: 2px solid #f5c6cb; 
        }
        .optional { 
            color: #666; 
            font-size: 0.9em; 
            font-style: italic; 
            margin-top: 5px;
        }
        .divider { 
            margin: 25px 0; 
            border-top: 2px solid #eee; 
            padding-top: 20px; 
        }
        .info-box { 
            background-color: #e3f2fd; 
            color: #1565c0; 
            padding: 20px; 
            border-radius: 6px; 
            margin-bottom: 25px; 
            border-left: 5px solid #2196f3; 
        }
        .required { color: #e74c3c; font-weight: bold; }
        h2 { color: #333; text-align: center; margin-bottom: 30px; }
        .footer-info { 
            margin-top: 30px; 
            padding-top: 20px; 
            border-top: 1px solid #eee; 
            color: #666; 
        }
    </style>
</head>
<body>
    <div class="container">
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
                <label for="username">Username <span class="required">*</span></label>
                <input type="text" id="username" name="username" required 
                       value="{{ request.form.username if request.form.username else '' }}"
                       placeholder="Enter your username">
            </div>
            
            <div class="form-group">
                <label for="password">Password <span class="required">*</span></label>
                <input type="password" id="password" name="password" required
                       placeholder="Enter your password">
            </div>
            
            <div class="divider">
                <strong>Additional Verification</strong>
                <div class="optional">Optional - provides enhanced security</div>
            </div>
            
            <div class="form-group">
                <label for="email">Email Address</label>
                <input type="email" id="email" name="email" 
                       placeholder="your.email@example.com"
                       value="{{ request.form.email if request.form.email else '' }}">
                <div class="optional">Leave blank if you don't want to verify email</div>
            </div>
            
            <div class="form-group">
                <label for="phone">Phone Number</label>
                <input type="tel" id="phone" name="phone" 
                       placeholder="e.g., +1234567890"
                       value="{{ request.form.phone if request.form.phone else '' }}">
                <div class="optional">Leave blank if you don't want to verify phone</div>
            </div>
            
            <button type="submit">Validate Login</button>
        </form>
        
        <div class="footer-info">
            <p><strong>Test with your existing database credentials</strong></p>
            <p><small><span class="required">*</span> Required fields | Additional fields are optional but provide extra security</small></p>
            <p><small>Visit <a href="/debug">/debug</a> to check database connection and data</small></p>
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
        
        # Validate required fields
        if not username or not password:
            return render_template_string(LOGIN_TEMPLATE, 
                                        message="Please enter both username and password", 
                                        message_type="error",
                                        request=request)
        
        # Check database connection first
        connection = get_db_connection()
        if not connection:
            logger.error("Database connection failed during login attempt")
            return render_template_string(LOGIN_TEMPLATE, 
                                        message="Database connection failed. Please check your environment variables and try again.", 
                                        message_type="error",
                                        request=request)
        connection.close()
        
        # Attempt user validation
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
        
        # Check if table exists
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        # Get table structure
        cursor.execute("DESCRIBE User_info")
        columns = cursor.fetchall()
        
        # Get sample data (first 5 rows, hiding passwords)
        cursor.execute("SELECT user_id, user_name, 'HIDDEN' as password, email, phone FROM User_info LIMIT 5")
        sample_data = cursor.fetchall()
        
        # Count total users
        cursor.execute("SELECT COUNT(*) FROM User_info")
        user_count = cursor.fetchone()[0]
        
        # Safely convert all data to JSON-serializable format
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

# Initialize database connection check on startup
if __name__ == '__main__':
    logger.info("Starting Flask application...")
    
    # Check environment variables
    required_env_vars = ['DB_HOST', 'DB_USER', 'DB_PASSWORD']
    missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.warning(f"Missing environment variables: {missing_vars}")
        logger.warning("Application may not function properly without proper database configuration")
    
    # Test database connection
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
    
    # Start the application
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting server on port {port}")
    app.run(debug=True, host='0.0.0.0', port=port)
