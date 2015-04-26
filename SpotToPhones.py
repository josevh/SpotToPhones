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

    playlist_name = ConfigSectionMap("GENERAL")['playlist_name']

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

def callHeadphones(cmd):
    hp_user = ConfigSectionMap("HEADPHONES")['user']
    hp_pass = ConfigSectionMap("HEADPHONES")['password']
    hp_ip = ConfigSectionMap("HEADPHONES")['ip']
    # hp_root = ""  #web_root not implemented
    hp_port = ConfigSectionMap("HEADPHONES")['port']
    hp_api_key = ConfigSectionMap("HEADPHONES")['api_key']
    hp_api_url = "http://" + hp_ip + ":" + hp_port + "/api?apikey=" + hp_api_key + "&cmd="
    request = hp_api + cmd
    result = requests.get(request)
    result = result.json()
    return result

def checkHeadphones(track_data):
    #search for tracks/albums/artists in Headphones libray
    hp_index = callHeadphones('getIndex')
    for x in range(0,len(track_data)):
        spArtist = track_data[x][0]
        spAlbum = track_data[x][1]
        spTrack = track_data[x][2]
        for x in range(0,len(hp_index)):
            if hp_index[x]['ArtistName'] == spArtist:
                hp_artist_id = hp_index[x]['ArtistID']
            else:
                hp_artist_id = "notfound"
                #need to query musicbrainz for artistid
                #and query for the album id and add to wanted
                #and end this function, do not search for
                #albums and tracks since artist is not in library
                break
        #search for albums in Headphones library
        hp_query = 'getArtist&id=' + hp_artist_id
        hp_albums = callHeadphones(hp_query)
        for x in range(0,len(hp_albums)):
            if hp_albums['albums'][x]['AlbumTitle'] == spAlbum:
                hp_album_id = hp_albums['albums'][x]['AlbumID']
            else:
                hp_album_id = "notfound"
                #do stuff
                break
        #search for track if Album in library
        hp_query = 'getAlbum&id=' + hp_track_album_id
        hp_tracks = callHeadphones(hp_query)
        for x in range(0,len(hp_tracks)):
            if hp_tracks['tracks'][x]['TrackTitle'] == spTrack:
                #have the artist, album, date
                #do not queue, remove from spotify playlist
                break
            else:
                #have artist and incomplete album
                #redownload? investigate further
                #could be an issue in deluxe album vs normal
                break


    #return an array with artistid and albumid to add to headphones

def queueAlbum(artist_id, album_id):    #in headphones
    print("todo")
def getMusicbrainzArtistID():
    print("todo")
    #findArtist&name=$artistname[&limit=$limit]
    #returns artist id
def getMusicbrainzAlbumID():
    print("todo")


def main():
    track_data = getSpotTracks()
    checkHeadphones(track_data)

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
