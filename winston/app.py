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

	def get_message(self, folder: str, id):
		def logic(imap):
			imap.select(folder, True)
			(_, data) = imap.fetch(id, "(RFC822)")
			data = email.message_from_string(data[0][1].decode())
			sender_name, sender = re.findall("(.*) \<(.*)\>", data["From"])[0]
			return {
				"content"     : data.get_payload(),
				"date"        : data["Date"],
				"sender"      : sender,
				"sender_name" : sender_name,
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
			date = (datetime.date.today() - datetime.timedelta(1)).strftime("%d-%b-%Y")
			(_, data) = imap.search(None, ('UNSEEN'), '(SENTSINCE {0})'.format(date))
			# NOTE: this gets unread messages from after yesterday
			result = []
			for id in data[0].split():
				result.append(id)
			return result
			# NOTE: this returns message IDs (keeps byte type for use in get_message method)
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