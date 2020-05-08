from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def root():
	return render_template("main.html")

@app.route("/compose")
def compose():
	return render_template("compose.html")