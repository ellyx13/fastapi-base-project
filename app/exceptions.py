class CustomException(Exception):
    def __init__(self, type: str, title: str, status: int, detail: str):
        self.type = type
        self.status = status
        self.title = title
        self.detail = detail
