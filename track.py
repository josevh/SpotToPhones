class Track(object):
    """Tracks have the following attributes:
    
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
    """

    def __init__(self, name, album, artist, uri, sp_uri, sp_id, sp_album_id, sp_artist_id):
        self.name               = name
        self.album              = album
        self.artist             = artist
        
        self.sp_uri             = sp_uri
        self.sp_id              = sp_id
        self.sp_album_id        = sp_album_id
        self.sp_artist_id       = sp_artist_id
        
        self.mb_id              = None
        self.mb_album_id        = None
        self.mb_artist_id       = None
        
        self.have_track         = None
        self.have_album         = None
        
        self.dl_request_status  = None