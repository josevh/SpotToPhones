import spotipy
import spotipy.util as util

class Spotify(object):
    def __init__(self, config):
        self.sp = self.__get_token(config)
    
    def __get_token(self, config):
        token = util.prompt_for_user_token(
            config.get('SPOTIPY', 'user'),
            scope= config.get('SPOTIPY', 'scope'),
            client_id= config.get('SPOTIPY', 'spotify_client_id'),
            client_secret= config.get('SPOTIPY', 'spotify_client_secret'),
            redirect_uri= config.get('SPOTIPY', 'spotify_redirect_uri'))
        if token:
            return spotipy.Spotify(auth=token)
            
    def get_playlists(self, username):
        return self.sp.user_playlists(username)
    
    def get_playlist_id(self, playlists, playlist_name):
        for playlist in playlists['items']:
            if playlist['name'] == playlist_name:
                return playlist['id']