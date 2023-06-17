class Document:
    def __init__(self, id, url, is_russian):
        self.id = id
        self.url = url
        self.is_russian = is_russian

        self.text = None
