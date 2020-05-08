from flask import Flask, render_template, request
from winston.app import Winston
import os, re

app = Flask(__name__)

@app.route("/")
def root():
	return render_template("main.html")

@app.route("/compose", methods = ["GET", "POST"])
def compose():
	if request.method == "POST":

		# TEST SEND
		def account_data():
			with open(os.path.join(os.path.dirname(os.path.realpath("__file__")), "account")) as fs:
				result = fs.read()
			return re.split("\\|", result)
		account, password = account_data()
		Winston("smtp.live.com", 587, account, password).send(request.form['recipient'], request.form['subject'], request.form['content'])

		# TEMP CONTENT
		return "Message Sent"
	else:
		return render_template("compose.html")