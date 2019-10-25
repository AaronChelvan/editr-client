from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import json, string, difflib

# The main window for the client program
class MainWindow(QMainWindow):
	# Constructor
	def __init__(self):
		super(MainWindow, self).__init__()
		self.setCentralWidget(Textbox()) # Add a Textbox to the window

# The textbox where the file contents will be displayed
class Textbox(QTextEdit):
	# Constructor
	def __init__(self):
		super(Textbox, self).__init__()
		self.setFont(QFont('Monospace', 14)) # Set the font
		self.textChanged.connect(self.textChangedHandler)
		self.prevText = self.toPlainText() # The content currently in the textbox
	
	# This functions executes everytime the contents of the textbox changes
	def textChangedHandler(self):
		# Use sequence matcher to find what changes were made to the textbox contents
		s = difflib.SequenceMatcher(None, self.prevText, self.toPlainText())

		# Iterate through the changes
		for tag, i1, i2, j1, j2 in s.get_opcodes():
			if tag == "replace": # If characters were overwritten
				sendUpdate("remove", i1, i2-i1)
				sendUpdate("write", i1, self.toPlainText()[j1:j2])
			elif tag == "delete": # If characters were deleted
				sendUpdate("remove", i1, i2-i1)
			elif tag == "insert": # If characters were inserted
				sendUpdate("write", i1, self.toPlainText()[j1:j2])

		self.prevText = self.toPlainText()

# When the contents of the textbox is edited, generate a JSON string describing the edit
# and send it to the server
def sendUpdate(*args):
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

	# TODO 
	# convert "message" to a JSON string and send it to the server


#app = QApplication([])
#app.setApplicationName("Editr Client")
#def test():

#window = MainWindow()
#window.show()
#app.exec_()
