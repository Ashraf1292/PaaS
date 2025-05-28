from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Login</title>
    <style>
        /* Reset some default styles */
        * {
            box-sizing: border-box;
        }
        body {
            margin: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea, #764ba2);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            color: #333;
        }
        .login-container {
            background: #fff;
            padding: 2.5rem 3rem;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
            width: 350px;
        }
        .login-container h2 {
            margin-bottom: 1.5rem;
            text-align: center;
            color: #4a148c;
            font-weight: 700;
        }
        label {
            display: block;
            margin-bottom: 0.3rem;
            font-weight: 600;
            color: #555;
        }
        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 0.6rem 0.8rem;
            margin-bottom: 1.2rem;
            border: 1.5px solid #ccc;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }
        input[type="text"]:focus, input[type="password"]:focus {
            border-color: #764ba2;
            outline: none;
            box-shadow: 0 0 6px #a87eff88;
        }
        button {
            width: 100%;
            background-color: #764ba2;
            color: white;
            padding: 0.75rem 0;
            font-size: 1.1rem;
            font-weight: 600;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        button:hover {
            background-color: #5b3580;
        }
        .error-message {
            background-color: #fce4e4;
            color: #b00020;
            padding: 0.7rem 1rem;
            border-radius: 6px;
            margin-bottom: 1rem;
            font-size: 0.9rem;
            text-align: center;
        }
        .footer-text {
            margin-top: 1.5rem;
            text-align: center;
            font-size: 0.85rem;
            color: #888;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <h2>Login to Your Account</h2>
        {% if error %}
        <div class="error-message">{{ error }}</div>
        {% endif %}
        <form method="POST" action="{{ url_for('login') }}">
            <label for="username">Username</label>
            <input type="text" id="username" name="username" required placeholder="Enter username" />

            <label for="password">Password</label>
            <input type="password" id="password" name="password" required placeholder="Enter password" />

            <button type="submit">Log In</button>
        </form>
        <div class="footer-text">
            &copy; 2025 Your Company
        </div>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Example check - replace with your real auth logic
        if username == 'admin' and password == 'secret':
            return redirect(url_for('welcome'))
        else:
            error = "Invalid username or password"
    
    return render_template_string(LOGIN_TEMPLATE, error=error)

@app.route('/welcome')
def welcome():
    return "<h1>Welcome! You have successfully logged in.</h1>"

if __name__ == '__main__':
    app.run(debug=True)
