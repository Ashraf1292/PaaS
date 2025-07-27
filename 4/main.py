from flask import Flask, request, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nth Largest Number Finder</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 25%, #ff8e53 50%, #ff6b9d 75%, #c44569 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            animation: gradientShift 10s ease infinite;
        }

        @keyframes gradientShift {
            0%, 100% { background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 25%, #ff8e53 50%, #ff6b9d 75%, #c44569 100%); }
            50% { background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%); }
        }

        .container {
            background: rgba(255, 255, 255, 0.95);
            padding: 50px;
            border-radius: 25px;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            max-width: 700px;
            width: 100%;
            text-align: center;
            position: relative;
            overflow: hidden;
        }

        .container::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.1), transparent);
            transform: rotate(45deg);
            animation: shimmer 3s linear infinite;
        }

        @keyframes shimmer {
            0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
            100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
        }

        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2.8em;
            font-weight: 300;
            background: linear-gradient(135deg, #ff6b6b, #ee5a52, #ff8e53);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            position: relative;
            z-index: 1;
        }

        .subtitle {
            color: #666;
            font-size: 1.1em;
            margin-bottom: 40px;
            font-weight: 400;
            position: relative;
            z-index: 1;
        }

        form {
            position: relative;
            z-index: 1;
        }

        .input-group {
            margin-bottom: 25px;
            text-align: left;
        }

        label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-size: 1.1em;
            font-weight: 600;
        }

        input[type="text"], input[type="number"] {
            width: 100%;
            padding: 15px 20px;
            font-size: 1.1em;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            transition: all 0.3s ease;
            background: rgba(255, 255, 255, 0.9);
            box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.05);
        }

        input[type="text"]:focus, input[type="number"]:focus {
            outline: none;
            border-color: #ff6b6b;
            box-shadow: 0 0 20px rgba(255, 107, 107, 0.3);
            transform: translateY(-2px);
            background: rgba(255, 255, 255, 1);
        }

        .form-row {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
            align-items: end;
        }

        .btn {
            background: linear-gradient(135deg, #ff6b6b, #ee5a52);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 1.2em;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4);
            position: relative;
            overflow: hidden;
        }

        .btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: left 0.5s;
        }

        .btn:hover::before {
            left: 100%;
        }

        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 35px rgba(255, 107, 107, 0.5);
        }

        .btn:active {
            transform: translateY(-1px);
        }

        .result {
            margin-top: 40px;
            padding: 25px;
            border-radius: 15px;
            position: relative;
            z-index: 1;
            animation: slideUp 0.5s ease;
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

        .result.success {
            background: linear-gradient(135deg, rgba(76, 175, 80, 0.1), rgba(139, 195, 74, 0.1));
            border: 2px solid #4caf50;
            color: #2e7d32;
        }

        .result.error {
            background: linear-gradient(135deg, rgba(244, 67, 54, 0.1), rgba(255, 87, 34, 0.1));
            border: 2px solid #f44336;
            color: #c62828;
        }

        .result h3 {
            font-size: 1.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }

        .result-value {
            font-size: 2.5em;
            font-weight: 800;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
        }

        .numbers-display {
            margin-top: 20px;
            padding: 15px;
            background: rgba(255, 255, 255, 0.7);
            border-radius: 10px;
            font-size: 0.9em;
            color: #666;
        }

        .sorted-numbers {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            justify-content: center;
            margin-top: 10px;
        }

        .number-item {
            background: linear-gradient(135deg, #ff6b6b, #ee5a52);
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9em;
            box-shadow: 0 2px 8px rgba(255, 107, 107, 0.3);
        }

        .number-item.highlight {
            background: linear-gradient(135deg, #4caf50, #66bb6a);
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.4);
            transform: scale(1.1);
            animation: pulse 0.5s ease;
        }

        @keyframes pulse {
            0%, 100% { transform: scale(1.1); }
            50% { transform: scale(1.2); }
        }

        .placeholder-text {
            color: #999;
            font-style: italic;
        }

        @media (max-width: 600px) {
            .container {
                padding: 30px 20px;
                margin: 10px;
            }
            
            h1 {
                font-size: 2.2em;
            }
            
            .form-row {
                grid-template-columns: 1fr;
                gap: 20px;
            }
            
            .result-value {
                font-size: 2em;
            }
        }

        .info-box {
            background: rgba(33, 150, 243, 0.1);
            border-left: 4px solid #2196f3;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
            color: #1976d2;
            font-size: 0.9em;
            text-align: left;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Nth Largest Finder</h1>
        <p class="subtitle">Discover the Nth largest number from your dataset</p>
        
        <div class="info-box">
            <strong>How it works:</strong> Enter numbers separated by commas, specify which largest number you want (1st, 2nd, 3rd, etc.), and we'll find it for you!
        </div>
        
        <form method="POST">
            <div class="form-row">
                <div class="input-group">
                    <label for="numbers">📊 Enter Numbers:</label>
                    <input type="text" 
                           id="numbers" 
                           name="numbers" 
                           placeholder="e.g., 45, 23, 78, 12, 89, 34, 67" 
                           value="{{ request.form.numbers if request.form.numbers else '' }}"
                           required>
                </div>
                
                <div class="input-group">
                    <label for="n">🎯 Find Nth Largest:</label>
                    <input type="number" 
                           id="n" 
                           name="n" 
                           min="1" 
                           placeholder="e.g., 3"
                           value="{{ request.form.n if request.form.n else '' }}"
                           required>
                </div>
            </div>
            
            <button type="submit" class="btn">Find Number</button>
        </form>

        {% if result is not none %}
            <div class="result {{ 'success' if result != 'Error' and 'Error' not in result|string else 'error' }}">
                {% if 'Error' in result|string %}
                    <h3>❌ Error Occurred</h3>
                    <p>{{ result }}</p>
                {% elif result == "N is too large" %}
                    <h3>⚠️ Invalid Input</h3>
                    <p>The value of N ({{ n }}) is larger than the number of elements provided.</p>
                {% else %}
                    <h3>✅ Result Found!</h3>
                    <p>The <strong>{{ n }}{{ 'st' if n == 1 else 'nd' if n == 2 else 'rd' if n == 3 else 'th' }}</strong> largest number is:</p>
                    <div class="result-value">{{ result }}</div>
                    
                    {% if sorted_numbers %}
                        <div class="numbers-display">
                            <p><strong>Numbers sorted in descending order:</strong></p>
                            <div class="sorted-numbers">
                                {% for num in sorted_numbers %}
                                    <span class="number-item {{ 'highlight' if loop.index == n else '' }}">{{ num }}</span>
                                {% endfor %}
                            </div>
                        </div>
                    {% endif %}
                {% endif %}
            </div>
        {% endif %}
    </div>

    <script>
        // Add some interactive effects
        document.addEventListener('DOMContentLoaded', function() {
            const inputs = document.querySelectorAll('input');
            inputs.forEach(input => {
                input.addEventListener('focus', function() {
                    this.parentElement.style.transform = 'scale(1.02)';
                });
                
                input.addEventListener('blur', function() {
                    this.parentElement.style.transform = 'scale(1)';
                });
            });

            // Auto-focus on first input
            document.getElementById('numbers').focus();
        });
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    n = None
    sorted_numbers = None
    
    if request.method == 'POST':
        numbers = request.form['numbers']
        n = int(request.form['n'])
        
        try:
            # Parse and validate numbers
            num_list = [int(x.strip()) for x in numbers.split(',') if x.strip()]
            
            if not num_list:
                result = "Error: Please enter at least one valid number"
            elif n > len(num_list):
                result = "N is too large"
            else:
                # Sort in descending order and find nth largest
                sorted_list = sorted(num_list, reverse=True)
                result = sorted_list[n-1]
                sorted_numbers = sorted_list
                
        except ValueError:
            result = "Error: Please enter valid numbers separated by commas"
        except Exception as e:
            result = f"Error: {str(e)}"
    
    return render_template_string(HTML_TEMPLATE, 
                                result=result, 
                                n=n, 
                                sorted_numbers=sorted_numbers,
                                request=request)

@app.route('/health')
def health_check():
    return {"status": "healthy"}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
