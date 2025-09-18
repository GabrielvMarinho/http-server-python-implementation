class HTTPResponse:
    def __init__(self, message, status, content_type, content):
        self.http_spec = "HTTP/1.1"
        self.status = status
        self.message = message
        self.content_type = content_type
        self.server = "http-server"
        self.content = content

    def __str__(self):
        start_line = str.join(" ", [self.http_spec, self.status, self.message])
        header = str.join("", [f"Content-Type: {self.content_type}\r\n", f"Server: {self.server}\r\n"])
        body = self.content
        return bytes.join(b"\r\n", [start_line.encode(), header.encode(), body])
    