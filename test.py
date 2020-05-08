#!/usr/bin/python

import os, re
from winston.app import Winston

# Account Data
def account_data():
	result = ""
	with open(os.path.join(os.path.dirname(os.path.realpath("__file__")), "account")) as fs:
		result = fs.read()
	return re.split("\\|", result)

# Execute Test
account, password = account_data()
test = Winston("smtp.live.com", 587, account, password)
#test.send("*****@hotmail.com", "Test", "Hello World")
for folder in test.list_folders():
	message_id_list = test.list_messages(folder)
	if(len(message_id_list)):
		print("\n{}".format(folder))
		data = []
		for id in message_id_list:
			data.append(test.get_message(folder, id))
		data.sort(key = lambda e: e["date"], reverse = True)
		for message in data:
			print(message)