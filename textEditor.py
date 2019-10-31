from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import json, string, difflib, socket, sys

# The text editor window
class MainWindow(QMainWindow):
	stopEditing = pyqtSignal()

	# Constructor
	def __init__(self, clientSocket):
		super(MainWindow, self).__init__()
		self.setGeometry(400, 400, 600, 500)
		self.setCentralWidget(Textbox(clientSocket)) # Add a Textbox to the window
		self.clientSocket = clientSocket
		closeButton = QPushButton('Save & Close', self)
		closeButton.move(450, 450)
		closeButton.clicked.connect(self.stopEditingFunction)
	
	def stopEditingFunction(self):
		# Save the changes made and close the file
		# TODO - save seems to hang
		# sendUpdate(self.clientSocket, "save")
		self.clientSocket.close()
		self.stopEditing.emit()

# The textbox where the file contents will be displayed
class Textbox(QTextEdit):
	# Constructor
	def __init__(self, clientSocket):
		super(Textbox, self).__init__()
		self.setFont(QFont('Monospace', 14)) # Set the font
		self.clientSocket = clientSocket # Save the socket

		# Open the file
		response = sendUpdate(self.clientSocket, "open", "test.txt")
		if "Err" in response:
			print("trying to open a file that doesn't exist")
			return

		# Read the file contents and display it in the textbox
		response = sendUpdate(self.clientSocket, "read", 0, 999)
		fileContents = response["ReadResp"]["Ok"]
		fileContents = bytearray(fileContents).decode("utf-8")
		self.setText(fileContents)
		
		# Start detecting edits made to the textbox contents
		self.textChanged.connect(self.textChangedHandler)
		self.prevText = self.toPlainText() # The content currently in the textbox

	# This functions executes everytime the contents of the textbox changes
	def textChangedHandler(self):
		# Use sequence matcher to find what changes were made to the textbox contents
		s = difflib.SequenceMatcher(None, self.prevText, self.toPlainText())

		# Iterate through the changes
		for tag, i1, i2, j1, j2 in s.get_opcodes():
			if tag == "replace": # If characters were overwritten
				sendUpdate(self.clientSocket, "delete", i1, i2-i1)
				sendUpdate(self.clientSocket, "write", i1, self.toPlainText()[j1:j2])
			elif tag == "delete": # If characters were deleted
				sendUpdate(self.clientSocket, "delete", i1, i2-i1)
			elif tag == "insert": # If characters were inserted
				sendUpdate(self.clientSocket, "write", i1, self.toPlainText()[j1:j2])

		self.prevText = self.toPlainText()

# When the contents of the textbox is edited, generate a JSON string describing the edit
# and send it to the server
def sendUpdate(clientSocket, *args):
	message = {}
	if args[0] == "open":
		fileName = args[1]
		message["OpenReq"] = fileName
	elif args[0] == "write":
		data = list(bytes(args[2], "utf-8"))
		message["WriteReq"] = {"offset": args[1], "data": data}
	elif args[0] == "read":
		message["ReadReq"] = {"offset": args[1], "len": args[2]}
	elif args[0] == "delete":
		message["DeleteReq"] = {"offset": args[1], "len": args[2]}
	elif args[0] == "save":
		message["SaveReq"] = ""
	else:
		print("Unknown operation")
		exit()

	print(message)
	# Convert "message" to a JSON string and send it to the server
	clientSocket.send(json.dumps(message).encode("utf-8"))
	# TODO - If the JSON string is greater than 1024 bytes, break it up into multiple messages  

	# Wait for an ack
	response = clientSocket.recv(1024)
	responseDict = json.loads(response.decode())
	print(responseDict)
	return responseDict

	'''
	while True:
		response = self.clientSocket.recv(1024)
		if not response:
			break
		else:
			print(response.decode())
	'''
	# TODO check that the ack is valid for the request sent
