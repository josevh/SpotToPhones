import ConfigParser
import spotipy
import spotipy.util as util
from track import Track

def getSpotPlaylists():
    playlists = sp.user_playlists(config.get('SPOTIPY', 'user'))
    wanted_playlist_found_test = 0
    playlist_found_count = 0
    pdata = {}
    for playlist in playlists['items']:
        #Get playlist id's of all our playlists in one go
        if playlist['name'] == config.get('GENERAL', 'error_playlist'):
            pdata['Error Playlist Name'] = config.get('GENERAL', 'error_playlist')
            pdata['Error Playlist ID'] = playlist['id']
            playlist_found_count += 1
        if playlist['name'] == config.get('GENERAL', 'snatched_playlist'):
            pdata['Snatched Playlist Name'] = config.get('GENERAL', 'snatched_playlist')
            pdata['Snatched Playlist ID'] = playlist['id']
            playlist_found_count += 1
        if playlist['name'] == config.get('GENERAL', 'wanted_playlist'):
            pdata['Wanted Playlist Name'] = config.get('GENERAL', 'wanted_playlist')
            pdata['Wanted Playlist ID'] = playlist['id']
            playlist_found_count += 1
            wanted_playlist_found_test = 1
        if playlist_found_count >= 3: #dup playlist names allowed?
            break
    if wanted_playlist_found_test == 0:
          logging.debug("Did not find wanted playlist.")
          sys.exit()
    if playlist_found_count < 3:
        logging.debug("Did not find one of snatched or error playlists.")
        sys.exit()
    return pdata

def getSpotTracks(playlist_id):
    ''' Get playlist tracks' artist and album information.
        Returns a dict object with all tracks' information.
    '''
    tracks = sp.user_playlist(config.get('SPOTIPY', 'user'), playlist_id, fields="tracks")

    if tracks['tracks']['total'] == 0:
        logging.info("Playlist was empty.")
        sys.exit()
    
    track_data = []
    
    for track in tracks['tracks']['items']:
        data = {
            'artist': track['track']['artists'][0]['name'],
            'album': track['track']['album']['name'],
            'name': track['track']['name'],
            'sp_uri': track['track']['uri'],
            'sp_artist_id': track['track']['artists'][0]['id'],
            'sp_album_id': track['track']['album']['id'],
            'sp_id': track['track']['id'],
            }
        track_data.append(data)
        
    track_objs = [Track(data, config) for data in track_data]
    return track_objs
        
def callSpotify():
    ''' Get and return Auth Token from Spotify for API calls.
    '''
    token = util.prompt_for_user_token(config.get('SPOTIPY', 'user'), scope= config.get('SPOTIPY', 'scope'),
        client_id= config.get('SPOTIPY', 'spotify_client_id'),
        client_secret= config.get('SPOTIPY', 'spotify_client_secret'),
        redirect_uri= config.get('SPOTIPY', 'spotify_redirect_uri'))

    if token:
        sp = spotipy.Spotify(auth=token)
        return sp
    else:
        logging.debug("Can't get token for " + config.get('SPOTIPY', 'user'))
        sys.exit()
        
def remFromSpotPlaylist(sp, tracks):
    ''' Calls on Spotify API to remove tracks from wanted_playlist if download requested
        Method does not give option to choose what playlist to remove from, possibly in future if needed.
    '''
    playlist_id = playlists['Wanted Playlist ID']
    remCall = sp.user_playlist_remove_all_occurrences_of_tracks(config.get('SPOTIPY', 'user'),playlist_id,tracks)

def addToSpotPlaylist(sp, playlist_id, tracks):
    ''' Calls on Spotify API to add tracks to a playlist.
        Playlist is specified by arg:playlist_id when called.
    '''
    sp.user_playlist_add_tracks(config.get('SPOTIPY', 'user'), playlist_id, tracks)

def addToErrorPL(sp, tracks):
    ''' Albums which were not matched successfully and/or not queued
        will be moved to a new playlist.
    '''
    playlist_id = playlists['Error Playlist ID']
    addToSpotPlaylist(sp, playlist_id, tracks)


def addToSnatchedPL(sp, tracks):
    ''' Albums which were matched successfully and/or queued
        will be moved to a new playlist.
    '''
    playlist_id = playlists['Snatched Playlist ID']
    addToSpotPlaylist(sp, playlist_id, tracks)



def main():
    tracks = getSpotTracks(playlists['Wanted Playlist ID'])
    
    snatchedTracks = []
    errorTracks = []
    for track in tracks:
        if track.queue_status:
            snatchedTracks.append(track.sp_uri)
            print "Moved " + track.name + " to snatched pl"
        else:
            errorTracks.append(track.sp_uri)
            print "Moved " + track.name + " to error pl"
            
    if len(snatchedTracks) > 0:
      remFromSpotPlaylist(sp, snatchedTracks)
      addToSnatchedPL(sp, snatchedTracks)
    if len(errorTracks) > 0:
      remFromSpotPlaylist(sp, errorTracks)
      addToErrorPL(sp, errorTracks)
            
    
config = ConfigParser.ConfigParser()
config.read("config.ini")
sp = callSpotify()
playlists = getSpotPlaylists()

main()
