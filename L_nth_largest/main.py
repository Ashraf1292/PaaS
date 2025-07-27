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
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
    animation: gradientShift 15s ease infinite;
    position: relative;
}

body::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
        radial-gradient(circle at 30% 20%, rgba(255, 255, 255, 0.15) 0%, transparent 50%),
        radial-gradient(circle at 70% 80%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
    pointer-events: none;
}

@keyframes gradientShift {
    0%, 100% { 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%); 
    }
    33% { 
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 25%, #ff8e53 50%, #ff6b9d 75%, #c44569 100%); 
    }
    66% { 
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 25%, #667eea 50%, #764ba2 75%, #f093fb 100%); 
    }
}

.container {
    background: rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(25px);
    padding: 60px;
    border-radius: 30px;
    box-shadow: 
        0 30px 60px rgba(0, 0, 0, 0.2),
        inset 0 1px 0 rgba(255, 255, 255, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.3);
    max-width: 750px;
    width: 100%;
    text-align: center;
    position: relative;
    overflow: hidden;
    transform: translateY(0);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.container:hover {
    transform: translateY(-8px);
    box-shadow: 
        0 40px 80px rgba(0, 0, 0, 0.25),
        inset 0 1px 0 rgba(255, 255, 255, 0.5);
}

.container::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.15), transparent);
    transform: rotate(45deg);
    animation: shimmer 4s linear infinite;
}

@keyframes shimmer {
    0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
    100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
}

h1 {
    color: #fff;
    margin-bottom: 15px;
    font-size: 3.2em;
    font-weight: 800;
    text-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    position: relative;
    z-index: 2;
    letter-spacing: -2px;
}

h1::after {
    content: '';
    position: absolute;
    bottom: -10px;
    left: 50%;
    transform: translateX(-50%);
    width: 80px;
    height: 6px;
    background: linear-gradient(90deg, rgba(255, 255, 255, 0.8), rgba(255, 255, 255, 0.4));
    border-radius: 3px;
    box-shadow: 0 2px 10px rgba(255, 255, 255, 0.3);
}

.subtitle {
    color: rgba(255, 255, 255, 0.85);
    font-size: 1.2em;
    margin-bottom: 50px;
    font-weight: 400;
    position: relative;
    z-index: 2;
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

form {
    position: relative;
    z-index: 2;
}

.input-group {
    margin-bottom: 30px;
    text-align: left;
}

label {
    display: block;
    margin-bottom: 12px;
    color: rgba(255, 255, 255, 0.9);
    font-size: 1.2em;
    font-weight: 600;
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

input[type="text"], input[type="number"] {
    width: 100%;
    padding: 20px 25px;
    font-size: 1.2em;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 15px;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    background: rgba(255, 255, 255, 0.25);
    backdrop-filter: blur(10px);
    color: #fff;
    font-weight: 500;
}

input[type="text"]::placeholder, input[type="number"]::placeholder {
    color: rgba(255, 255, 255, 0.6);
}

input[type="text"]:focus, input[type="number"]:focus {
    outline: none;
    border-color: rgba(255, 255, 255, 0.6);
    box-shadow: 
        0 0 30px rgba(255, 255, 255, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.4);
    transform: translateY(-3px) scale(1.02);
    background: rgba(255, 255, 255, 0.35);
}

.form-row {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 25px;
    align-items: end;
}

.btn {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.3) 0%, rgba(255, 255, 255, 0.2) 100%);
    backdrop-filter: blur(15px);
    color: white;
    border: 2px solid rgba(255, 255, 255, 0.4);
    padding: 20px 45px;
    font-size: 1.2em;
    border-radius: 25px;
    cursor: pointer;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    box-shadow: 0 10px 30px rgba(255, 255, 255, 0.2);
    position: relative;
    overflow: hidden;
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.btn::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
    transition: left 0.6s;
}

.btn:hover::before {
    left: 100%;
}

.btn:hover {
    transform: translateY(-4px) scale(1.05);
    box-shadow: 0 20px 40px rgba(255, 255, 255, 0.3);
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.4) 0%, rgba(255, 255, 255, 0.3) 100%);
    border-color: rgba(255, 255, 255, 0.6);
}

.btn:active {
    transform: translateY(-2px) scale(1.02);
}

.result {
    margin-top: 50px;
    padding: 30px;
    border-radius: 20px;
    position: relative;
    z-index: 2;
    animation: slideUp 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255, 255, 255, 0.3);
}

@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(40px) scale(0.95);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

.result.success {
    background: linear-gradient(135deg, rgba(76, 175, 80, 0.25), rgba(139, 195, 74, 0.25));
    border-color: rgba(76, 175, 80, 0.6);
    color: #fff;
    box-shadow: 0 15px 35px rgba(76, 175, 80, 0.2);
}

.result.error {
    background: linear-gradient(135deg, rgba(244, 67, 54, 0.25), rgba(255, 87, 34, 0.25));
    border-color: rgba(244, 67, 54, 0.6);
    color: #fff;
    box-shadow: 0 15px 35px rgba(244, 67, 54, 0.2);
}

.result h3 {
    font-size: 1.6em;
    margin-bottom: 15px;
    font-weight: 700;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.result-value {
    font-size: 2.8em;
    font-weight: 900;
    text-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    margin: 10px 0;
}

.numbers-display {
    margin-top: 25px;
    padding: 20px;
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    font-size: 1em;
    color: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.sorted-numbers {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    justify-content: center;
    margin-top: 15px;
}

.number-item {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.3), rgba(255, 255, 255, 0.2));
    backdrop-filter: blur(10px);
    color: white;
    padding: 8px 16px;
    border-radius: 25px;
    font-weight: 700;
    font-size: 1em;
    box-shadow: 0 4px 15px rgba(255, 255, 255, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.3);
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.number-item:hover {
    transform: translateY(-2px) scale(1.05);
    box-shadow: 0 8px 25px rgba(255, 255, 255, 0.3);
}

.number-item.highlight {
    background: linear-gradient(135deg, rgba(76, 175, 80, 0.8), rgba(139, 195, 74, 0.8));
    box-shadow: 0 8px 25px rgba(76, 175, 80, 0.4);
    transform: scale(1.15);
    animation: highlightPulse 0.8s ease;
}

@keyframes highlightPulse {
    0%, 100% { transform: scale(1.15); }
    50% { transform: scale(1.25); box-shadow: 0 12px 35px rgba(76, 175, 80, 0.6); }
}

.placeholder-text {
    color: rgba(255, 255, 255, 0.6);
    font-style: italic;
}

@media (max-width: 600px) {
    .container {
        padding: 40px 25px;
        margin: 10px;
        border-radius: 20px;
    }
    
    h1 {
        font-size: 2.5em;
        margin-bottom: 10px;
    }
    
    .subtitle {
        font-size: 1.1em;
        margin-bottom: 40px;
    }
    
    .form-row {
        grid-template-columns: 1fr;
        gap: 20px;
    }
    
    .result-value {
        font-size: 2.2em;
    }

    input[type="text"], input[type="number"] {
        padding: 18px 20px;
        font-size: 1.1em;
    }

    .btn {
        padding: 18px 35px;
        font-size: 1.1em;
    }
}

.info-box {
    background: rgba(33, 150, 243, 0.2);
    backdrop-filter: blur(10px);
    border-left: 4px solid rgba(33, 150, 243, 0.8);
    padding: 20px;
    margin: 25px 0;
    border-radius: 10px;
    color: rgba(255, 255, 255, 0.9);
    font-size: 1em;
    text-align: left;
    border: 1px solid rgba(33, 150, 243, 0.3);
    box-shadow: 0 8px 25px rgba(33, 150, 243, 0.15);
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
