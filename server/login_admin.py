import logging

def _check_for_builtin(environ):
    return (
        'HTTP_X_APPENGINE_QUEUENAME' in environ or
        'HTTP_X_APPENGINE_CRON' in environ or
        False)

_no_admin = lambda x: False

def authorize_middlware(app, check_env_for_admin=_no_admin):
    def wsgi_app(environ, start_response):
        if _check_for_builtin(environ) or check_env_for_admin(environ):
            return app(environ, start_response)
        else:
            logging.warning('Failed to authorize request, environment is: %s', environ)
            status = '403 Forbidden'
            headers = [('Content-type', 'text/plain')]
            start_response(status, headers)
            return ['Forbidden']
    return wsgi_app
