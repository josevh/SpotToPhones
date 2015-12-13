import ConfigParser
from Spotify import Spotify

def main():
    config = ConfigParser.ConfigParser()
    config.read("config.ini")
    spot = Spotify(config)

if __name__ == "__main__": main()