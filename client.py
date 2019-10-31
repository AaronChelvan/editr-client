from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import json, string, difflib, socket, sys

# The main window for the client program
class MainWindow(QMainWindow):
	stopEditing = pyqtSignal(str)

	# Constructor
	def __init__(self, socket):
		super(MainWindow, self).__init__()
		self.setCentralWidget(Textbox(socket)) # Add a Textbox to the window

# The textbox where the file contents will be displayed
class Textbox(QTextEdit):
	# Constructor
	def __init__(self, clientSocket):
		super(Textbox, self).__init__()
		self.setFont(QFont('Monospace', 14)) # Set the font
		self.textChanged.connect(self.textChangedHandler)
		self.prevText = self.toPlainText() # The content currently in the textbox
		self.clientSocket = clientSocket

	# This functions executes everytime the contents of the textbox changes
	def textChangedHandler(self):
		# Use sequence matcher to find what changes were made to the textbox contents
		s = difflib.SequenceMatcher(None, self.prevText, self.toPlainText())

		# Iterate through the changes
		for tag, i1, i2, j1, j2 in s.get_opcodes():
			if tag == "replace": # If characters were overwritten
				self.sendUpdate("remove", i1, i2-i1)
				self.sendUpdate("write", i1, self.toPlainText()[j1:j2])
			elif tag == "delete": # If characters were deleted
				self.sendUpdate("remove", i1, i2-i1)
			elif tag == "insert": # If characters were inserted
				self.sendUpdate("write", i1, self.toPlainText()[j1:j2])

		self.prevText = self.toPlainText()

	# When the contents of the textbox is edited, generate a JSON string describing the edit
	# and send it to the server
	def sendUpdate(self, *args):
		message = {}
		if args[0] == "open":
			# TODO
			pass
		elif args[0] == "write":
			data = list(bytes(args[2], "utf-8"))
			message["WriteReq"] = {"offset": args[1], "data": data}
		elif args[0] == "read":
			# TODO
			pass
		elif args[0] == "remove":
			message["RemoveReq"] = {"offset": args[1], "len": args[2]}
		else:
			print("Unknown operation")
			exit()

		print(message)
		# Convert "message" to a JSON string and send it to the server
		self.clientSocket.send(json.dumps(message).encode("utf-8"))
		# TODO - If the JSON string is greater than 1024 bytes, break it up into multiple messages  

		# Wait for an ack
		response = self.clientSocket.recv(1024)
		print(json.loads(response.decode()))

		'''
		while True:
			response = self.clientSocket.recv(1024)
			if not response:
				break
			else:
				print(response.decode())
		'''
		# TODO check that the ack is valid for the request sent


#app = QApplication([])
#app.setApplicationName("Editr Client")
#def test():

#window = MainWindow()
#window.show()
#app.exec_()
