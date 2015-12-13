import ConfigParser
from Helpers import Spotify
from Helpers import Headphones
from Helpers import Playlist

def main():
    config = ConfigParser.ConfigParser()
    config.read("config.ini")
    sp = Spotify(config)
    
    hp_worker = Headphones(
            config.get('HEADPHONES', 'ip'),
            config.get('HEADPHONES', 'port'),
            config.get('HEADPHONES', 'webroot'),
            config.get('HEADPHONES', 'api_key'),
            config.get('ECHONEST', 'api_key')
        )
    
    sp.get_playlist_ids(sp.working_playlists)
    
    if sp.get_playlist_tracks(sp.working_playlists):
        sp.get_playlist_mb_ids(hp_worker, sp.working_playlists)
        sp.add_tracks_hp(hp_worker, sp.playlist_wanted)
        sp.playlist_move_tracks(sp.playlist_wanted)
        
        #TODO: deleteme        
        # for playlist in sp.working_playlists:
        #     playlist._print()
        #     print ""
        #     for track in playlist.tracks:
        #         #if track.valid_mb_ids():
        #         track._print()
        #         print ""
        #     print ""

if __name__ == "__main__": main()
        