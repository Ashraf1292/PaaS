from flask import Flask, request, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Matrix Multiplication</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 40px; background-color: #f2f2f2; }
        h2 { color: #333; }
        form { margin-bottom: 20px; }
        input[type="number"] {
            width: 50px;
            padding: 5px;
            margin: 5px;
            text-align: center;
        }
        .matrix { display: inline-block; margin: 0 20px; }
        table { border-collapse: collapse; }
        td {
            border: 1px solid #999;
            padding: 10px;
            width: 40px;
            text-align: center;
            background-color: white;
        }
    </style>
</head>
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
