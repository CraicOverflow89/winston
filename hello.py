from flask import Flask, redirect, render_template, request, url_for
from winston.app import Winston
import os, re

app = Flask(__name__)

@app.route("/")
def root():
    return redirect(url_for("inbox"))

@app.route("/compose", methods = ["GET", "POST"])
def compose():
	if request.method == "POST":

		# TEST SEND
		_winston().send(request.form['recipient'], request.form['subject'], request.form['content'])

		# TEMP CONTENT
		return "Message Sent"
	else:
		return render_template("compose.html")

@app.route("/inbox")
def inbox():

	# TEST FETCH
	w = _winston()
	data = []
	for id in w.list_messages("Inbox"):
		data.append(w.get_message("Inbox", id))

	# TEMP CONTENT
	return render_template("inbox.html", data=data)

def _winston():
	def account_data():
		with open(os.path.join(os.path.dirname(os.path.realpath("__file__")), "account")) as fs:
			result = fs.read()
		return re.split("\\|", result)
	account, password = account_data()
	return Winston("smtp.live.com", 587, account, password)