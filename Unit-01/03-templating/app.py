from flask import Flask, render_template, request, url_for

app = Flask(__name__)


# Part 1
@app.route('/person/<name>/<int:age>')
def say_name_and_age(name, age):
	name = name.title()
	return render_template('person.html', name=name, age=age)
	

if __name__ == "__main__":
	app.run(debug=True)