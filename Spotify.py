import spotipy
import spotipy.util as util
import pyen
import requests

class Spotify(object):
    def __init__(self, config):
        self.playlist_wanted        = Playlist(config.get('SPOTIFY', 'wanted_playlist'))
        self.playlist_error         = Playlist(config.get('SPOTIFY', 'error_playlist'))
        self.playlist_success       = Playlist(config.get('SPOTIFY', 'success_playlist'))
        
        self.username               = config.get('SPOTIFY', 'username')
        self.scope                  = config.get('SPOTIFY', 'scope')
        self.client_id              = config.get('SPOTIFY', 'client_id')
        self.client_secret          = config.get('SPOTIFY', 'client_secret')
        self.redirect_uri           = config.get('SPOTIFY', 'redirect_uri')
        
        self.sp = self.__get_token()
        self.playlists = self.__get_playlists()
        self.__get_playlist_ids(
            self.playlist_wanted,
            self.playlist_error,
            self.playlist_success
        )
        self.__get_playlist_tracks(
            self.playlist_wanted,
            self.playlist_error,
            self.playlist_success
        )
        
        hp_worker = HeadphonesWorker(
            config.get('HEADPHONES', 'ip'),
            config.get('HEADPHONES', 'port'),
            config.get('HEADPHONES', 'webroot'),
            config.get('HEADPHONES', 'api_key'),
            config.get('ECHONEST', 'api_key')
        )
        
        self.__get_playlist_mb_ids(
            hp_worker,
            self.playlist_wanted,
            self.playlist_error,
            self.playlist_success
        )
        
        self.playlist_wanted._print()
        print ""
        for track in self.playlist_wanted.tracks:
            #if track.valid_mb_ids():
            track._print()
            print ""
            break
        print ""


    def __get_token(self):
        token = util.prompt_for_user_token(
            self.username,
            self.scope,
            self.client_id,
            self.client_secret,
            self.redirect_uri
        )
        if token:
            return spotipy.Spotify(auth=token)
            
    def __get_playlists(self):
        return self.sp.user_playlists(self.username)
    
    def __get_playlist_ids(self, *playlists):
        for playlist in playlists:
            for pl in self.playlists['items']:
                if pl['name'] == playlist.name:
                    playlist.id = pl['id']
                
    def __get_playlist_tracks(self, *playlists):
        for playlist in playlists:
            tracks = self.sp.user_playlist(self.username, playlist.id, fields="tracks")
            if len(tracks['tracks']['items']) > 0:
                for track in tracks['tracks']['items']:
                    playlist.tracks.append(
                        Track(
                            track['track']['name'],
                            track['track']['id'],
                            track['track']['artists'][0]['name'],
                            track['track']['artists'][0]['id'],
                            track['track']['album']['name'],
                            track['track']['album']['id'],
                            track['track']['album']['album_type']
                        )
                    )

    def __get_playlist_mb_ids(self, hp_worker, *playlists):
        for playlist in playlists:
            for track in playlist.tracks:
                track.artist_id_mb = hp_worker.get_mb_artist_id(track.artist_id_sp)
                track.album_id_mb = hp_worker.get_mb_album_id(
                    track.artist_name,
                    track.album_name,
                    track.artist_id_mb,
                    track.album_type
                )
                if track.valid_mb_ids():
                    track.in_hp = hp_worker.in_hp(track.artist_id_mb, track.album_id_mb)

class Playlist(object):
    def __init__(self, name):
        self.name   = name
        self.id     = ""
        self.tracks = []
    def _print(self):
        print "playlist name: " + self.name
        print "playlist id: " + self.id
        
class Track(object):
    def __init__(self, name, id, artist_name, artist_id, album_name, album_id, album_type):
        self.name           = name
        self.id_sp          = id
        
        self.artist_name    = artist_name
        self.artist_id_sp   = artist_id
        self.artist_id_mb   = ""
        
        self.album_name     = album_name
        self.album_id_sp    = album_id
        self.album_id_mb    = ""
        self.album_type     = album_type
        
        self.in_hp          = None
    def valid_mb_ids(self):
        return self.artist_id_mb is not None and self.album_id_mb is not None
    def _print(self):
        print "track name: " + self.name
        print "track artist name: " + self.artist_name
        if self.artist_id_mb is not None:
            print "track artist mb id: " + self.artist_id_mb
        print "track album name: " + self.album_name
        if self.album_id_mb is not None:
            print "track album mb id: " + self.album_id_mb
        if self.in_hp:
            print "track in hp: yes"
        
class HeadphonesWorker(object):
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
            req = {'cmd': 'findAlbum', 'name': album_name + ':' + artist_name, 'limit': 5}
            count = 0
            while True: # retry connection if failed, until successful or 5 tries
                count += 1
                albumQuery = self.__get_headphones(req)
                if isinstance(albumQuery, list):
                    for album in albumQuery:
                        if album['id'] == artist_id_mb and (album['title']).lower() == (album_name).lower() and album['rgtype'] == album_type.title():  #ignore case
                            return album['rgid']  #Headphones prefers the release group id
                    break
                if count > 5:
                    break
    def __artist_in_hp(self, mb_artist_id):
        req = {'cmd': 'getIndex'}
        library = self.__get_headphones(req)
        status = False
        for item in library:
            if item['ArtistID'] == mb_artist_id:
                return True
        return False
    def __album_in_hp(self, mb_album_id):
        req = {'cmd': 'getAlbum', 'id': mb_album_id}
        check = self.__get_headphones(req)
        return len(check['album']) > 0
    def in_hp(self, mb_artist_id, mb_album_id):
        return (self.__artist_in_hp(mb_artist_id) and self.__album_in_hp(mb_album_id))
            