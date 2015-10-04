import pyen
import requests

class Track(object):
    '''Tracks have the following attributes:
    
        name:               A string representing the track's name.
        album:              A string representing the track's album.
        artist:             A string representing the track's artist.
        
        sp_uri:             A string representing the track's Spotify URI.
        sp_id:              A string representing the track's Spotify ID.
        sp_album_id:        A string representing the track's album's Spotify ID.
        sp_artist_id:       A string representing the track's artist's Spotify ID.
        
        mb_id:              A string representing the track's Musicbrainz ID.
        mb_album_id:        A string representing the track's Album's Musicbrainz ID.
        mb_artist_id:       A string representing the track's Artist's Musicbrainz ID.
        
        have_track:         A boolean representing whether the track is in Headphones library.
        have_album:         A boolean representing whether the track's album is in Headphones library.
        have_artist:        A boolean representing whether the artist is in Headphones library.
        
        queue_status:       A string representing the outcome of adding album to Headphones queue.
    '''

    def __init__(self, data, config):
        self.name               = data['name']
        self.album              = data['album']
        self.artist             = data['artist']
        
        self.sp_uri             = data['sp_uri']
        self.sp_id              = data['sp_id']
        self.sp_album_id        = data['sp_album_id']
        self.sp_artist_id       = data['sp_artist_id']
        
        self.config             = config
        
        self.mb_artist_id       = self.__get_mb_artist_id()
        #self.mb_id              = None
        self.mb_album_id        = self.__get_mb_album_id()
        
        #self.have_track         = None
        self.have_album         = self.__find_album_in_hp()
        self.have_artist        = self.__find_artist_in_hp()
        
        self.queue_status       = self.__queue_album_in_hp()
        
    def __get_mb_artist_id(self):
        ''' Use EchoNest API to map Spotify artist id to Musicbrainz artist id
        '''
        config = self.config
        en = pyen.Pyen(config.get('ECHONEST', 'api_key'))
        params = {
            'id':       'spotify:artist:' + self.sp_artist_id,
            'bucket':   ['id:musicbrainz'],
        }
        response = en.get('artist/profile', **params)
        if (response['status']['message'] == 'Success' and 'foreign_ids' in response['artist']):        #some artists will not return foreign id
            mbid = response['artist']['foreign_ids'][0]['foreign_id']
            return mbid[19:]    #remove 'musicbrainz:artist:'
        else:
            return 'notfound'

    def __get_mb_album_id(self):
        ''' Queries Headphone's API Musicbrainz query method to get Musicbrainz album id.
            Returns Musicbrainz album id.
            if unable to acquire, returns string 'notfound'.
        '''
        mb_album_id = None
        if self.mb_artist_id != "notfound":
            req = {'cmd': 'findAlbum', 'name': self.album + ':' + self.artist, 'limit': 15}
            count = 0
            while True: # retry connection if failed, until successful or 5 tries
                count += 1
                albumQuery = self.__callHeadphones(req)
                if isinstance(albumQuery, list):
                    break
                if count > 5:
                    mb_album_id = "notfound"
                    break
            if mb_album_id != "notfound":
                for album in albumQuery:
                  if album['id'] == self.mb_artist_id and (album['title']).lower() == (self.album).lower() and album['rgtype'] == 'Album':  #ignore case
                      mb_album_id = album['rgid']  #Headphones prefers the release group id
                      break
                  else:
                      mb_album_id = "notfound"
        else:
            mb_album_id = "notfound"
        return mb_album_id
    
    def __callHeadphones(self, req):
        config = self.config
        data = { 'apikey': config.get('HEADPHONES', 'api_key') }
        payload = {}
        for item in (data, req):
            payload.update(item)
        hp_api = "http://" + config.get('HEADPHONES', 'ip') + ":" + config.get('HEADPHONES', 'port') +  config.get('HEADPHONES', 'webroot') + "/api"
        result = requests.get(hp_api, params=payload)
        result = result.json()
        return result
        
    def __modHeadphones(self, req):
        ''' Handles POST calls to Headphones API.
            Returns response 'OK' if successful.
        '''
        config = self.config
        data = { 'apikey': config.get('HEADPHONES', 'api_key') }
        payload = {}
        for item in (data, req):
            payload.update(item)
        hp_api = "http://" + config.get('HEADPHONES', 'ip') + ":" + config.get('HEADPHONES', 'port') +  config.get('HEADPHONES', 'webroot') + "/api"
        count = 0
        while True:
            if count > 3:
                return False
            result = requests.post(hp_api, params=payload)
            if result.text == 'OK':
                return True
            count += 1
        
    def __find_artist_in_hp(self):
        if self.mb_artist_id == "notfound":
            return False
        req = {'cmd': 'getIndex'}
        library = self.__callHeadphones(req)
        status = False
        for item in library:
            if item['ArtistID'] == self.mb_artist_id:
                status = True
                break
        return status
            
    def __find_album_in_hp(self):
        if self.mb_album_id == "notfound":
            return False
        req = {'cmd': 'getAlbum', 'id': self.mb_album_id}
        check = self.__callHeadphones(req)
        if len(check['album']) > 0:
            return True
        else:
            return False
            
    def __add_artist_in_hp(self):
        if self.mb_artist_id == "notfound":
            return False
        req = {'cmd': 'addArtist', 'id': self.mb_artist_id}
        request = self.__modHeadphones(req)
        if request:
            return True
        else:
            return False
        
    def __add_album_in_hp(self):
        if self.mb_album_id == "notfound":
            return False
        req = {'cmd': 'addAlbum', 'id': self.mb_album_id}
        request = self.__modHeadphones(req)
        if request:
            return True
        else:
            return False
            
    def __queue_album_in_hp(self):
        if (self.have_artist or self.__add_artist_in_hp()) and (self.have_album or self.__add_album_in_hp()):
            # TODO: queue the album
            req = {'cmd': 'queueAlbum', 'id': self.mb_album_id}
            request = self.__modHeadphones(req)
            if request:
                return True
            else:
                return False
        else:
            return False