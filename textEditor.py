from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from lib import *
import json, string, difflib, socket, sys

# The text editor window
class textEditorWindow(QMainWindow):
	stopEditing = pyqtSignal(object)

	# Constructor
	def __init__(self, clientSocket, fileName):
		super(textEditorWindow, self).__init__()
		self.setGeometry(400, 400, 600, 500)
		self.setCentralWidget(Textbox(clientSocket, fileName)) # Add a Textbox to the window
		self.clientSocket = clientSocket
		closeButton = QPushButton('Save && Close', self)
		closeButton.move(450, 450)
		closeButton.clicked.connect(self.stopEditingFunction)
	
	def stopEditingFunction(self):
		# Save the changes made and close the file
		sendMessage(self.clientSocket, "save")
		sendMessage(self.clientSocket, "close")
		self.stopEditing.emit(self.clientSocket)

# The textbox where the file contents will be displayed
class Textbox(QTextEdit):
	# Constructor
	def __init__(self, clientSocket, fileName):
		super(Textbox, self).__init__()
		self.setFont(QFont('Monospace', 14)) # Set the font
		self.clientSocket = clientSocket # Save the socket

		# Read the file contents and display it in the textbox
		response = sendMessage(self.clientSocket, "read", 0, 999)
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
				sendMessage(self.clientSocket, "remove", i1, i2-i1)
				sendMessage(self.clientSocket, "write", i1, self.toPlainText()[j1:j2])
			elif tag == "delete": # If characters were deleted
				sendMessage(self.clientSocket, "remove", i1, i2-i1)
			elif tag == "insert": # If characters were inserted
				sendMessage(self.clientSocket, "write", i1, self.toPlainText()[j1:j2])

		self.prevText = self.toPlainText()
