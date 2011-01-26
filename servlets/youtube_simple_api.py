import gdata.youtube.service

import base_servlet

class YoutubeSimpleApiHandler(base_servlet.BareBaseRequestHandler):
    def get(self):
        action = self.request.get('action')
        yt_service = gdata.youtube.service.YouTubeService()
        if action == 'favorites':
            username = self.request.get('username')
            text_query = self.request.get('query')
            query = gdata.youtube.service.YouTubeUserQuery(username=username, feed_type=action, text_query=text_query, params={'max-results': '50'})
            feed = yt_service.YouTubeQuery(query)
        elif action == 'playlists':
            username = self.request.get('username')
            text_query = self.request.get('query')
            query = gdata.youtube.service.YouTubeUserQuery(username=username, feed_type=action, text_query=text_query, params={'max-results': '50'})
            result = yt_service.Query(query.ToUri())
            #feed = yt_service.YouTubeQuery(query)
            feed = gdata.youtube.YouTubePlaylistFeedFromString(result.ToString())
        elif action == 'one_playlist':
            username = self.request.get('username')
            text_query = self.request.get('query')
            playlist_id = self.request.get('playlist_id')
            query = gdata.youtube.service.YouTubePlaylistQuery(playlist_id=playlist_id, text_query=text_query, params={'max-results': '50'})
            result = yt_service.Query(query.ToUri())
            feed = gdata.youtube.YouTubePlaylistVideoFeedFromString(result.ToString())
        elif action == 'search':
            text_query = self.request.get('query')
            query = gdata.youtube.service.YouTubeVideoQuery(text_query=text_query, params={'max-results': '50'})
            feed = yt_service.YouTubeQuery(query)
        else:
            assert False
        print '\n\n'
        for entry in feed.entry:
            if isinstance(entry, gdata.youtube.YouTubePlaylistEntry):
                pid = entry.id.text.split('/')[-1]
                print 'Playlist title: %s: %s' % (pid, entry.title.text)
            else:
                print 'Video title: %s' % entry.media.title.text


