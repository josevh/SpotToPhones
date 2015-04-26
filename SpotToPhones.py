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
Config.read("config.ini")
logging.basicConfig(filename='SpotToPhones.log',level=logging.DEBUG)
pp = pprint.PrettyPrinter(indent=4, depth=2)

def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

def getSpotTracks():
    app_scope = ConfigSectionMap("SPOTIPY")['scope']
    username = ConfigSectionMap("SPOTIPY")['user']
    token = util.prompt_for_user_token(username, scope=app_scope,
        client_id=ConfigSectionMap("SPOTIPY")['spotipy_client_id'],
        client_secret=ConfigSectionMap("SPOTIPY")['spotipy_client_secret'],
        redirect_uri=ConfigSectionMap("SPOTIPY")['spotipy_redirect_uri'])

    if token:
        sp = spotipy.Spotify(auth=token)
        playlists = sp.user_playlists(username)
    else:
        print("Can't get token for " + username)
        sys.exit()

    playlist_name = ConfigSectionMap("General")['playlist_name']

    playlists = sp.user_playlists(username)

    playlist_found_test = 0
    for playlist in playlists['items']:
        if playlist['name'] == playlist_name:
            tracks = sp.user_playlist(username, playlist['id'], fields="tracks")
            playlist_found_test = 1
            break

    if playlist_found_test == 0:
        print("Did not find playlist.")
        sys.exit()

    track_data = []

    x = 0
    for track in tracks['tracks']['items']:
        track_data.append([])           #adds a new row in 2d array/list
        #pp.pprint(track['track'])        
        #artist, album, track
        track_artist = track['track']['artists'][0]['name']
        track_album = track['track']['album']['name']
        track_name = track['track']['name']
        track_data[x].append(track_artist)
        track_data[x].append(track_album)
        track_data[x].append(track_name)
        x+=1
    
    return track_data
    
def main():
    track_data = getSpotTracks()
    
    ### TESTING ###
    print(track_data[0][0]) #[0] artist
    print(track_data[0][1]) #[0] album
    print(track_data[0][2]) #[0] track
    print(track_data[1][0])
    print(track_data[1][1])
    print(track_data[1][2])
    print(track_data[2][0])
    print(track_data[2][1])
    print(track_data[2][2])


main()
