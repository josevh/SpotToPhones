class Track(object):
    def __init__(self, name, id, artist_name, artist_id_sp, album_name, album_id_sp, album_type):
        self.name           = name
        self.id             = id
        
        self.artist_name    = artist_name
        self.artist_id_sp   = artist_id_sp
        self.artist_id_mb   = ""
        self.artist_in_hp   = None
        
        self.album_name     = album_name
        self.album_id_sp    = album_id_sp
        self.album_id_mb    = ""
        self.album_type     = album_type
        self.album_in_hp    = None
        
        self.add_result     = None
        
    def valid_mb_ids(self):
        return self.artist_id_mb is not None and self.album_id_mb is not None
    def _print(self):
        print "track name: " + self.name
        print "track artist name: " + self.artist_name
        if self.artist_id_mb is not None:
            print "track artist mb id: " + self.artist_id_mb
        print "track album name: " + self.album_name
        if self.album_id_mb is not None:
            print "track album mb id: " + self.album_id_mb
        if self.artist_in_hp:
            print "artist in hp: yes"
        else:
            print "artist in hp: no"
        if self.album_in_hp:
            print "album in hp: yes"
        else:
            print "album in hp: no"
        if self.add_result:
            print "track add result: ok"
        else:
            print "track add result: not ok"