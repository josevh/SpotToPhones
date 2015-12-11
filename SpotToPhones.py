import ConfigParser
from Spotify import Spotify

import pprint #TODO: deleteme

def main():
    spot = Spotify(config)
    #playlists = spot.get_playlists()
    #playlist_id = spot.get_playlist_id(config.get('SPOTIFY', 'wanted_playlist')) #2WgSH6ivNs8bixraYXBf8C
    #tracks = spot.get_playlist_tracks('2WgSH6ivNs8bixraYXBf8C') #3CKCZ9pfwAfoMZlMncA1Nc #adele 21 set-fire-to-the-rain
    
    # [0]['track']['id']
    # [0]['track']['name']
    # [0]['track']['artists'][0]['name']
    # [0]['track']['artists'][0]['id']
    # [0]['track']['album']['id']
    # [0]['track']['album']['name']
    
    #pp.pprint(tracks)
    
            
pp = pprint.PrettyPrinter(indent=4) #TODO: deleteme    
config = ConfigParser.ConfigParser()
config.read("config.ini")

main()
