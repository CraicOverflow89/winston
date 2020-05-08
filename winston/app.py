import smtplib, sys

class Winston():

	def __init__(self, host: str, port: int, account: str, password: str):
		self.account = account
		self.password = password
		self.smtp = smtplib.SMTP(host, port)

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
		try:
			self.smtp.ehlo()
			self.smtp.starttls()
			self.smtp.ehlo()
			self.smtp.login(self.account, self.password)
			self.smtp.sendmail(self.account, recipient, message)
			self.smtp.quit()
		except smtplib.SMTPException:
			print("Error Encountered")
			print(sys.exc_info())