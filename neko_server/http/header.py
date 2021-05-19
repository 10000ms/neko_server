class SingleHttpHeader:

    def __init__(self, key, value):
        self.key = key.lower()
        self.value = value


class HttpHeader:

    def __init__(self):
        self.single_http_headers = []

    def add_header(self, single_http_header):
        self.single_http_headers.append(single_http_header)
