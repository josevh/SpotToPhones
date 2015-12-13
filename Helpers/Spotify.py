import spotipy
import spotipy.util as util
from Track import Track
from Playlist import Playlist

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
        
        self.working_playlists      = []
        self.working_playlists.append(self.playlist_wanted)
        self.working_playlists.append(self.playlist_success)
        self.working_playlists.append(self.playlist_error)
        
        self.sp = self.__get_token()
        self.playlists = self.__get_playlists()
        
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
    
    def get_playlist_ids(self, playlists):
        for playlist in playlists:
            for pl in self.playlists['items']:
                if pl['name'] == playlist.name:
                    playlist.id = pl['id']
                
    def get_playlist_tracks(self, playlists):
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
                return True
            else:
                return False

    def get_playlist_mb_ids(self, hp_worker, playlists):
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
                    track.artist_in_hp = hp_worker.artist_in_hp(track.artist_id_mb)
                    track.album_in_hp = hp_worker.album_in_hp(track.album_id_mb)
    def add_tracks_hp(self, hp_worker, playlist):
        for track in playlist.tracks:
            if track.artist_in_hp and track.album_in_hp:
                track.add_result    = True
            else:
                if hp_worker.add_track(track.artist_id_mb, track.album_id_mb):
                    track.add_result    = True
                else:
                    track.add_result    = False
                    
    def __playlist_rem_track(self, playlist_id, track_id):
        ''' Calls on Spotify API to remove tracks from wanted_playlist if download requested
            Method does not give option to choose what playlist to remove from, possibly in future if needed.
        '''
        tracks = [track_id]
        self.sp.user_playlist_remove_all_occurrences_of_tracks(
            self.username,
            playlist_id,
            tracks
        )

    def __playlist_add_track(self, playlist_id, track_id):
        ''' Calls on Spotify API to add tracks to a playlist.
            Playlist is specified by arg:playlist_id when called.
        '''
        tracks = [track_id]
        self.sp.user_playlist_add_tracks(
            self.username,
            playlist_id,
            tracks
        )
    
    def __playlist_move(self, track):
        if track.add_result is None:      #not success, not error, pass
            pass
        elif track.add_result:            #True == success
            self.__playlist_rem_track(self.playlist_wanted.id, track.id)
            self.__playlist_add_track(self.playlist_success.id, track.id)
        elif not track.add_result:        #False == error
            self.__playlist_rem_track(self.playlist_wanted.id, track.id)
            self.__playlist_add_track(self.playlist_error.id, track.id)
        else:                       #else, what???
            pass
    def playlist_move_tracks(self, playlist):
        for track in playlist.tracks:
            self.__playlist_move(track)
            
