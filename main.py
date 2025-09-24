import socket
import os
import mimetypes
from exception import HTTPException
from request import HTTPRequest
from response import HTTPResponse
from threading import Thread

class HTTPServer:
    def __init__(self):
        self.PORT = 8000
        self.FILE = "FILE"
        self.FOLDER = "FOLDER"
        # creates a tcp socket over ipv4
        self.tcp_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # take out 1 minute timeout from the socket after closed
        self.tcp_listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_listener.bind(("localhost", self.PORT))
        self.tcp_listener.listen(5)
        self.listen_forever()

    def listen_forever(self):
        print(f"Server started on port {self.PORT}")
        while True:
            socket_, _ = self.tcp_listener.accept()
            thread = Thread(target=self.handle_request, args=(socket_, ))
            thread.start()

    def handle_request(self, socket_):
        try:
            msg_buffer = b""
            #receiving each 16 bytes and storing in a buffer
            while b"\r\n\r\n" not in msg_buffer:
                data = socket_.recv(16)
                msg_buffer = msg_buffer+ data                

            http_request = HTTPRequest(msg_buffer)
            if hasattr(self, f'handle_{http_request.get_method()}'):
                http_response = getattr(HTTPServer, f'handle_{http_request.get_method()}')(self, http_request)
                socket_.send(http_response.__str__())
            else:
                raise HTTPException("Method not allowed", "405")
        except HTTPException as e:
            http_response = HTTPResponse(e.args[0], e.status, f"<h1>{e.status} {e.args[0]}</h1>")
            socket_.send(http_response.__str__())
        except Exception as e:
            socket_.send(HTTPResponse(content="<h1>Something went wrong</h1>".encode(), content_type="text/html", message="Something went wrong", status="400").__str__())

            print("Error ocurred: ", e)

        finally:
            socket_.close()
        
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
            if endpoint != "/":
                list_endpoint = str.split(endpoint, "/")
                list_endpoint = list_endpoint[1:len(list_endpoint)-1]
                endpoint_to_go_back = "/"+"/".join(str(item) for item in list_endpoint)
                html_list = html_list + f"<li style='list-style-type:none'><a href='{endpoint_to_go_back}'>../</a></li>"
            
            for node_obj in nodes:
                [(node, node_type)] = node_obj.items()
                if(node_type == self.FOLDER):
                    html_list = html_list+f"<li style='list-style-type:none'><a href='{endpoint+("/" if endpoint != "/" else "")+node}'>{node}/</a></li>"
                else:
                    html_list = html_list+f"<li style='list-style-type:none'><a href='{endpoint+ ("/" if endpoint != "/" else "")+node}'>{node}</a></li>"
            html_list = html_list+ "</ol>"
            content = f"""
                        <div>
                        <h1>{endpoint}</h1>        
                        {html_list}
                        <div/>
                        </body>
                        </html>
                        """
            return HTTPResponse(status="200", message="OK", content_type="text/html", content=content.encode())

        else:
            # return specific file
            content = open(path, "rb").read()
            content_type, _ = mimetypes.guess_type(path)            
            return HTTPResponse(status="200", message="OK", content_type=content_type, content=content)
    
    def get_file_system_nodes(self, path):
        return [{dir:self.FOLDER} if os.path.isdir(os.path.join(path, dir)) else {dir:self.FILE}
                                        for dir in sorted(os.listdir(path))]
        
if __name__ == "__main__":
    HTTPServer()