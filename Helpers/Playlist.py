class Playlist(object):
    def __init__(self, name):
        self.name   = name
        self.id     = ""
        self.tracks = []
    def _print(self):
        print "playlist name: " + self.name
        print "playlist id: " + self.id