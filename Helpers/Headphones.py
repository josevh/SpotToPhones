import requests
import pyen
import time                 #used for pause in add_track method

class Headphones(object):
    def __init__(self, ip, port, webroot, api_key, echonest_api_key):
        self.ip                 = ip
        self.port               = port
        self.webroot            = webroot
        self.api_key            = api_key
        self.echonest_api_key   = echonest_api_key
    def __get_headphones(self, req):
        data = { 'apikey': self.api_key }
        params = {}
        for item in (data, req):
            params.update(item)
        hp_api = "http://" + self.ip + ":" + self.port + self.webroot + "/api"
        result = requests.get(hp_api, params=params)
        result = result.json()
        return result
    def __post_headphones(self, req):
        ''' Handles POST calls to Headphones API.
            Returns response 'OK' if successful.
        '''
        data = { 'apikey': self.api_key }
        params = {}
        for item in (data, req):
            params.update(item)
        hp_api = "http://" + self.ip + ":" + self.port +  self.webroot + "/api"
        count = 0
        while True:
            if count > 3:
                return False
            result = requests.post(hp_api, params=params)
            if result.text == 'OK':
                return True
            count += 1
        return False
    def get_mb_artist_id(self, sp_artist_id):
        ''' Use EchoNest API to map Spotify artist id to Musicbrainz artist id
        '''
        en = pyen.Pyen(self.echonest_api_key)
        params = {
            'id':       'spotify:artist:' + sp_artist_id,
            'bucket':   ['id:musicbrainz'],
        }
        response = en.get('artist/profile', **params)
        if (response['status']['message'] == 'Success' and 'foreign_ids' in response['artist']):        #some artists will not return foreign id
            mbid = response['artist']['foreign_ids'][0]['foreign_id']
            return mbid[19:]    #remove 'musicbrainz:artist:'
    def get_mb_album_id(self, artist_name, album_name, artist_id_mb, album_type):
        ''' Queries Headphone's API Musicbrainz query method to get Musicbrainz album id.
            Returns Musicbrainz album id.
        '''
        if artist_id_mb:
            req = {'cmd': 'findAlbum', 'name': album_name + ':' + artist_name, 'limit': 10}
            count = 0
            while True: # retry connection if failed, until successful or 5 tries
                count += 1
                albumQuery = self.__get_headphones(req)
                if isinstance(albumQuery, list):
                    for album in albumQuery:
                        if (
                            album['id']             == artist_id_mb and
                            album['title'].lower()  == (album_name).lower() and
                            album['rgtype']         == album_type.title()
                        ):
                            return album['rgid']  #Headphones prefers the release group id
                    break
                if count > 5:
                    break
    def artist_in_hp(self, artist_id_mb):
        req = {'cmd': 'getIndex'}
        library = self.__get_headphones(req)
        status = False
        for item in library:
            if item['ArtistID'] == artist_id_mb:
                return True
        return False
    def album_in_hp(self, album_id_mb):
        req = {'cmd': 'getAlbum', 'id': album_id_mb}
        check = self.__get_headphones(req)
        return len(check['album']) > 0
    def __add_artist(self, artist_id_mb):
        req = {'cmd': 'addArtist', 'id': artist_id_mb}
        return self.__post_headphones(req)
    def __add_album(self, album_id_mb):
        req = {'cmd': 'addAlbum', 'id': album_id_mb}
        return self.__post_headphones(req)
    def __queue_album(self, album_id_mb):
        req = {'cmd': 'queueAlbum', 'id': album_id_mb}
        return self.__post_headphones(req)
    def add_track(self, artist_id_mb, album_id_mb):
        task1 = self.__add_artist(artist_id_mb)
        time.sleep(3)
        task2 = self.__add_album(album_id_mb)
        time.sleep(3)
        task3 = self.__queue_album(album_id_mb)
        time.sleep(3)
        return task1 and task2 and task3
        #TODO: test without sleep, calls to add tracks to hp already slow as is