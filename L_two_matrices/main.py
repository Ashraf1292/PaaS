from flask import Flask, request, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Matrix Multiplication</title>
    <style>
    body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    padding: 50px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #4facfe 100%);
    min-height: 100vh;
    position: relative;
    overflow-x: auto;
}

body::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
        radial-gradient(circle at 20% 30%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
        radial-gradient(circle at 80% 70%, rgba(255, 255, 255, 0.08) 0%, transparent 50%);
    pointer-events: none;
}

h2 {
    color: #fff;
    font-size: 2.5em;
    font-weight: 700;
    text-align: center;
    margin-bottom: 40px;
    text-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    letter-spacing: -1px;
    position: relative;
}

h2::after {
    content: '';
    position: absolute;
    bottom: -10px;
    left: 50%;
    transform: translateX(-50%);
    width: 80px;
    height: 4px;
    background: linear-gradient(90deg, rgba(255, 255, 255, 0.8), rgba(255, 255, 255, 0.4));
    border-radius: 2px;
    box-shadow: 0 2px 10px rgba(255, 255, 255, 0.3);
}

form {
    margin-bottom: 40px;
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 20px;
    padding: 30px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
    max-width: 800px;
    margin: 0 auto 40px auto;
    transition: all 0.3s ease;
}

form:hover {
    transform: translateY(-2px);
    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2);
}

input[type="number"] {
    width: 60px;
    padding: 12px 8px;
    margin: 8px;
    text-align: center;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(10px);
    color: #fff;
    font-size: 1.1em;
    font-weight: 600;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

input[type="number"]::placeholder {
    color: rgba(255, 255, 255, 0.6);
}

input[type="number"]:focus {
    outline: none;
    border-color: rgba(255, 255, 255, 0.6);
    background: rgba(255, 255, 255, 0.3);
    box-shadow: 
        0 0 25px rgba(255, 255, 255, 0.3),
        0 6px 20px rgba(0, 0, 0, 0.15);
    transform: translateY(-2px) scale(1.05);
}

input[type="number"]:hover {
    border-color: rgba(255, 255, 255, 0.5);
    background: rgba(255, 255, 255, 0.25);
    transform: translateY(-1px);
}

.matrix {
    display: inline-block;
    margin: 0 30px 20px 30px;
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(15px);
    border-radius: 15px;
    padding: 20px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
    transition: all 0.3s ease;
    position: relative;
}

.matrix::before {
    content: '';
    position: absolute;
    top: -1px;
    left: -1px;
    right: -1px;
    bottom: -1px;
    background: linear-gradient(45deg, rgba(255, 255, 255, 0.2), transparent, rgba(255, 255, 255, 0.2));
    border-radius: 15px;
    z-index: -1;
    opacity: 0;
    transition: opacity 0.3s ease;
}

.matrix:hover::before {
    opacity: 1;
}

.matrix:hover {
    transform: translateY(-5px) scale(1.02);
    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2);
}

table {
    border-collapse: separate;
    border-spacing: 3px;
    background: transparent;
}

td {
    border: 2px solid rgba(255, 255, 255, 0.3);
    padding: 15px 12px;
    width: 50px;
    height: 50px;
    text-align: center;
    background: rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(10px);
    border-radius: 8px;
    color: #fff;
    font-weight: 700;
    font-size: 1.1em;
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}

td::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: left 0.5s;
}

td:hover::before {
    left: 100%;
}

td:hover {
    background: rgba(255, 255, 255, 0.3);
    border-color: rgba(255, 255, 255, 0.5);
    transform: translateY(-2px) scale(1.05);
    box-shadow: 0 8px 25px rgba(255, 255, 255, 0.2);
}

/* Button styles if you have any */
button {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.3) 0%, rgba(255, 255, 255, 0.2) 100%);
    backdrop-filter: blur(15px);
    color: white;
    border: 2px solid rgba(255, 255, 255, 0.4);
    padding: 15px 30px;
    font-size: 1.1em;
    border-radius: 25px;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    box-shadow: 0 10px 30px rgba(255, 255, 255, 0.15);
    margin: 10px;
    position: relative;
    overflow: hidden;
}

button::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
    transition: left 0.5s;
}

button:hover::before {
    left: 100%;
}

button:hover {
    transform: translateY(-3px) scale(1.05);
    box-shadow: 0 15px 40px rgba(255, 255, 255, 0.25);
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.4) 0%, rgba(255, 255, 255, 0.3) 100%);
    border-color: rgba(255, 255, 255, 0.6);
}

button:active {
    transform: translateY(-1px) scale(1.02);
}

/* Labels and text elements */
label {
    color: rgba(255, 255, 255, 0.9);
    font-weight: 600;
    font-size: 1.1em;
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
    margin-right: 10px;
}

/* Responsive design */
@media (max-width: 768px) {
    body {
        padding: 20px;
    }
    
    h2 {
        font-size: 2em;
        margin-bottom: 30px;
    }
    
    form {
        padding: 20px;
        border-radius: 15px;
    }
    
    .matrix {
        margin: 0 10px 20px 10px;
        padding: 15px;
        display: block;
        width: fit-content;
        margin-left: auto;
        margin-right: auto;
    }
    
    td {
        padding: 10px 8px;
        width: 40px;
        height: 40px;
        font-size: 1em;
    }
    
    input[type="number"] {
        width: 50px;
        padding: 10px 6px;
        margin: 6px;
    }
}

@media (max-width: 480px) {
    .matrix {
        margin: 0 5px 15px 5px;
    }
    
    td {
        padding: 8px 6px;
        width: 35px;
        height: 35px;
        font-size: 0.9em;
    }
    
    input[type="number"] {
        width: 45px;
        padding: 8px 4px;
        margin: 4px;
        font-size: 1em;
    }
}</head>
</style>
<body>
    <h2>2x2 Matrix Multiplication</h2>
    <form method="post">
        <div class="matrix">
            <h4>Matrix A</h4>
            {% for i in range(2) %}
                {% for j in range(2) %}
                    <input type="number" name="a{{i}}{{j}}" required>
                {% endfor %}
                <br>
            {% endfor %}
        </div>

        <div class="matrix">
            <h4>Matrix B</h4>
            {% for i in range(2) %}
                {% for j in range(2) %}
                    <input type="number" name="b{{i}}{{j}}" required>
                {% endfor %}
                <br>
            {% endfor %}
        </div>
        <br><br>
        <input type="submit" value="Multiply">
    </form>

    {% if result %}
        <h3>Result:</h3>
        <div class="matrix">
            <h4>A × B</h4>
            <table>
                {% for row in result %}
                    <tr>
                        {% for val in row %}
                            <td>{{ val }}</td>
                        {% endfor %}
                    </tr>
                {% endfor %}
            </table>
        </div>
    {% endif %}
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def multiply_matrices():
    result = None
    if request.method == 'POST':
        try:
            # Read Matrix A
            matrix_a = [
                [int(request.form['a00']), int(request.form['a01'])],
                [int(request.form['a10']), int(request.form['a11'])]
            ]

            # Read Matrix B
            matrix_b = [
                [int(request.form['b00']), int(request.form['b01'])],
                [int(request.form['b10']), int(request.form['b11'])]
            ]

            # Matrix multiplication logic
            result = [[0, 0], [0, 0]]
            for i in range(2):
                for j in range(2):
                    result[i][j] = matrix_a[i][0] * matrix_b[0][j] + matrix_a[i][1] * matrix_b[1][j]

        except ValueError:
            result = [["Error", "in"], ["input", "!"]]

    return render_template_string(HTML_TEMPLATE, result=result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
