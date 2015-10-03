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
        logging.debug("Can't get token for " + username)
        sys.exit()

def main():
    playlists = getSpotPlaylists()
    tracks = getSpotTracks(playlists['Wanted Playlist ID'])
    for track in tracks:
        print("trackname: ", track.name)
        print("track artist: ", track.artist)
        print("mb artist id: ", track.mb_artist_id)
        print("mb album id: ", track.mb_album_id)
        if track.have_album:
            print("have album: True")
        else:
            print("have album: False")
        if track.have_artist:
            print("have artist: True")
        else:
            print("have artist: False")
        if track.queue_status:
            print("queue status: True")
        else:
            print("queue status: False")
        print("")
    
    # get_mb_album_id("cc2c9c3c-b7bc-4b8b-84d8-4fbd8779e493", "21")
    
config = ConfigParser.ConfigParser()
config.read("dev/config.ini")
sp = callSpotify()
    
main()

# TODO:
#     -queue album is not working
#     -move tracks to appropriate spotify playlists post process
    
    
