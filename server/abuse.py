# import IPy
# ip = IPy(request.remote_addr)
# gce_list = '130.211.0.0/16'
# gce_list.overlaps(ip)

def is_abuse(request):
    user_agent = request.headers.get('user-agent', 'NO_USER_AGENT')

    if 'python-requests' in user_agent:
        return True

    return False
