from flask import Flask, render_template_string

app = Flask(__name__)

# HTML template as a string
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Even Numbers Generator</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .container {
            background: rgba(255, 255, 255, 0.95);
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            max-width: 600px;
            width: 100%;
            text-align: center;
        }

        h1 {
            color: #333;
            margin-bottom: 30px;
            font-size: 2.5em;
            font-weight: 300;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .input-group {
            margin-bottom: 30px;
        }

        label {
            display: block;
            margin-bottom: 10px;
            color: #555;
            font-size: 1.1em;
            font-weight: 500;
        }

        input[type="number"] {
            width: 200px;
            padding: 15px;
            font-size: 1.2em;
            border: 2px solid #ddd;
            border-radius: 10px;
            text-align: center;
            transition: all 0.3s ease;
            background: rgba(255, 255, 255, 0.8);
        }

        input[type="number"]:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 15px rgba(102, 126, 234, 0.3);
            transform: translateY(-2px);
        }

        .btn {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 1.1em;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s ease;
            margin: 10px;
            min-width: 120px;
            font-weight: 500;
        }

        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        }

        .btn:active {
            transform: translateY(-1px);
        }

        .result {
            margin-top: 30px;
            padding: 20px;
            background: rgba(102, 126, 234, 0.1);
            border-radius: 15px;
            border-left: 5px solid #667eea;
            display: none;
        }

        .result.show {
            display: block;
            animation: fadeInUp 0.5s ease;
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .result h3 {
            color: #333;
            margin-bottom: 15px;
            font-size: 1.3em;
        }

        .numbers-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(50px, 1fr));
            gap: 10px;
            margin-top: 15px;
        }

        .number-item {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 10px;
            border-radius: 8px;
            font-weight: bold;
            transition: all 0.3s ease;
        }

        .number-item:hover {
            transform: scale(1.1);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .error {
            background: rgba(255, 87, 87, 0.1);
            border-left: 5px solid #ff5757;
            color: #d63031;
        }

        .loading {
            display: none;
            color: #667eea;
            font-style: italic;
        }

        .loading.show {
            display: block;
        }

        @media (max-width: 480px) {
            .container {
                padding: 20px;
            }
            
            h1 {
                font-size: 2em;
            }
            
            input[type="number"] {
                width: 100%;
                max-width: 200px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>✨ Even Numbers Generator</h1>
        
        <form id="evenForm">
            <div class="input-group">
                <label for="numberInput">Enter the count of even numbers:</label>
                <input type="number" id="numberInput" name="n" min="1" max="1000" value="10" required>
            </div>
            
            <button type="submit" class="btn">Generate Numbers</button>
            <button type="button" class="btn" onclick="clearResult()">Clear</button>
        </form>

        <div class="loading" id="loading">Generating numbers...</div>
        
        <div class="result" id="result">
            <h3 id="resultTitle"></h3>
            <div class="numbers-grid" id="numbersGrid"></div>
        </div>
    </div>

    <script>
        const form = document.getElementById('evenForm');
        const loading = document.getElementById('loading');
        const result = document.getElementById('result');
        const resultTitle = document.getElementById('resultTitle');
        const numbersGrid = document.getElementById('numbersGrid');

        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const n = parseInt(document.getElementById('numberInput').value);
            
            if (isNaN(n) || n < 1 || n > 1000) {
                showError('Please enter a valid number between 1 and 1000.');
                return;
            }

            generateEvenNumbers(n);
        });

        function generateEvenNumbers(n) {
            // Show loading
            loading.classList.add('show');
            result.classList.remove('show');
            
            // Simulate API call delay for better UX
            setTimeout(() => {
                try {
                    const evenNumbers = [];
                    for (let i = 1; i <= n; i++) {
                        evenNumbers.push(2 * i);
                    }

                    displayResult(n, evenNumbers);
                } catch (error) {
                    showError('An error occurred while generating numbers.');
                } finally {
                    loading.classList.remove('show');
                }
            }, 300);
        }

        function displayResult(n, numbers) {
            resultTitle.textContent = `The first ${n} even numbers are:`;
            
            numbersGrid.innerHTML = '';
            numbers.forEach((num, index) => {
                const numElement = document.createElement('div');
                numElement.className = 'number-item';
                numElement.textContent = num;
                numElement.style.animationDelay = `${index * 0.05}s`;
                numbersGrid.appendChild(numElement);
            });

            result.className = 'result show';
        }

        function showError(message) {
            resultTitle.textContent = 'Error';
            numbersGrid.innerHTML = `<div style="grid-column: 1 / -1; color: #d63031; font-weight: 500;">${message}</div>`;
            result.className = 'result show error';
            loading.classList.remove('show');
        }

        function clearResult() {
            result.classList.remove('show');
            document.getElementById('numberInput').value = '10';
            document.getElementById('numberInput').focus();
        }

        // Auto-focus on load
        document.getElementById('numberInput').focus();
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/health')
def health_check():
    return {"status": "healthy"}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
