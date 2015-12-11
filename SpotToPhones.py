import ConfigParser
from Spotify import Spotify

import pprint #TODO: deleteme

def main():
    spot = Spotify(config)
    pls = spot.get_playlists(config.get('SPOTIPY', 'user'))
    pp.pprint(pls)
            
pp = pprint.PrettyPrinter(indent=4) #TODO: deleteme    
config = ConfigParser.ConfigParser()
config.read("config.ini")

main()
