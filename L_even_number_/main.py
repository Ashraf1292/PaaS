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
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #4c6ef5 100%);
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
    position: relative;
    overflow-x: hidden;
}

body::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
        radial-gradient(circle at 20% 50%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.08) 0%, transparent 50%),
        radial-gradient(circle at 40% 80%, rgba(255, 255, 255, 0.06) 0%, transparent 50%);
    pointer-events: none;
}

.container {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.3);
    padding: 50px;
    border-radius: 30px;
    box-shadow: 
        0 25px 50px rgba(0, 0, 0, 0.2),
        inset 0 1px 0 rgba(255, 255, 255, 0.4);
    max-width: 650px;
    width: 100%;
    text-align: center;
    position: relative;
    transform: translateY(0);
    transition: all 0.3s ease;
}

.container:hover {
    transform: translateY(-5px);
    box-shadow: 
        0 35px 70px rgba(0, 0, 0, 0.25),
        inset 0 1px 0 rgba(255, 255, 255, 0.4);
}

h1 {
    color: #fff;
    margin-bottom: 40px;
    font-size: 3em;
    font-weight: 700;
    text-shadow: 0 2px 20px rgba(0, 0, 0, 0.3);
    letter-spacing: -1px;
    position: relative;
}

h1::after {
    content: '';
    position: absolute;
    bottom: -10px;
    left: 50%;
    transform: translateX(-50%);
    width: 60px;
    height: 4px;
    background: linear-gradient(90deg, #4c6ef5, #7c3aed);
    border-radius: 2px;
}

.input-group {
    margin-bottom: 40px;
}

label {
    display: block;
    margin-bottom: 15px;
    color: rgba(255, 255, 255, 0.9);
    font-size: 1.2em;
    font-weight: 600;
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

input[type="number"] {
    width: 220px;
    padding: 18px 24px;
    font-size: 1.3em;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 15px;
    text-align: center;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    background: rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(10px);
    color: #fff;
    font-weight: 500;
}

input[type="number"]::placeholder {
    color: rgba(255, 255, 255, 0.6);
}

input[type="number"]:focus {
    outline: none;
    border-color: #4c6ef5;
    background: rgba(255, 255, 255, 0.25);
    box-shadow: 
        0 0 25px rgba(76, 110, 245, 0.4),
        inset 0 1px 0 rgba(255, 255, 255, 0.3);
    transform: translateY(-2px) scale(1.02);
}

.btn {
    background: linear-gradient(135deg, #4c6ef5 0%, #7c3aed 100%);
    color: white;
    border: none;
    padding: 18px 36px;
    font-size: 1.1em;
    border-radius: 25px;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    margin: 12px 8px;
    min-width: 140px;
    font-weight: 600;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 25px rgba(76, 110, 245, 0.3);
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
    transform: translateY(-3px) scale(1.05);
    box-shadow: 0 15px 35px rgba(76, 110, 245, 0.4);
    background: linear-gradient(135deg, #5c7cfa 0%, #8b5cf6 100%);
}

.btn:active {
    transform: translateY(-1px) scale(1.02);
}

.result {
    margin-top: 40px;
    padding: 30px;
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(15px);
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    display: none;
    position: relative;
}

.result.show {
    display: block;
    animation: slideInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes slideInUp {
    from {
        opacity: 0;
        transform: translateY(30px) scale(0.95);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

.result h3 {
    color: #fff;
    margin-bottom: 20px;
    font-size: 1.4em;
    font-weight: 600;
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.numbers-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(60px, 1fr));
    gap: 12px;
    margin-top: 20px;
}

.number-item {
    background: linear-gradient(135deg, rgba(76, 110, 245, 0.8) 0%, rgba(124, 58, 237, 0.8) 100%);
    backdrop-filter: blur(10px);
    color: white;
    padding: 15px 10px;
    border-radius: 12px;
    font-weight: 700;
    font-size: 1.1em;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.number-item:hover {
    transform: translateY(-3px) scale(1.08);
    box-shadow: 0 10px 25px rgba(76, 110, 245, 0.4);
    background: linear-gradient(135deg, rgba(92, 124, 250, 0.9) 0%, rgba(139, 92, 246, 0.9) 100%);
}

.error {
    background: rgba(239, 68, 68, 0.15);
    border: 1px solid rgba(239, 68, 68, 0.3);
    color: #fecaca;
}

.loading {
    display: none;
    color: rgba(255, 255, 255, 0.8);
    font-style: italic;
    font-size: 1.1em;
}

.loading.show {
    display: block;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 0.6; }
    50% { opacity: 1; }
}

@media (max-width: 480px) {
    .container {
        padding: 30px 20px;
        border-radius: 20px;
    }
    
    h1 {
        font-size: 2.2em;
        margin-bottom: 30px;
    }
    
    input[type="number"] {
        width: 100%;
        max-width: 250px;
        padding: 16px 20px;
    }

    .btn {
        padding: 16px 30px;
        margin: 8px 4px;
        min-width: 120px;
    }

    .numbers-grid {
        grid-template-columns: repeat(auto-fill, minmax(50px, 1fr));
        gap: 8px;
    }

    .number-item {
        padding: 12px 8px;
        font-size: 1em;
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
