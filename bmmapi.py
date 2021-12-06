"""Minimal BMM Api

From @Stolpervogel(Pascal Ilg) - Telegram

Modified by Eliezer to change authentication mechanism.
    - Use token based authentication instead of basic authentication.
    - Get access token by logging in using puppeteer.
"""
import os
import re
import sys
import shutil
import subprocess

import requests


SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))


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

    lang_list = ['de', 'en', 'es', 'fi', 'fr', 'hu', 'it', 'nb', 'nl', 'pl', 'pt', 'ro', 'ru', 'sl', 'ta', 'tr']

    def __init__(self, base_url):
        self.authenticated = False
        self.token = None
        self.base_url = base_url
        self.lang = 'nb'

    def _get_token(self):
        """Call external nodejs script `get_token.js` to get access token"""
        print('Getting token')
        res = subprocess.run(
                    ['node', f'{SCRIPT_DIR}/get_token.js'],
                    stdout=subprocess.PIPE, stderr=sys.stdout,
                    text=True
                )
        token = res.stdout
        return token.strip()

    def _get_response(self, method, path, use_auth, **kwargs):
        url = self.base_url + path
        # 'Accept-Language': 'de-DE,de;q=0.8,en-US;q=0.6,en;q=0.4,nb;q=0.2',
        headers = {
            'Accept': 'application/json',
            'Accept-Language': '{0}'.format(self.lang),
            'Accept-Encoding': 'gzip, deflate, sdch, br',
            'Authorization': f'Bearer {self.token}'
        }

        if method == 'GET':
            return requests.get(
                url, params=kwargs, headers=headers)

        if method == 'POST':
            return requests.post(
                url, data=kwargs, headers=headers)

        raise ValueError('Unknown request method {0}!'.format(method))

    def _get(self, path, **kwargs):
        return self._get_response('GET', path, True, **kwargs)

    def _post(self, path, **kwargs):
        return self._get_response('POST', path, True, **kwargs)

    def download(self, url, path, use_auth=True):
        response = self.get_response_object(url, use_auth)
        path = path.translate(str.maketrans({"?": r"q"}))
        with open(path, 'wb') as fout:
            fobj = response.raw
            fobj.decode_content = True
            shutil.copyfileobj(fobj, fout)

    def get_response_object(self, url, use_auth=True):
        headers = {
            'Accept-Encoding': 'gzip, deflate, sdch, br',
        }
        query_params = { 'auth': f'Bearer {self.token}' }
        response = requests.get(url, headers=headers, stream=True, params=query_params, timeout=15)
        assert_ok(response)
        return response

    def authenticate(self, username, password):
        os.environ['BMM_USERNAME'] = username
        os.environ['BMM_PASSWORD'] = password
        self.token = self._get_token()
        if not self.token or re.search(r'\s', self.token):
            self.authenticated = False
        else:
            self.authenticated = True

    def is_authenticated(self):
        return self.authenticated

    def setLanguage(self, lang):
        if lang not in self.lang_list:
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
