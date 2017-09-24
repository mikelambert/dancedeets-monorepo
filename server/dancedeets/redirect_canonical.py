def redirect_canonical(app, source, canonical):
    def wsgi_app(environ, start_response):
        if environ.get('HTTP_HOST') == source:
            new_url = 'https://%s%s' % (canonical, environ['PATH_INFO'])
            if environ['QUERY_STRING']:
                new_url += '?%s' % environ['QUERY_STRING']
            start_response('301 Moved Permanently', [('Location', new_url)])
            return []
        return app(environ, start_response)

    return wsgi_app
