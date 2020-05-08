import datetime, imaplib, re, smtplib, sys

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

	def list_folders(self):
		def logic(imap):
			result = []
			for folder in imap.list()[1]:
				result.append(re.split(" ", folder.decode())[-1])
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