import pyen

class Track(object):
    '''Tracks have the following attributes:
    
        name:               A string representing the track's name.
        album:              A string representing the track's album.
        artist:             A string representing the track's artist.
        
        sp_uri:             A string representing the track's Spotify URI.
        sp_id:              A string representing the track's Spotify ID.
        sp_album_id:        A string representing the track's album's Spotify ID.
        sp_artist_id:       A string representing the track's artist's Spotify ID.
        
        mb_id:              A string representing the track's Musicbrainz ID.
        mb_album_id:        A string representing the track's Album's Musicbrainz ID.
        mb_artist_id:       A string representing the track's Artist's Musicbrainz ID.
        
        have_track:         A boolean representing whether the track is in Headphones library.
        have_album:         A boolean representing whether the track's album is in Headphones library.
        
        dl_request_status:  A string representing the outcome of adding album to Headphones queue.
    '''

    def __init__(self, data, config):
        self.name               = data['name']
        self.album              = data['album']
        self.artist             = data['artist']
        
        self.sp_uri             = data['sp_uri']
        self.sp_id              = data['sp_id']
        self.sp_album_id        = data['sp_album_id']
        self.sp_artist_id       = data['sp_artist_id']
        
        self.config             = config
        
        self.mb_artist_id       = self._get_mb_artist_id(self.sp_artist_id)
        self.mb_id              = None
        self.mb_album_id        = None
        
        self.have_track         = None
        self.have_album         = None
        
        self.dl_request_status  = None
        
    def _get_mb_artist_id(self, sp_artist_id):
        ''' Use EchoNest API to map Spotify artist id to Musicbrainz artist id
        '''
        config = self.config
        en = pyen.Pyen(config.get('ECHONEST', 'api_key'))
        params = {
            'id':       'spotify:artist:' + sp_artist_id,
            'bucket':   ['id:musicbrainz'],
        }
        response = en.get('artist/profile', **params)
        if (response['status']['message'] == 'Success'):
            mbid = response['artist']['foreign_ids'][0]['foreign_id']
            return mbid[19:]    #remove 'musicbrainz:artist:'
        else:
            return 'notfound'

