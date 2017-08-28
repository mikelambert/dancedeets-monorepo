# import IPy
# ip = IPy(ips.get_remote_ip(self.request))
# gce_list = '130.211.0.0/16'
# gce_list.overlaps(ip)

import IPy
from util import ips

banned_list = IPy.IPSet([
    IPy.IP('188.165.25.197'),  # A scraper that hammered the site too quickly.
    IPy.IP('46.101.245.227'),  # Digital Ocean Scraper. Hammered my server for city pages, which started 502-ing on user traffic.
])


def is_abuse(request):
    user_agent = request.headers.get('user-agent', 'NO_USER_AGENT')

    if 'python-requests' in user_agent:
        return True

    ip = IPy.IP(ips.get_remote_ip(request))

    if ip in banned_list:
        return True

    return False
