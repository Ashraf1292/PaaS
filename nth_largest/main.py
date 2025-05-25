from flask import Flask, request, render_template_string

app = Flask(__name__)

HTML_FORM = """
<!doctype html>
<title>Find Nth Largest Number</title>
<h2>Enter numbers separated by commas and the value of n</h2>
<form method="POST">
  Numbers: <input name="numbers" placeholder="e.g. 10, 30, 50, 20, 60"><br><br>
  N: <input name="n" type="number" min="1"><br><br>
  <input type="submit" value="Find Nth Largest">
</form>
{% if result is not none %}
  <h3>{{ n }}th largest number is: {{ result }}</h3>
{% endif %}
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    n = None
    if request.method == 'POST':
        numbers = request.form['numbers']
        n = int(request.form['n'])
        try:
            num_list = list(map(int, numbers.split(',')))
            num_list.sort(reverse=True)
            result = num_list[n-1] if n <= len(num_list) else "N is too large"
        except Exception as e:
            result = f"Error: {e}"
    return render_template_string(HTML_FORM, result=result, n=n)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
