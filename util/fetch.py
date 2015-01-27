import urllib2

def fetch_data(url):
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        mimetype = response.info().getheader('Content-Type')
        return mimetype, response.read()
