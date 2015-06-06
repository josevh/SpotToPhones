from __future__ import absolute_import
from __future__ import print_function
import ssl
import sys
import spotipy
import spotipy.util as util
import requests
import pprint
import logging
import ConfigParser

Config = ConfigParser.ConfigParser()
Config.read("dev/config.ini")
logging.basicConfig(filename='SpotToPhones.log',level=logging.DEBUG)
pp = pprint.PrettyPrinter(indent=4, depth=2)
playlist_data = []


def ConfigSectionMap(section):
    ''' Return vars from config.ini to a dict object.
    '''
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            logging.debug("Exception on %s!" % option)
            dict1[option] = None
    return dict1

''' HEADPHONES API URL
'''
hp_api = "http://" + ConfigSectionMap("HEADPHONES")['ip'] + ":" + ConfigSectionMap("HEADPHONES")['port'] +  ConfigSectionMap("HEADPHONES")['webroot'] + "/api"

def callSpotify():
    ''' Get and return Auth Token from Spotify for API calls.
    '''
    app_scope = ConfigSectionMap("SPOTIPY")['scope']
    username = ConfigSectionMap("SPOTIPY")['user']
    token = util.prompt_for_user_token(username, scope=app_scope,
    client_id=ConfigSectionMap("SPOTIPY")['spotify_client_id'],
    client_secret=ConfigSectionMap("SPOTIPY")['spotify_client_secret'],
    redirect_uri=ConfigSectionMap("SPOTIPY")['spotify_redirect_uri'])

    if token:
        sp = spotipy.Spotify(auth=token)
        return sp
    else:
        logging.debug("Can't get token for " + username)
        sys.exit()

def getSpotTracks(sp):
    ''' Get playlist tracks' artist and album information.
        Returns a dict object with all tracks' information.
    '''
    username = ConfigSectionMap("SPOTIPY")['user']
    playlists = sp.user_playlists(username)
    playlist_name = ConfigSectionMap("GENERAL")['wanted_playlist']

    playlist_found_test = 0
    for playlist in playlists['items']:
        #Get playlist id's of all our playlists in one go
        if playlist['name'] == playlist_name:
            pdata = {
                'Wanted Playlist Name': playlist_name,
                'Wanted Playlist ID': playlist['id']
                }
        if playlist['name'] == ConfigSectionMap("GENERAL")['error_playlist']:
            pdata1 = {
                'Error Playlist Name': ConfigSectionMap("GENERAL")['error_playlist'],
                'Error Playlist ID': playlist['id']
                }
        if playlist['name'] == ConfigSectionMap("GENERAL")['wanted_playlist']:
            pdata2 = {
                'Snatched Playlist Name': ConfigSectionMap("GENERAL")['snatched_playlist'],
                'Snatched Playlist ID': playlist['id']
                }
            playlist_data.append(pdata)
            playlist_data.append(pdata1)
            playlist_data.append(pdata2)
            tracks = sp.user_playlist(username, playlist['id'], fields="tracks")
            playlist_found_test = 1
            break

    if playlist_found_test == 0:
        logging.debug("Did not find playlist.")
        sys.exit()

    track_data = []

    for track in tracks['tracks']['items']:
        data = {
            'Artist': track['track']['artists'][0]['name'],
            'Album': track['track']['album']['name'],
            'Track': track['track']['name'],
            'URI': track['track']['uri'],
            }
        track_data.append(data)

    return track_data

def callHeadphones(req):
    global hp_api
    data = { 'apikey': ConfigSectionMap("HEADPHONES")['api_key'] }
    payload = {}
    for item in (data, req):
        payload.update(item)
    result = requests.get(hp_api, params=payload)
    result = result.json()
    return result

def modHeadphones(req):
    ''' Handles POST calls to Headphones API.
        Returns response 'OK' if successful.
    '''
    global hp_api
    data = {'apikey': ConfigSectionMap("HEADPHONES")['api_key']}
    payload = {}
    for item in (data, req):
        payload.update(item)
    count = 0
    while True:
        result = requests.post(hp_api, params=payload)
        if result.text == 'OK':
            break
        if count >= 1:
            break
        count += 1
    return result.text

def checkHeadphones(track_data):
    ''' Calls Headphones API to check if tracks are present in library.
        Appends artist and/or album id's to track_data dict.
        If information is not found, will store string 'notfound'.
    '''
    req = {'cmd': 'getIndex'}
    hp_index = callHeadphones(req)
    for i in range(0,len(track_data)):
        spArtist = track_data[i]['Artist']
        spAlbum = track_data[i]['Album']
        spTrack = track_data[i]['Track']
        if hp_index: # check if Headphones library is empty
            # search for artist in library
            for j in range(0,len(hp_index)):
                if hp_index[j]['ArtistName'] == spArtist:
                    hp_artist_id = hp_index[j]['ArtistID']

                    # search for albums in Headphones library
                    req ={'cmd': 'getArtist', 'id': hp_artist_id}
                    hp_albums = callHeadphones(req)
                    for k in range(0,len(hp_albums['albums'])):
                        if hp_albums['albums'][k]['AlbumTitle'] == spAlbum:
                            hp_album_id = hp_albums['albums'][k]['AlbumID']

                            # search for track, Album is in library
                            req = {'cmd': 'getAlbum', 'id': hp_album_id}
                            hp_tracks = callHeadphones(req)
                            for l in range(0,len(hp_tracks['tracks'])):
                                if hp_tracks['tracks'][l]['TrackTitle'] == spTrack:
                                    hp_track_test = "found"
                                    break
                                else:
                                    hp_track_test = "notfound"
                            break
                        else:
                            hp_album_id = getMusicbrainzAlbumID(hp_artist_id, spAlbum)
                            hp_track_test = "notfound"
                    break
                else:
                    hp_artist_id = getMusicbrainzArtistID(spArtist)
                    hp_album_id = getMusicbrainzAlbumID(hp_artist_id, spAlbum)
                    hp_track_test = "notfound"
            track_data[i]['Artist ID'] = hp_artist_id
            track_data[i]['Album ID'] = hp_album_id
            track_data[i]['Track Test'] = hp_track_test
        else:   # headphones library is empty
            hp_artist_id = getMusicbrainzArtistID(spArtist)
            hp_album_id = getMusicbrainzAlbumID(hp_artist_id, spAlbum)
            hp_track_test = "notfound"
            track_data[i]['Artist ID'] = hp_artist_id
            track_data[i]['Album ID'] = hp_album_id
            track_data[i]['Track Test'] = hp_track_test
    return track_data

def getMusicbrainzArtistID(sp_artist_name):
    ''' Queries Headphone's API Musicbrainz query method to get Musicbrainz artist id.
        Returns Musicbrainz artist id.
        if unable to acquire, returns string 'notfound'.
    '''
    hp_artist_id = ''
    req = {'cmd': 'findArtist', 'name': sp_artist_name, 'limit': 10}
    count = 0
    while True: # retry connection if failed, until successful or 5 tries
        count += 1
        artistQuery = callHeadphones(req)
        if isinstance(artistQuery, list):
            break
        if count > 5:
            hp_artist_id = "notfound"
            break
    if hp_artist_id != "notfound":
        for artist in artistQuery:
            # cannot reliably verify artist name matches
            # probs: order of lname & fname; identically named artists with score 100, for ex. 'Lorde'
            if artist['score'] > 90:    
                hp_artist_id = artist['id']
                break
            else:
                hp_artist_id = "notfound"
    return hp_artist_id

def getMusicbrainzAlbumID(hp_artist_id, sp_album_name):
    ''' Queries Headphone's API Musicbrainz query method to get Musicbrainz album id.
        Returns Musicbrainz album id.
        if unable to acquire, returns string 'notfound'.
    '''
    hp_album_id = ''
    req = {'cmd': 'findAlbum', 'name': sp_album_name, 'limit': 15}
    count = 0
    while True: # retry connection if failed, until successful or 5 tries
        count += 1
        albumQuery = callHeadphones(req)
        if isinstance(albumQuery, list):
            break
        if count > 5:
            hp_album_id = "notfound"
            break
    if hp_album_id != "notfound":
        for album in albumQuery:
           if album['id'] == hp_artist_id and (album['title']).lower() == (sp_album_name).lower():  #ignore case
               hp_album_id = album['rgid']  #Headphones prefers the release group id
               break
           else:
               hp_album_id = "notfound"
    return hp_album_id

def queueAlbum(sp, hp_track_data):
    ''' Request tracks' album is downloaded by calling Headphones API.
        If artist id and/or album id is string 'notfound', does nothing. 
    '''
    snatchedTracks = []
    errorTracks = []
    for x in range(0,len(hp_track_data)):
        if hp_track_data[x]['Track Test'] == "found":
            snatchedTracks.append(hp_track_data[x]['URI'])
            # already have artist, album, track. End.
            # remove from playlist, do not queue
        elif hp_track_data[x]['Artist ID'] == "notfound" or hp_track_data[x]['Album ID'] == "notfound":
            errorTracks.append(hp_track_data[x]['URI'])
            # could not locate artist id or album id on musicbrainz, try again next time
            # or will have to be downloaded manually, or add song from diff album release
        else:
            # add artist to headphones db
            req = {'cmd': 'addArtist', 'id': hp_track_data[x]['Artist ID']}
            artistReq = modHeadphones(req)
            if artistReq == 'OK':
                # add album to headphones db
                req = {'cmd': 'addAlbum', 'id': hp_track_data[x]['Album ID']}
                albumReq = modHeadphones(req)
                if albumReq == 'OK':
                    # request album be downloaded
                    req = {'cmd': 'queueAlbum', 'id': hp_track_data[x]['Album ID']}
                    queue = modHeadphones(req)
                    if queue == 'OK':
                        snatchedTracks.append(hp_track_data[x]['URI'])
                    else:
                        logging.debug("queueAlbum for " + hp_track_data[x]['Album'] + " by " + hp_track_data[x]['Artist'] + "not successful.")
                else:
                    logging.debug("addAlbum for " + hp_track_data[x]['Album'] + " by " + hp_track_data[x]['Artist'] + "not successful.")
            else:
                logging.debug("addArtist for " + hp_track_data[x]['Album'] + " by " + hp_track_data[x]['Artist'] + "not successful.")
                        
    remFromSpotPlaylist(sp, snatchedTracks) #does not specify playlist id
    addToSnatchedPL(sp, snatchedTracks)
    addToErrorPL(sp, errorTracks)
    
def remFromSpotPlaylist(sp, tracks):
    ''' Calls on Spotify API to remove tracks from wanted_playlist if download requested
        Method does not give option to choose what playlist to remove from, possibly in future if needed.
    '''
    username = ConfigSectionMap("SPOTIPY")['user']
    playlist_id = playlist_data[0]['Wanted Playlist ID']
    remCall = sp.user_playlist_remove_all_occurrences_of_tracks(username,playlist_id,tracks)

def addToSpotPlaylist(sp, playlist_id, tracks):
    ''' Calls on Spotify API to add tracks to a playlist.
        Playlist is specified by arg:playlist_id when called.
    '''
    username = ConfigSectionMap("SPOTIPY")['user']
    addCall = sp.user_playlist_add_tracks(username, playlist_id, tracks)
    
def addToErrorPL(sp, tracks):
    ''' Albums which were not matched successfully and/or not queued
        will be moved to a new playlist.
    '''
    playlist_id = playlist_data[0]['Error Playlist ID']
    addToSpotPlaylist(sp, playlist_id, tracks)
    
    
def addToSnatchedPL(sp, tracks):
    ''' Albums which were matched successfully and/or queued
        will be moved to a new playlist.
    '''
    playlist_id = playlist_data[0]['Snatched Playlist ID']
    addToSpotPlaylist(sp, playlist_id, tracks)
    
def main():
    sp = callSpotify()
    track_data = getSpotTracks(sp)
    track_data = checkHeadphones(track_data)
    queueAlbum(sp, track_data)
    toSnatchedPL(sp, track_data)
    toErrorPL(sp, track_data)

    '''
    ### TESTING ###
    #pp.pprint(hp_track_data)
    print(playlist_data[0]['Wanted Playlist Name'])
    print(playlist_data[0]['Wanted Playlist ID'])
    print("")

    for x in range(0,len(track_data)):
        print("Artist: ", track_data[x]['Artist'])
        print("Artist ID: ", track_data[x]['Artist ID'])
        print("Album: ", track_data[x]['Album'])
        print("Album ID: ", track_data[x]['Album ID'])
        print("Track: ", track_data[x]['Track'])
        print("Track Test: ", track_data[x]['Track Test'])
        print("Track URI: ", track_data[x]['URI'])
        print("")
    '''    
main()
