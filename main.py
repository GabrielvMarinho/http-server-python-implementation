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
    
    def get_endpoint(self):
        return str.split(self.request_line, " ")[1]

class HTTPResponse:
    def __init__(self, message, status, content_type, content):
        self.http_spec = "HTTP/1.1"
        self.status = status
        self.message = message
        self.content_type = content_type
        self.server = "Marinho's HTTP server"
        self.content = content

    def __str__(self):
        start_line = str.join(" ", [self.http_spec, self.status, self.message])
        header = str.join("\r\n", [f"Content-Type: {self.content_type}", f"Server: {self.server}"])
        body = self.content
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
                    http_response = getattr(HTTPServer, f'handle_{http_request.get_method()}')(self, http_request)
                    socket.send(http_response.__str__().encode())
                else:
                    raise HTTPException("Method not allowed", "405")
            except HTTPException as e:
                http_response = HTTPResponse(e.args[0], e.status, f"<h1>{e.status} {e.args[0]}</h1>")
                socket.send(http_response.__str__().encode())

            finally:
                socket.close()

    def handle_GET(self, http_request: HTTPRequest) -> str:
        endpoint = http_request.get_endpoint()

        path = os.getcwd() +endpoint[0:len(endpoint)]
        if os.path.isdir(path):
            # return list of files
            nodes = self.get_file_system_nodes(path)
            content = """
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>200 OK</title>
                    </head>
                    <body> 
                    """
            html_list = "<ol>"
            for node_obj in nodes:
                [(node, node_type)] = node_obj.items()
                if(node_type == self.FOLDER):
                    html_list = html_list+f"<li>{node}/</li>"
                else:
                    html_list = html_list+f"<li>{node}</li>"
            html_list = html_list+ "</ol>"
            content = f"""
                        <div>
                        <h1>{endpoint}</h1>
                        {html_list}
                        <div/>
                        </body>
                        </html>
                        """
            return HTTPResponse(status="200", message="OK", content_type="text/html", content=content)

        else:
            # return specific file
            content = open(path).read()
            return HTTPResponse(status="200", message="OK", content_type="text/plain", content=content)


        
    
    def get_file_system_nodes(self, path):
        return [{dir:self.FOLDER} if os.path.isdir(os.path.join(path, dir)) else {dir:self.FILE}
                                        for dir in sorted(os.listdir(path))]
        
if __name__ == "__main__":
    HTTPServer()