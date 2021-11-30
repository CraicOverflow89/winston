from flask import Flask, redirect, render_template, request, url_for
from flask_cors import CORS
from winston.app import Winston
import datetime, json, os, re

app = Flask(__name__)
CORS(app)

@app.route("/")
def root():
    return redirect(url_for("inbox"))

@app.route("/folder", methods = ["GET"])
def folder_all():
	data = _winston().list_folders()
	return render_template("folders.html", data=data)

@app.route("/folder/<string:name>", methods = ["GET"])
def folder_get(name: str):
	w = _winston()
	data = []
	for id in w.list_messages(name):
		data.append(w.get_message(name, id))
	data.sort(key = lambda e: e["date"], reverse = True)
	return json.dumps(data, default = str)

@app.route("/folder/<string:name>/message/<int:id>", methods = ["GET"])
def message_get(name: str, id: int):
	return json.dumps(_winston().get_message(name, id), default = str)

# TO BE DELETED
@app.route("/compose", methods = ["GET", "POST"])
def compose():
	if request.method == "POST":

		# TEST SEND
		_winston().send(request.form['recipient'], request.form['subject'], request.form['content'])

		# TEMP CONTENT
		return "Message Sent"
	else:
		return render_template("compose.html")

# TO BE DELETED
@app.route("/inbox")
def inbox():

	# TEST FETCH
	w = _winston()
	data = []
	for id in w.list_messages("Inbox"):
		data.append(w.get_message("Inbox", id))
	data.sort(key = lambda e: e["date"], reverse = True)
	# TODO: pass limit by x messages to list_messages as arg

	# TEMP CONTENT
	return render_template("inbox.html", data=data)

def _winston():
	def account_data():
		with open(os.path.join(os.path.dirname(os.path.realpath("__file__")), "account")) as fs:
			result = fs.read()
		return re.split("\\|", result)
	account, password = account_data()
	return Winston("smtp.live.com", 587, account, password)

# TO BE DELETED
@app.template_filter()
def format_datetime(value):
	if value.date() == datetime.date.today():
		return value.strftime("%H:%M:%S")
	else:
		return value.strftime("%d/%m/%Y, %H:%M:%S")