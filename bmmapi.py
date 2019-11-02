"""Minimal BMM Api

From @Stolpervogel(Pascal Ilg) - Telegram
"""
import shutil

import requests
from requests.auth import HTTPBasicAuth


class BmmApiError(Exception):
    pass


def notAuthorized():
    return BmmApiError('Not authorized for this action!')


def notFound():
    return BmmApiError('Did not find requested object!')


def ok(response):
    return response.status_code == requests.codes.ok


def forbidden(response):
    return response.status_code == requests.codes.forbidden


def not_found(response):
    return response.status_code == requests.codes.not_found


def assert_ok(response):
    if ok(response):
        return True
    if forbidden(response):
        raise notAuthorized()
    if not_found(response):
        raise notFound()
    raise BmmApiError(
        "request returned '{0}'. Expected '200 OK'".format(
            response.status_code))


class MinimalBmmApi:
    def __init__(self, base_url):
        self.authenticated = False
        self.token = None
        self.base_url = base_url
        self.lang = 'nb'

    def _get_response(self, method, path, use_auth, **kwargs):
        url = self.base_url + path
        # 'Accept-Language': 'de-DE,de;q=0.8,en-US;q=0.6,en;q=0.4,nb;q=0.2',
        headers = {
            'Accept': 'application/json',
            'Accept-Language': '{0};q=0.8,nb;q=0.2'.format(self.lang),
            'Accept-Encoding': 'gzip, deflate, sdch, br',
        }

        auth = None
        if use_auth:
            auth = HTTPBasicAuth(self.username, self.token)

        if method == 'GET':
            return requests.get(
                url, auth=auth, params=kwargs, headers=headers)

        if method == 'POST':
            return requests.post(
                url, auth=auth, data=kwargs, headers=headers)

        raise ValueError('Unknown request method {0}!'.format(method))

    def _get(self, path, **kwargs):
        return self._get_response('GET', path, True, **kwargs)

    def _post(self, path, **kwargs):
        return self._get_response('POST', path, True, **kwargs)

    def download(self, url, path, use_auth=True):
        headers = {
            'Accept-Encoding': 'gzip, deflate, sdch, br',
        }
        auth = None
        if use_auth:
            auth = HTTPBasicAuth(self.username, self.token)

        response = requests.get(url, headers=headers, auth=auth, stream=True)
        assert_ok(response)
        path = path.translate(str.maketrans({"?": r"q"}))
        with open(path, 'wb') as fout:
            fobj = response.raw
            fobj.decode_content = True
            shutil.copyfileobj(fobj, fout)

    def authenticate(self, username, password):
        response = self._get_response(
            'POST', '/login/authentication', False,
            username=username, password=password)
        if not ok(response):
            raise ValueError(
                'Authentication failed ({0})!'.format(response.status_code))

        data = response.json()
        resp_username = data.get('username')
        if resp_username != username:
            raise ValueError('Login returned different'
                             ' username than used for login!')

        token = data.get('token')
        if not token:
            raise ValueError('Login did not return valid token!')

        self.username = username
        # self.first_name = data.get('first_name')
        # self.last_name = data.get('last_name')
        self.token = token
        self.authenticated = True

    def setLanguage(self, lang):
        if lang not in ['de', 'en', 'nb']:
            raise ValueError("Not supported language: " + lang)
        self.lang = lang

    def podcasts(self):
        response = self._get('/podcast/')
        assert_ok(response)
        return response.json()

    def podcast(self, id):
        response = self._get('/podcast/{0}'.format(id))
        assert_ok(response)
        return response.json()

    def podcastTracks(self, id):
        response = self._get('/podcast/{0}/track/'.format(id))
        assert_ok(response)
        return response.json()
