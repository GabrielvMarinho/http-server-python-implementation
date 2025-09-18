class HTTPException(Exception):
    def __init__(self, args, status):
        super().__init__(args)
        self.status = status