from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def generate_even_numbers():
    try:
        n = int(request.args.get('n', 10))
    except ValueError:
        return "Invalid input. Please provide an integer value for 'n'."

    even_numbers = [2 * i for i in range(1, n + 1)]
    return f'The first {n} even numbers are: {even_numbers}'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
