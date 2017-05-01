def get_remote_ip(request):
    # This is bogus Google IPs: self.request.remote_addr
    return request.headers.get('x-forwarded-for', '127.0.0.1').split(', ')[0]
