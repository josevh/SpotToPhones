## Work in progress

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
    token = util.prompt_for_user_token(username,
        scope=app_scope,
        client_id=ConfigSectionMap("SPOTIPY")['spotipy_client_id'],
        client_secret=ConfigSectionMap("SPOTIPY")['spotipy_client_secret'],
        redirect_uri=ConfigSectionMap("SPOTIPY")['spotipy_redirect_uri'])
    if token:
        sp = spotipy.Spotify(auth=token)
        playlists = sp.user_playlists(username)
        pp.pprint(playlists)
    else:
        print("Can't get token for " + username)
        sys.exit()

    playlist_name = ConfigSectionMap("General")['playlist_name']
    track_data = []
    track_data.append([])
    track_data.append([])

    playlists = sp.user_playlists(username)

    for playlist in playlists['items']:
        print("x_ playlistname: " + playlist_name)
        if playlist['name'] == playlist_name:
            print("x_ playlist name matches\n")
            tracks = sp.user_playlist(username, playlist['id'], fields="tracks")
        else:
            print("Unable to find playlist.")
            sys.exit()

    x = 0
    for track in tracks['tracks']['items']:
        #artist, album, track
        track_data[x].append(track['track']['artists'][0]['name'])
        track_data[x].append(track['track']['album']['name'])
        track_data[x].append(track['track']['name'])
        # track_album = track['track']['album']['name']
        # track_artist = track['track']['artists'][0]['name']
        # track_name = track['track']['name']
        x+=1
    print(track_data[0][0])
    print(track_data[0][1])
    print(track_data[0][2])
    print(track_data[1][0])
    print(track_data[1][1])
    print(track_data[1][2])
    print(track_data[2][0])
    print(track_data[2][1])
    print(track_data[2][2])
    print("end of getSpotTracks")

def main():
    getSpotTracks()


main()
##########testing#############################################################
