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

# Modern HTML template for login form
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SecureAuth - Login Portal</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            overflow-x: hidden;
        }
        
        /* Animated background particles */
        body::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image: 
                radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 40% 40%, rgba(120, 119, 198, 0.2) 0%, transparent 50%);
            animation: float 20s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-20px); }
        }
        
        .container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 24px;
            padding: 48px;
            width: 100%;
            max-width: 480px;
            box-shadow: 
                0 32px 64px rgba(0, 0, 0, 0.12),
                0 0 0 1px rgba(255, 255, 255, 0.05);
            position: relative;
            z-index: 1;
            animation: slideUp 0.8s ease-out;
        }
        
        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .logo {
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 24px;
            position: relative;
            overflow: hidden;
        }
        
        .logo::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            animation: shine 2s infinite;
        }
        
        @keyframes shine {
            0% { left: -100%; }
            100% { left: 100%; }
        }
        
        .logo i {
            color: white;
            font-size: 32px;
            z-index: 1;
        }
        
        h1 {
            font-size: 32px;
            font-weight: 700;
            color: #1a202c;
            margin-bottom: 8px;
            letter-spacing: -0.5px;
        }
        
        .subtitle {
            color: #64748b;
            font-size: 16px;
            font-weight: 400;
        }
        
        .info-banner {
            background: linear-gradient(135deg, #e0e7ff, #c7d2fe);
            border: 1px solid #a5b4fc;
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 32px;
            position: relative;
            overflow: hidden;
        }
        
        .info-banner::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, #667eea, #764ba2);
        }
        
        .info-banner h3 {
            color: #3730a3;
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .info-banner p {
            color: #4338ca;
            font-size: 14px;
            line-height: 1.5;
        }
        
        .form-section {
            margin-bottom: 32px;
        }
        
        .section-title {
            font-size: 18px;
            font-weight: 600;
            color: #1a202c;
            margin-bottom: 4px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .section-subtitle {
            color: #64748b;
            font-size: 14px;
            margin-bottom: 20px;
        }
        
        .form-group {
            margin-bottom: 24px;
            position: relative;
        }
        
        .input-wrapper {
            position: relative;
        }
        
        .input-icon {
            position: absolute;
            left: 16px;
            top: 50%;
            transform: translateY(-50%);
            color: #64748b;
            font-size: 18px;
            z-index: 2;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #374151;
            font-size: 14px;
        }
        
        .required {
            color: #ef4444;
            margin-left: 4px;
        }
        
        input[type="text"], 
        input[type="password"], 
        input[type="email"], 
        input[type="tel"] {
            width: 100%;
            padding: 16px 16px 16px 52px;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            font-size: 16px;
            background: rgba(255, 255, 255, 0.8);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
        }
        
        input:focus {
            outline: none;
            border-color: #667eea;
            background: rgba(255, 255, 255, 1);
            box-shadow: 
                0 0 0 4px rgba(102, 126, 234, 0.1),
                0 4px 12px rgba(102, 126, 234, 0.15);
            transform: translateY(-2px);
        }
        
        input:focus + .input-icon {
            color: #667eea;
        }
        
        .optional-hint {
            color: #64748b;
            font-size: 12px;
            margin-top: 4px;
            font-style: italic;
        }
        
        .divider {
            display: flex;
            align-items: center;
            margin: 32px 0 24px;
            gap: 16px;
        }
        
        .divider::before,
        .divider::after {
            content: '';
            flex: 1;
            height: 1px;
            background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
        }
        
        .divider-text {
            color: #64748b;
            font-size: 14px;
            font-weight: 500;
            white-space: nowrap;
        }
        
        .submit-btn {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        
        .submit-btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }
        
        .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 
                0 12px 24px rgba(102, 126, 234, 0.3),
                0 0 0 1px rgba(255, 255, 255, 0.1);
        }
        
        .submit-btn:hover::before {
            left: 100%;
        }
        
        .submit-btn:active {
            transform: translateY(0);
        }
        
        .message {
            padding: 16px 20px;
            border-radius: 12px;
            margin-bottom: 24px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 12px;
            animation: slideIn 0.5s ease-out;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(-20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        .message i {
            font-size: 18px;
        }
        
        .success {
            background: linear-gradient(135deg, #d1fae5, #a7f3d0);
            color: #065f46;
            border: 1px solid #86efac;
        }
        
        .error {
            background: linear-gradient(135deg, #fee2e2, #fecaca);
            color: #991b1b;
            border: 1px solid #fca5a5;
        }
        
        .footer {
            margin-top: 32px;
            padding-top: 24px;
            border-top: 1px solid #e2e8f0;
            text-align: center;
        }
        
        .footer-text {
            color: #64748b;
            font-size: 14px;
            margin-bottom: 12px;
        }
        
        .debug-link {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            color: #667eea;
            text-decoration: none;
            font-size: 14px;
            font-weight: 500;
            padding: 8px 16px;
            border-radius: 8px;
            background: rgba(102, 126, 234, 0.1);
            transition: all 0.3s ease;
        }
        
        .debug-link:hover {
            background: rgba(102, 126, 234, 0.2);
            transform: translateY(-1px);
        }
        
        /* Responsive design */
        @media (max-width: 640px) {
            .container {
                margin: 16px;
                padding: 32px 24px;
            }
            
            h1 {
                font-size: 28px;
            }
            
            .logo {
                width: 64px;
                height: 64px;
            }
            
            .logo i {
                font-size: 24px;
            }
        }
        
        /* Loading state */
        .submit-btn:disabled {
            opacity: 0.7;
            cursor: not-allowed;
            transform: none;
        }
        
        .loading {
            position: relative;
        }
        
        .loading::after {
            content: '';
            position: absolute;
            width: 16px;
            height: 16px;
            border: 2px solid transparent;
            border-top: 2px solid currentColor;
            border-radius: 50%;
            right: 16px;
            top: 50%;
            transform: translateY(-50%);
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            to {
                transform: translateY(-50%) rotate(360deg);
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">
                <i class="fas fa-shield-alt"></i>
            </div>
            <h1>SecureAuth</h1>
            <p class="subtitle">Multi-Factor Authentication Portal</p>
        </div>
        
        <div class="info-banner">
            <h3><i class="fas fa-info-circle"></i>Enhanced Security</h3>
            <p>Enter your credentials with optional email and phone verification for additional security layers.</p>
        </div>
        
        {% if message %}
            <div class="message {{ message_type }}">
                {% if message_type == 'success' %}
                    <i class="fas fa-check-circle"></i>
                {% else %}
                    <i class="fas fa-exclamation-triangle"></i>
                {% endif %}
                {{ message }}
            </div>
        {% endif %}
        
        <form method="POST" action="/login" id="loginForm">
            <div class="form-section">
                <div class="section-title">
                    <i class="fas fa-user-lock"></i>
                    Required Credentials
                </div>
                <div class="section-subtitle">Please provide your username and password</div>
                
                <div class="form-group">
                    <label for="username">Username <span class="required">*</span></label>
                    <div class="input-wrapper">
                        <input type="text" id="username" name="username" required 
                               value="{{ request.form.username if request.form.username else '' }}"
                               placeholder="Enter your username">
                        <i class="fas fa-user input-icon"></i>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="password">Password <span class="required">*</span></label>
                    <div class="input-wrapper">
                        <input type="password" id="password" name="password" required
                               placeholder="Enter your password">
                        <i class="fas fa-lock input-icon"></i>
                    </div>
                </div>
            </div>
            
            <div class="divider">
                <span class="divider-text">Optional Verification</span>
            </div>
            
            <div class="form-section">
                <div class="section-title">
                    <i class="fas fa-shield-check"></i>
                    Additional Security
                </div>
                <div class="section-subtitle">Optional fields for enhanced authentication</div>
                
                <div class="form-group">
                    <label for="email">Email Address</label>
                    <div class="input-wrapper">
                        <input type="email" id="email" name="email" 
                               placeholder="your.email@example.com"
                               value="{{ request.form.email if request.form.email else '' }}">
                        <i class="fas fa-envelope input-icon"></i>
                    </div>
                    <div class="optional-hint">Leave blank to skip email verification</div>
                </div>
                
                <div class="form-group">
                    <label for="phone">Phone Number</label>
                    <div class="input-wrapper">
                        <input type="tel" id="phone" name="phone" 
                               placeholder="+1234567890"
                               value="{{ request.form.phone if request.form.phone else '' }}">
                        <i class="fas fa-phone input-icon"></i>
                    </div>
                    <div class="optional-hint">Leave blank to skip phone verification</div>
                </div>
            </div>
            
            <button type="submit" class="submit-btn" id="submitBtn">
                <i class="fas fa-sign-in-alt" style="margin-right: 8px;"></i>
                Authenticate
            </button>
        </form>
        
        <div class="footer">
            <p class="footer-text">
                <i class="fas fa-database" style="margin-right: 4px;"></i>
                Connected to secure database
            </p>
            <a href="/debug" class="debug-link">
                <i class="fas fa-bug"></i>
                System Debug
            </a>
        </div>
    </div>
    
    <script>
        // Add loading state to form submission
        document.getElementById('loginForm').addEventListener('submit', function() {
            const submitBtn = document.getElementById('submitBtn');
            submitBtn.disabled = true;
            submitBtn.classList.add('loading');
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin" style="margin-right: 8px;"></i>Authenticating...';
        });
        
        // Add floating label effect
        const inputs = document.querySelectorAll('input');
        inputs.forEach(input => {
            input.addEventListener('focus', function() {
                this.parentElement.classList.add('focused');
            });
            
            input.addEventListener('blur', function() {
                if (!this.value) {
                    this.parentElement.classList.remove('focused');
                }
            });
            
            // Initialize state
            if (input.value) {
                input.parentElement.classList.add('focused');
            }
        });
    </script>
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
