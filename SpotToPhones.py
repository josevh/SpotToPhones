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

    for track in tracks['tracks']['items']:
        #pp.pprint(track['track'])
        #artist, album, track
        data = {'Artist': track['track']['artists'][0]['name'],
            'Album': track['track']['album']['name'],
            'Track': track['track']['name']}
        track_data.append(data)

    return track_data

def callHeadphones(cmd):
    hp_user = ConfigSectionMap("HEADPHONES")['user']
    hp_pass = ConfigSectionMap("HEADPHONES")['password']
    hp_ip = ConfigSectionMap("HEADPHONES")['ip']
    # hp_root = ""  #web_root not implemented
    hp_port = ConfigSectionMap("HEADPHONES")['port']
    hp_api_key = ConfigSectionMap("HEADPHONES")['api_key']
    hp_api_url = "http://" + hp_ip + ":" + hp_port + "/api?apikey=" + hp_api_key + "&cmd="
    request = hp_api_url + cmd
    result = requests.get(request)
    result = result.json()
    return result

def checkHeadphones(track_data):
    #search for tracks/albums/artists in Headphones libray
    hp_index = callHeadphones('getIndex')
    for x in range(0,len(track_data)):
        spArtist = track_data[x]['Artist']
        spAlbum = track_data[x]['Album']
        spTrack = track_data[x]['Track']
        if hp_index: # check if Headphones library is empty
            for x in range(0,len(hp_index)):
                print("index loop started\n")
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
                                else:
                                    hp_track_test = "notfound"
                        else:
                            hp_album_id = getMusicbrainzAlbumID(spAlbum, hp_artist_id)
                            hp_track_test = "notfound"
                else:
                    hp_artist_id = getMusicbrainzArtistID(spArtist)
                    hp_album_id = getMusicbrainzAlbumID(hp_artist_id, spAlbum)
                    hp_track_test = "notfound"
            print("does this loop?")
            track_data[x]['Artist ID'] = hp_artist_id
            track_data[x]['Album ID'] = hp_album_id
            track_data[x]['Track Test'] = hp_track_test
        else: #headphones library is empty
            hp_artist_id = getMusicbrainzArtistID(spArtist)
            hp_album_id = getMusicbrainzAlbumID(hp_artist_id, spAlbum)
            hp_track_test = "notfound"
            track_data[x]['Artist ID'] = hp_artist_id
            track_data[x]['Album ID'] = hp_album_id
            track_data[x]['Track Test'] = hp_track_test
    return track_data

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
    #find a way to incorporate track_data here, add 'ArtistID'. or a func to do it
    hp_artist_id = ''
    hp_query = 'findArtist&name=' + sp_artist_name + '&limit=3'
    count = 0
    while True: #retry connection if failed, until successful or 5 tries
        count += 1
        artistQuery = callHeadphones(hp_query)
        if (isinstance(artistQuery, list)):
            break
        if (count > 5):
            hp_artist_id = "notfound"
            break
    if (hp_artist_id != "notfound"):
        for artist in artistQuery:
            if artist['score'] == 100: #cannot reliably verify artist name matches
                hp_artist_id = artist['id']
                break
            else:
                hp_artist_id = "notfound"
                break
    return hp_artist_id

def getMusicbrainzAlbumID(hp_artist_id, sp_album_name):
    #find a way to incorporate track_data dict here  or a func to do it
    hp_album_id = ''
    hp_query = 'findAlbum&name=' + sp_album_name + '&limit=3'
    count = 0
    while True: #retry connection if failed, until successful or 5 tries
        count += 1
        albumQuery = callHeadphones(hp_query)
        if (isinstance(albumQuery, list)):
            break
        if (count > 5):
            hp_album_id = "notfound"
            break
    if (hp_album_id != "notfound"):
        for album in albumQuery:
           if album['uniquename'] == sp_album_name and album['id'] == hp_artist_id:
               hp_album_id = album['albumid']
               break
           else:
               hp_album_id = "notfound"
               break
    return hp_album_id
def remFromSpotPlaylist():
    print("todo")

def main():
    sp_track_data = getSpotTracks()
    hp_track_data = checkHeadphones(sp_track_data)
    queueAlbum(hp_track_data)
#    queueAlbum(hp_track_data)

    ### TESTING ###
    #pp.pprint(hp_track_data)
    print(sp_track_data[0]['Artist']) #[0] artist
    print(hp_track_data[0]['Artist ID'])
    print(sp_track_data[0]['Album']) #[0] album
    print(hp_track_data[0]['Album ID'])
    print(sp_track_data[0]['Track']) #[0] track
    print(hp_track_data[0]['Track Test'])


main()
