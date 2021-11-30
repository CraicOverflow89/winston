import datetime, email, imaplib, re, smtplib, sys

class Winston():

	def __init__(self, host: str, port: int, account: str, password: str):
		"""
		Initialises the Winston core

		:param host: the host to connect to
		:param port: the port to connect to
		:param account: the email account
		:param password: the account password
		:return: instance of Winston core
		"""
		self.host = host
		self.port = port
		self.account = account
		self.password = password

	def _imap(self, logic):
		"""
		Performs a task using imap

		:param logic: the callable to perform using imap
		:return: result of the task
		"""

		# Establish Connection
		imap = imaplib.IMAP4_SSL(self.host)
		imap.login(self.account, self.password)

		# Execute Logic
		result = logic(imap)

		# Terminate Connection
		imap.logout()
		return result

	def _smtp(self, logic):
		"""
		Performs a task using smtp

		:param logic: the callable to perform using smtp
		:return: result of the task
		"""

		# Establish Connection
		smtp = smtplib.SMTP(self.host, self.port)
		smtp.ehlo()
		smtp.starttls()
		smtp.ehlo()
		smtp.login(self.account, self.password)

		# Execute Logic
		result = logic(smtp)

		# Terminate Connection
		smtp.quit()
		return result

	def get_message(self, folder: str, id: int):
		"""
		Fetches an email message by id

		:param folder: the folder to fetch from
		:param id: the id of the message to fetch
		:return: dict of message data
		"""
		def logic(imap):

			# Message Data
			imap.select(folder, True)
			(_, data) = imap.fetch(str(id).encode(), "(RFC822)")
			data = email.message_from_string(data[0][1].decode())

			# Sender Data
			def parse_sender(value: str):

				# Default Values
				result = {
					"email" : value,
					"name"  : value
				}

				# Multiple Values
				if re.search(".* \<.*>", value):
					name, email = re.findall("(.*) \<(.*)\>", value)[0]
					result.update({
						"email" : email,
						"name"  : name
					})

				# Return Result
				return result
			sender = parse_sender(data["From"])
			# NOTE: [name, email] = parse_sender(data["From"]) ?

			# Return Message
			return {
				"content"     : data.get_payload(),
				"date"        : data["Date"],
				"sender"      : sender["email"],
				"sender_name" : sender["name"],
				"subject"     : email.header.decode_header(data["Subject"])[0][0]
			}
			#"date"        : datetime.datetime.strptime(data["Date"], "%a, %d %B %Y %H:%M:%S %z"),
		return self._imap(logic)

	def list_folders(self):
		"""
		Fetches folders of the account

		:return: list of folder names
		"""
		def logic(imap):
			result = []
			for folder in imap.list()[1]:
				result.append(re.split(" ", folder.decode())[-1])
			return result
		return self._imap(logic)

	def list_messages(self, folder: str):
		"""
		Fetches messages of a folder

		:param folder: the folder to fetch from
		:return: list of message data
		"""
		def logic(imap):
			imap.select(folder, True)
			# NOTE: this sets readonly to True (so unread messages will not be marked as read)
			(_, data) = imap.search(None, "ALL")
			result = []
			# for id in data[0].split():
			# 	result.append(id.decode())
			# return result
			# TEMP: fetching latest five messages
			for id in data[0].split()[-5:]:
				result.append(id.decode())
			return result
			# TODO: ordering (just iterate backwards in the view)?
		return self._imap(logic)

	def send(self, recipient: str, subject: str, content: str):
		"""
		Sends an email message

		:param recipient: the email recipient
		:param subject: the email subject
		:param content: the email content
		:return: None
		"""

		# Build Message
		message = []
		message.append("From: {}".format(self.account))
		message.append("To: {}".format(recipient))
		message.append("Subject: {}".format(subject))
		message.append("")
		message.append(content)
		message = "\n".join(message)

		# Send Email
		def logic(smtp):
			try:
				smtp.sendmail(self.account, recipient, message)
				# NOTE: anything to return from this?
			except smtplib.SMTPException:
				print("Error Encountered")
				print(sys.exc_info())
		self._smtp(logic)