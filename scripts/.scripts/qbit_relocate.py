#!/bin/env python
import json
import contextlib
import requests

IP = "http://192.168.1.105"
AUDIO_EXTENSION = {"mp3", "ogg", "wav", "m4b", "m4a"}


class QbitApi:
    def __init__(self, username, password, ip, port=9001):
        self.username = username
        self.password = password
        self.url = ip + ':' + str(port) + "/api/v2"
        self._cookies = None
        self._torrent_list = []

    def _get(self, endpoint, **kwargs):
        """
        Method to perform GET request on the API.
        :param endpoint: Endpoint of the API.
        :param kwargs: Other keyword arguments for requests.
        :return: Response of the GET request.
        """
        return self._request(endpoint, 'get', **kwargs)

    def _post(self, endpoint, data, **kwargs):
        """
        Method to perform POST request on the API.
        :param endpoint: Endpoint of the API.
        :param data: POST DATA for the request.
        :param kwargs: Other keyword arguments for requests.
        :return: Response of the POST request.
        """
        return self._request(endpoint, 'post', data, **kwargs)

    def _request(self, endpoint, method, data=None, **kwargs):
        """
        Method to hanle both GET and POST requests.
        :param endpoint: Endpoint of the API.
        :param method: Method of HTTP request.
        :param data: POST DATA for the request.
        :param kwargs: Other keyword arguments.
        :return: Response for the request.
        """
        final_url = self.url + endpoint

        rq = self.session
        if method == 'get':
            request = rq.get(final_url, **kwargs)
        else:
            request = rq.post(final_url, data, **kwargs)

        request.raise_for_status()
        request.encoding = 'utf_8'

        if len(request.text) == 0:
            data = json.loads('{}')
        else:
            try:
                data = json.loads(request.text)
            except ValueError:
                data = request.text

        return data

    @contextlib.contextmanager
    def login(self):
        r = requests.post(url=self.url + "/auth/login", params={"username": self.username, "password": self.password})
        self._cookies = r.cookies
        yield
        self.logout()

    def logout(self):
        r = requests.get(url=self.url + "/auth/logout", cookies=self._cookies)
        self._cookies = r.cookies

    def list_torrents(self):
        r = requests.get(url=self.url + "/torrents/info", params={"username": self.username, "password": self.password},
                         cookies=self._cookies)
        return r.json()

    def get_torrents_properties(self, hash):
        r = requests.get(url=self.url + "/torrents/properties", params={"hash": hash},
                         cookies=self._cookies)
        return r.json()

    def get_torrent_files(self, hash):
        r = requests.get(url=self.url + "/torrents/files", params={"hash": hash},
                         cookies=self._cookies)
        return r.json()

    def get_torrent_tracker(self, hash):
        r = requests.get(url=self.url + "/torrents/trackers", params={"hash": hash},
                         cookies=self._cookies)
        return r.json()

    def set_torrent_location(self, hash, path):
        r = requests.post(url=self.url + "/torrents/setLocation", data={"hash": hash, "location": path},
                          cookies=self._cookies)
        pass


def _is_audio_files(file_name: str):
    ext = ""
    for s in reversed(file_name):
        if s == ".":
            break
        ext = s + ext
    return ext in AUDIO_EXTENSION


if __name__ == '__main__':
    print("Moving audiobooks from /media/Books to /media/AudioBooks")
    api = QbitApi("admin", "adminadmin", IP)
    n = 1
    with api.login():
        torrents = api.list_torrents()
        hashes_to_change = []
        for this_torrent in torrents:
            hash = this_torrent["hash"]
            t_properties = api.get_torrents_properties(hash)
            t_files = api.get_torrent_files(hash)
            t_trackers = api.get_torrent_tracker(hash)
            if any((_is_audio_files(f["name"]) for f in t_files)) and "myanonamouse" in this_torrent["tracker"] and \
                    t_properties["save_path"] == "/media/Books/":
                print(f"{n}: {this_torrent['name']}, path {t_properties['save_path']}")
                hashes_to_change.append(hash)
                n += 1
        print(f"changing location of torrent hash: {'|'.join(hashes_to_change)} to /media/AudioBooks")
        #api.set_torrent_location("|".join(hashes_to_change), "/media/AudioBooks")
        api.set_torrent_location(hashes_to_change[0], "/media/AudioBooks")
