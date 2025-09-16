import socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
PORT = 8000

# take out 1 minute timeout from the socket after closed
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("localhost", PORT))
server.listen(5)
print(f"Server started on port {PORT}")
while True:
    request, address = server.accept()
    print(f"Request received: {request.recv(1024)}")
    string_to_return = ""
    string_to_return = string_to_return+"HTTP/1.1 200\r\n\r\n"
    string_to_return = string_to_return+"<!DOCTYPE HTML>"
    string_to_return = string_to_return+"<html lang='en'>"
    string_to_return = string_to_return+"<head>"
    string_to_return = string_to_return+"<meta charset='utf-8'>"
    string_to_return = string_to_return+"</head>"
    string_to_return = string_to_return+"<body>"
    string_to_return = string_to_return+"<h1>Server response</h1>"
    string_to_return = string_to_return+"</body>"
    string_to_return = string_to_return+"</html>"
    string_to_return = bytes(string_to_return.encode())
    request.send(string_to_return)
    request.close()
