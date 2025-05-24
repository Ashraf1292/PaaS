from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def multiply_matrices():
    # Example matrices
    matrix_a = [[1, 2], [3, 4]]
    matrix_b = [[5, 6], [7, 8]]

    # Matrix multiplication logic
    result = [[0, 0], [0, 0]]
    for i in range(len(matrix_a)):
        for j in range(len(matrix_b[0])):
            for k in range(len(matrix_b)):
                result[i][j] += matrix_a[i][k] * matrix_b[k][j]

    return f"Matrix A: {matrix_a}<br>Matrix B: {matrix_b}<br>Result (A x B): {result}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
