from urllib.request import Request, urlopen


def fetch_data(url):
    # In Python 3, URL must be a string not bytes
    if isinstance(url, bytes):
        url = url.decode('utf-8')
    req = Request(url)
    response = urlopen(req)
    mimetype = response.info().get('Content-Type')
    return mimetype, response.read()
