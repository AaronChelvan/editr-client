from PyQt5.QtWidgets import QMessageBox
import json

# Send a message to the server
def sendMessage(clientSocket, *args):
	message = {}
	if args[0] == "open":
		message["OpenReq"] = args[1]
	elif args[0] == "close":
		message = "CloseReq"
	elif args[0] == "write":
		data = list(bytes(args[2], "utf-8"))
		message["WriteReq"] = {"offset": args[1], "data": data}
	elif args[0] == "read":
		message["ReadReq"] = {"offset": args[1], "len": args[2]}
	elif args[0] == "remove":
		message["RemoveReq"] = {"offset": args[1], "len": args[2]}
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