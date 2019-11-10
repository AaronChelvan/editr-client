from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from lib import *
import json, string, difflib, socket, sys, threading, time

listenerThread = None

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
		# Stop the listener thread
		global listenerThread
		listenerThread.run = False
		listenerThread.join()

		# Enable socket blocking
		self.clientSocket.setblocking(True)

		# Save the changes made and close the file
		sendMessage(self.clientSocket, True, "save")
		sendMessage(self.clientSocket, True, "close")

		# Go to the file selection menu
		self.stopEditing.emit(self.clientSocket)

# The textbox where the file contents will be displayed
class Textbox(QTextEdit):
	# Constructor
	def __init__(self, clientSocket, fileName):
		super(Textbox, self).__init__()
		self.setFont(QFont('Monospace', 14)) # Set the font
		self.clientSocket = clientSocket # Save the socket

		# Read the file contents and display it in the textbox
		response = sendMessage(self.clientSocket, True, "read", 0, 999)
		fileContents = response["ReadResp"]["Ok"]
		fileContents = bytearray(fileContents).decode("utf-8")
		self.setText(fileContents)
		
		# Start detecting edits made to the textbox contents
		self.textChanged.connect(self.textChangedHandler)
		self.prevText = self.toPlainText() # The content currently in the textbox
		
		# Make the socket non-blocking
		self.clientSocket.setblocking(False)

		# Start the listener thread
		global listenerThread
		listenerThread = threading.Thread(target=self.listener)
		listenerThread.start()

	# This functions executes everytime the contents of the textbox changes
	def textChangedHandler(self):
		# Use sequence matcher to find what changes were made to the textbox contents
		s = difflib.SequenceMatcher(None, self.prevText, self.toPlainText())

		# Iterate through the changes
		for tag, i1, i2, j1, j2 in s.get_opcodes():
			if tag == "replace": # If characters were overwritten
				sendMessage(self.clientSocket, False, "remove", i1, i2-i1)
				sendMessage(self.clientSocket, False, "write", i1, self.toPlainText()[j1:j2])
			elif tag == "delete": # If characters were deleted
				sendMessage(self.clientSocket, False, "remove", i1, i2-i1)
			elif tag == "insert": # If characters were inserted
				sendMessage(self.clientSocket, False, "write", i1, self.toPlainText()[j1:j2])

		self.prevText = self.toPlainText()

	# This function executes in a separate thread and constantly checks for updates from the server
	def listener(self):
		t = threading.currentThread()
		decoder = json.JSONDecoder()
		while getattr(t, "run", True):
			try:
				data = self.clientSocket.recv(1024)

				# The client may have received multiple responses, so we need to split them
				count = 0
				listObjects = []
				while count < len(data.decode()):
					jsonObject = decoder.raw_decode(data.decode()[count:])
					listObjects.append(jsonObject[0])
					count += jsonObject[1]
				for o in listObjects:
					print("listener received: " + str(o))
					if "UpdateAdd" in o:
						self.blockSignals(True)
						updateCursor = self.cursorForPosition(o["UpdateAdd"]["offset"])
						updateCursor.insertText(bytearray(o["UpdateAdd"]["data"]).decode("utf-8"))
						self.blockSignals(False)
					elif "UpdateRemove" in o:
						self.blockSignals(True)
						updateCursor = self.cursorForPosition(o["UpdateRemove"]["offset"])
						for _ in o["UpdateRemove"]["len"]:
							updateCursor.deleteChar()
						self.blockSignals(False)
			except socket.error:
				time.sleep(0.1)

		print("listener is stopping")
