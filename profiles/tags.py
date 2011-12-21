import cgi
import urlparse

from google.appengine.ext import db
from spitfire.runtime.filters import skip_filter

SITE_YOUTUBE = 'YOUTUBE'
SITE_VIMEO = 'VIMEO'

def parse_url(url):
    purl = urlparse.urlparse(url)
    #TODO(lambert): handle embed codes and the like too?
    if purl.netloc.endswith('.youtube.com'):
        qs = cgi.parse_qs(purl.query)
        return SITE_YOUTUBE, qs['v'][0]
    elif purl.netloc.endswith('.vimeo.com'):
        match = re.match(r'^/(\d+)', purl.path)
        if match:
            return SITE_VIMEO, match.group(1)
    return None, None

class ProfileVideoTag(db.Model):
    fb_uid = db.IntegerProperty(indexed=False) # TODO: make this a proper key
    tagger_fb_uid = db.IntegerProperty(indexed=False)
    video_site = db.StringProperty(indexed=False)
    video_id = db.StringProperty(indexed=False)
    description = db.StringProperty(indexed=False) # "at 0:56", or "blue guy on the left"

    #TODO(lambert): if you want to split into playlists, or control ordering, then you need to use youtube playlists. Can just hook up a youtube playlist if you want from your list. If you hook up a playlist, then auto-grab tags from that playlist, polled periodically... And then we don't have an "authoritative editor" problem. Or you can use AuthSub/OAuth to manage your playlist in some far-out future, dealing with multimaster sync issues...

    playlist_name = db.StringListProperty(indexed=False)
    approved = db.BooleanProperty(indexed=False)
    deleted = db.BooleanProperty(indexed=False)

    def get_video_page(self):
        if self.video_site == SITE_YOUTUBE:
            return "http://www.youtube.com/watch?v=%s" % self.video_id
        elif self.video_site == SITE_VIMEO:
            return "http://www.vimeo.com/%s" % self.video_id
        else:
            return "unknown!"

    @skip_filter
    def get_video_embed(self):
        if self.video_site == SITE_YOUTUBE:
            return """\
<iframe title="YouTube video player" class="youtube-player" type="text/html" width="640" height="390" src="http://www.youtube.com/embed/%(video_id)s?hd=1" frameborder="0"></iframe>
""" % dict(video_id=self.video_id)
        elif self.video_site == SITE_VIMEO:
            return """\
<iframe src="http://player.vimeo.com/video/%(video_id)s?title=0&amp;byline=0&amp;portrait=0&amp;color=7a012e" width="400" height="225" frameborder="0"></iframe>
""" % dict(video_id=self.video_id)
        else:
            return "unknown!"

    def get_profile(self):
        return "/profile/%s" % fb_uid

# for logged-in playlist fetching:
# AuthSub
# http://code.google.com/appengine/articles/python/retrieving_gdata_feeds.html
# http://code.google.com/apis/youtube/2.0/developers_guide_protocol.html#AuthSub_Authentication
# OAuth
# https://github.com/adewale/oauthstarter
# http://code.google.com/apis/youtube/2.0/developers_guide_protocol.html#OAuth_Authentication

#yt_service = gdata.youtube.service.YouTubeService()
#video_entry = yt_service.GetYouTubeVideoEntry(video_id="XXX")
