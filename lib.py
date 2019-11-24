from PyQt5.QtWidgets import QMessageBox
import json

# Send a message to the server
def sendMessage(clientSocket, getResponse, *args):
	message = {}
	if args[0] == "open":
		message["OpenReq"] = {"file":args[1], "name":args[2]}
	elif args[0] == "close":
		message = "CloseReq"
	elif args[0] == "write":
		message["WriteAtCursorReq"] = {"data": args[1]}
	elif args[0] == "read":
		message["ReadReq"] = {"offset": args[1], "len": args[2]}
	elif args[0] == "remove":
		message["RemoveAtCursorReq"] = {"len": args[1]}
	elif args[0] == "save":
		message = "SaveReq"
	elif args[0] == "create":
		message["CreateReq"] = args[1]
	elif args[0] == "delete":
		message["DeleteReq"] = args[1]
	elif args[0] == "rename":
		message["RenameReq"] = {"from": args[1], "to": args[2]}
	elif args[0] == "getFiles":
		message = "FilesListReq"
	elif args[0] == "moveCursor":
		message["MoveCursor"] = args[1]
	elif args[0] == "getCursors":
		message = "GetCursorsReq"
	else:
		print("Unknown operation")
		exit()

	print(message)
	# Convert "message" to a JSON string and send it to the server
	clientSocket.send(json.dumps(message).encode("utf-8"))
	# TODO If the JSON string is greater than 1024 bytes, break it up into multiple messages
	# (only applicable for "write" and "read")  

	# Wait for an ack
	if getResponse == True:
		response = clientSocket.recv(40960)
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

def showErrorMessage(message):
	errorMessage = QMessageBox()
	errorMessage.setIcon(QMessageBox.Warning)
	errorMessage.setText(message)
	errorMessage.setWindowTitle("Error")
	errorMessage.exec_()

def showSuccessMessage(message):
	successMessage = QMessageBox()
	successMessage.setText(message)
	successMessage.setWindowTitle("Success")
	successMessage.exec_()