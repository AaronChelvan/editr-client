from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import json, string

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

	# When a key is pressed
	def keyPressEvent(self, event):
		# The location of the cursor
		cursorPosition = self.textCursor().selectionStart()

		# The number of characters highlighted (0 == no characters highlighted)
		numHighlightedChars = self.textCursor().selectionEnd() - self.textCursor().selectionStart()

		# User pressed backspace
		if event.key() == Qt.Key_Backspace:
			if numHighlightedChars > 0:
				sendUpdate("remove", cursorPosition, numHighlightedChars)
			elif self.textCursor().atStart() == False: # Is there a character to the left of the cursor?
				sendUpdate("remove", cursorPosition-1, 1)
			else:
				print("Nothing to delete")

		# User pressed delete
		elif event.key() == Qt.Key_Delete:
			if numHighlightedChars > 0:
				sendUpdate("remove", cursorPosition, numHighlightedChars)
			elif self.textCursor().atEnd() == False: # Is there a character to the right of the cursor?
				sendUpdate("remove", cursorPosition, 1)
			else:
				print("Nothing to delete")

		# User pressed a printable character
		elif event.text() in string.printable and event.text() != "":
			# If one or more characters are highlighted, they will get overwritten
			if numHighlightedChars > 0:
				sendUpdate("remove", cursorPosition, numHighlightedChars)

			# Write the new character
			if event.text() == "\r": # \r should be a newline char
				char = "\n"
			else:
				char = event.text()
			sendUpdate("write", cursorPosition, char)
		
		# User pressed cut (Ctrl + X)
		elif event.key() == Qt.Key_X and event.modifiers() == Qt.ControlModifier:
			if numHighlightedChars > 0:
				sendUpdate("remove", cursorPosition, numHighlightedChars)

		# User pressed paste (Ctrl + V)
		elif event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
			sendUpdate("write", cursorPosition, QApplication.clipboard().text())

		# Process the key press in the textbox
		super(Textbox, self).keyPressEvent(event)

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
	# convert "message" to a JSON string 
	# convert the JSON string to byte form
	# and send it to the server


app = QApplication([])
app.setApplicationName("Editr Client")

window = MainWindow()
window.show()
app.exec_()
