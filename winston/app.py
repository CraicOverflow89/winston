import datetime, email, imaplib, re, smtplib, sys

class Winston():

	def __init__(self, host: str, port: int, account: str, password: str):
		self.host = host
		self.port = port
		self.account = account
		self.password = password

	def _imap(self, logic):

		# Establish Connection
		imap = imaplib.IMAP4_SSL(self.host)
		imap.login(self.account, self.password)

		# Execute Logic
		result = logic(imap)

		# Terminate Connection
		imap.logout()
		return result

	def _smtp(self, logic):

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

			# Return Message
			return {
				"content"     : data.get_payload(),
				"date"        : datetime.datetime.strptime(data["Date"], "%a, %d %B %Y %H:%M:%S %z"),
				"sender"      : sender["email"],
				"sender_name" : sender["name"],
				"subject"     : email.header.decode_header(data["Subject"])[0][0]
			}
		return self._imap(logic)

	def list_folders(self):
		def logic(imap):
			result = []
			for folder in imap.list()[1]:
				result.append(re.split(" ", folder.decode())[-1])
			return result
		return self._imap(logic)

	def list_messages(self, folder: str):
		def logic(imap):
			imap.select(folder, True)
			# NOTE: this sets readonly to True (so unread messages will not be marked as read)
			(_, data) = imap.search(None, "ALL")
			result = []
			for id in data[0].split():
				result.append(id.decode())
			return result
		return self._imap(logic)

	def send(self, recipient: str, subject: str, content: str):

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
			except smtplib.SMTPException:
				print("Error Encountered")
				print(sys.exc_info())
		self._smtp(logic)