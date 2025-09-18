
class HTTPRequest:
    def __init__(self, request_string):
        array_of_splitted_string = list(filter(None, str.split(request_string.decode("UTF-8"), ("\r\n"))))
        self.request_line = array_of_splitted_string[0]
        self.headers = array_of_splitted_string[1:len(array_of_splitted_string)]

    def get_method(self):
        return str.split(self.request_line, " ")[0]
    
    def get_endpoint(self):
        return str.split(self.request_line, " ")[1]