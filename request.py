import cgi
import string
import time
import json

import webapp2

from nation import Nation


class Handler(webapp2.RequestHandler):
    """Abstract request details.

    Provides methods covering cookies and browser redirects.
    """
    _encodeMap = string.maketrans(' \'', '+*')
    _decodeMap = string.maketrans('+*', ' \'')

    def __init__(self, request=None, response=None):
        webapp2.RequestHandler.__init__(self, request, response)
        self._nation = None
        self._jsonReq = None

    def setCookie(self, key, value, timeout=999999):
        """Add a cookie to the header."""
        value = str(value).encode('ascii').translate(Handler._encodeMap)
        self.response.headers.add_header('Set-Cookie',
                                         key + '=' + value + '; '
                                         'max-age=' + str(timeout) + '; '
                                         'path=/;')

    def getCookie(self, key):
        """Read the contents of a cookie."""
        value = self.request.cookies.get(key)
        if value is not None:
            return str(value).encode('ascii').translate(Handler._decodeMap)
        else:
            return None

    def deleteCookie(self, key):
        """Delete a cookie from the client browser."""
        self.setCookie(key, '', timeout=-1)

    def inDict(self, dictionary, *args):
        """Returns True if all strings passed exist in dictionary."""
        for i in args:
            if i not in dictionary:
                return False
        return True

    def redirect(self, url):
        """Redirect client browser."""
        self.response.set_status(303)
        self.response.headers['Location'] = url
        self.response.out.write('Redirecting to <a href="%s">%s</a>' %
                                (url, url))

    def redirectToLogin(self):
        """Redirect the client browser to the login page."""
        self.redirect('/static/login.htm')

    def redirectToMap(self):
        """Redirect the client browser to the main game page."""
        self.redirect('/map')

    def loadNation(self):
        """Load the nation the client is logged in as."""
        nation = self.getCookie('nation')
        pwd = self.getCookie('pwd')
        if not nation or not pwd:
            return False
        n = Nation(nation, pwd)
        if n.exists():
            self._nation = n
            return True
        else:
            return False

    def writeLogoutJSON(self):
        self.writeJSON({'logout': True})

    def writeJSON(self, obj):
        """Write a Python object out as a JSON string."""
        self.response.headers['Content-Type'] = 'text/plain'
        j = json.JSONEncoder().encode({'response': obj,
                                       'time': int(time.time())})
        self.response.out.write(j)

    def getJSONRequest(self):
        if not self._jsonReq:
            self._jsonReq = json.loads(self.request.get('request'))
        return self._jsonReq

    def getNation(self):
        return self._nation

    def getCapitolNum(self):
        req = self.getJSONRequest()
        if 'capitol' in req:
            return req['capitol']
        c = self.getCookie('capitol')
        if c is None:
            return 0
        else:
            return int(c)
