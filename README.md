# SpotToPhones

## Goal:
  A program that will connect to Spotify and read tracks in a playlist of your choice.
  The program will then connect to your Headphones server and see if you already have that artist and album.
  If not, will download album and remove track from Spotify playlist.
  If it cannot, it will place the track on a playlist you designate.
  
## Status: **WIP**: PARTIALLY WORKING
* Method to queue track is not 100% reliable, WIP.
* In process of rewriting.
* Works best with Headphones VIP Musicbrainz Mirror

## Todo:
* add logging
* create documentation/setup tutorial

Open to any suggestions. First real GitHub project for me.
Forgive the sloppy code, still learning.

Thanks for reading!

#### REQUIREMENTS:
* [Requests](http://docs.python-requests.org/en/latest/user/install/)
* [Spotipy](http://spotipy.readthedocs.org/en/latest/#installation)
* [Pyen](https://github.com/plamere/pyen)
* Spotify developer account
* Echonest developer account

#### Setup Instructions
1. clone repo
2. edit **config.ini**
	* GENERAL
		* wanted_playlist
			* (name of playlist which contains tracks desired)
		* error_playlist
			* (name of playlist where tracks will be moved to on failed attempt to add to Headphones)
		* snatched_playlist
			* (name of playlist where tracks will be moved to on successful attempt to add to Headphones)
	* SPOTIPY
		* scope
			* (already set, allows SpotToPhones to access your playlists and their data)
		* user
			* (Spotify username)
		* spotify_client_id
			* (Spotify client id, provided at Spotify developer portal)
		* spotify_client_secret
			* (Spotify client secret, provided at Spotify developer portal)
		* spotify_redirect_uri
			* (Spotify redirect uri, provided at Spotify developer portal)
	* HEADPHONES
		* ip
		* port
		* webroot
		* api_key
	* ECHONEST
		* api_key
3. Run `python SpotToPhones.py`
4. Report bugs :D
