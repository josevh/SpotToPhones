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
    hp_track_data = []
    for x in range(0,len(track_data)):
        hp_track_data.append([])           #adds a new row in 2d array/list
        spArtist = track_data[x][0]
        spAlbum = track_data[x][1]
        spTrack = track_data[x][2]

        #search for artists in Headphones library, in future check getWanted also
        # could mean that album is already in queue, might be non-issue
        for x in range(0,len(hp_index)):
            if hp_index[x]['ArtistName'] == spArtist:
                hp_artist_id = hp_index[x]['ArtistID']

                #search for albums in Headphones library
                hp_query = 'getArtist&id=' + hp_artist_id
                hp_albums = callHeadphones(hp_query)
                for x in range(0,len(hp_albums)):
                    if hp_albums['albums'][x]['AlbumTitle'] == spAlbum:
                        hp_album_id = hp_albums['albums'][x]['AlbumID']

                        #search for track if Album in library
                        hp_query = 'getAlbum&id=' + hp_track_album_id
                        hp_tracks = callHeadphones(hp_query)
                        for x in range(0,len(hp_tracks)):
                            if hp_tracks['tracks'][x]['TrackTitle'] == spTrack:
                                hp_track_test = "found"
                                break
                            else:
                                hp_track_test = "notfound"
                                #have artist and incomplete album
                                #redownload? investigate further how Headphones handles
                                #could be an issue in deluxe album vs reg
                    else:
                        hp_album_id = getMusicbrainzAlbumID(spAlbum, hp_artist_id)
                        hp_track_test = "notfound"
            else:
                hp_artist_id = getMusicbrainzArtistID(spArtist)
                hp_album_id = getMusicbrainzAlbumID(spAlbum, hp_artist_id)
                hp_track_test = "notfound"
        hp_track_data[x].append(hp_artist_id)
        hp_track_data[x].append(hp_album_id)
        hp_track_data[x].append(hp_track_test)
    return hp_track_data

def queueAlbum(hp_track_data):    #in headphones
    for x in range(0,len(hp_track_data)):
        y = 3 * (x + 1)
        if hp_track_data[x][y] == "found":
            remFromSpotPlaylist()
            #alredy have artist, album, track. End.
            #remove from playlist, do not queue
        else:
            hp_query = '#queueAlbum&id=' + hp_track_data[x][2]
            callHeadphones(hp_query)
            #queueAlbum&id=$albumid[&new=True&lossless=True]
def getMusicbrainzArtistID(sp_artist_name):
    hp_query = 'findArtist&name=' + sp_artist_name + '&limit=25'
    artistQuery = callHeadphones(hp_query)
    #loop through list
    #match 'name'
    #return 'id' (artist)
def getMusicbrainzAlbumID(sp_album_name, hp_artist_id):
    #only need albumID to queue but want to verify with artistID
    #findAlbum&name=$albumname[&limit=$limit]
    hp_query = 'findAlbum&name=' + sp_album_name + '&limit=25'
    albumQuery = callHeadphones(hp_query)
    #loop through return list
    #match 'id' (artist) and return 'albumid'
def remFromSpotPlaylist():
    print("todo")

def main():
    sp_track_data = getSpotTracks()
    hp_track_data = checkHeadphones(sp_track_data)
    queueAlbum(hp_track_data)

    ### TESTING ###
    print(sp_track_data[0][0]) #[0] artist
    print(sp_track_data[0][1]) #[0] album
    print(sp_track_data[0][2]) #[0] track
    print(sp_track_data[1][0])
    print(sp_track_data[1][1])
    print(sp_track_data[1][2])
    print(sp_track_data[2][0])
    print(sp_track_data[2][1])
    print(sp_track_data[2][2])

main()
