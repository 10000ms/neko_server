class SingleHttpHeader:

    def __init__(self, key, value):
        self.key = self.format_key(key)
        self.value = value

    @classmethod
    def format_key(cls, key):
        key = key.lower()
        need_upper = True
        r = ''
        for k in key:
            if need_upper is True:
                r += k.upper()
                need_upper = False
            else:
                r += k
            if k == '-':
                need_upper = True
        return r


class HttpHeader:

    def __init__(self):
        self.single_http_headers = {}

    def add_header(self, single_http_header):
        self.single_http_headers[single_http_header.key] = single_http_header

    def __getitem__(self, item):
        k = SingleHttpHeader.format_key(item)
        return self.single_http_headers[k]

    def __contains__(self, item):
        k = SingleHttpHeader.format_key(item)
        return k in self.single_http_headers.keys()
