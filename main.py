import socket
import os


class HTTPException(Exception):
    def __init__(self, args, status):
        super().__init__(args)
        self.status = status

class HTTPRequest:
    def __init__(self, request_string):
        array_of_splitted_string = list(filter(None, str.split(request_string.decode("UTF-8"), ("\r\n"))))
        self.request_line = array_of_splitted_string[0]
        self.headers = array_of_splitted_string[1:len(array_of_splitted_string)]
    def get_method(self):
        return str.split(self.request_line, " ")[0]

class HTTPResponse:
    def __init__(self, message, status):
        self.http_spec = "HTTP/1.1"
        self.status = status
        self.message = message
        self.content_type = "text/html"
        self.server = "Marinho's HTTP server"
        self.html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.status} {self.message}</title>
</head>
<body>
    <h1>{self.status} {self.message}</h1>
</body>
</html>
"""

    def __str__(self):
        start_line = str.join(" ", [self.http_spec, self.status, self.message])
        header = str.join("\r\n", [f"Content-Type: {self.content_type}", f"Server: {self.server}"])
        body = self.html_content
        return str.join("\r\n", [start_line, header, body])
    
class HTTPServer:
    def __init__(self):
        self.PORT = 8000
        self.FILE = "FILE"
        self.FOLDER = "FOLDER"
        self.tcp_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # take out 1 minute timeout from the socket after closed
        self.tcp_listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_listener.bind(("localhost", self.PORT))
        self.tcp_listener.listen(5)
        self.listen_forever()

    def listen_forever(self):
        print(f"Server started on port {self.PORT}")
        while True:
            socket, address = self.tcp_listener.accept()
            try:
                msg = socket.recv(1024)
                http_request = HTTPRequest(msg)
                if hasattr(self, f'handle_{http_request.get_method()}'):
                    print("method implemented")
                else:
                    raise HTTPException("Method not allowed", "405")
                # file_system_nodes = self.get_file_system_nodes()
                # print(f"Request received: {socket.recv(1024)}")
                # string_to_return = ""
                # string_to_return = string_to_return+"HTTP/1.1 200\r\n\r\n"
                # string_to_return = string_to_return+"<!DOCTYPE HTML>"
                # string_to_return = string_to_return+"<html lang='en'>"
                # string_to_return = string_to_return+"<head>"
                # string_to_return = string_to_return+"<meta charset='utf-8'>"
                # string_to_return = string_to_return+"</head>"
                # string_to_return = string_to_return+"<body>"
                # string_to_return = string_to_return+"<h1>Server response</h1>"
                # string_to_return = string_to_return+"</body>"
                # string_to_return = string_to_return+"</html>"
                # string_to_return = bytes(string_to_return.encode())
                
            except HTTPException as e:
                response = HTTPResponse(e.args[0], e.status)
                socket.send(response.__str__().encode("UTF-8"))

            finally:
                socket.close()
    def get_file_system_nodes(self, path=None):
        return [{dir:self.FOLDER} if os.path.isdir(dir) else {dir:self.FILE}
                                        for dir in sorted(os.listdir(path))]
        
if __name__ == "__main__":
    HTTPServer()