# SpotToPhones

## Goal:
  A program that will connect to Spotify and read tracks in a playlist of your choice.
  The program will then connect to your Headphones server and see if you already have that artist and album.
  If not, will download album and remove track from Spotify playlist.
  If it cannot, it will place the track on a playlist you designate.

## Status: BROKEN
* Broken due to closure of Echonest API [link](https://developer.spotify.com/news-stories/2016/03/29/api-improvements-update/)
* Will have no time to fix before May 31st due to school and work schedule

## Todo:
* add logging
* add method docs
* create documentation/setup tutorial
* handle tracks with error due to musicbrainz timeout rather than not-found
* send bulk request to move tracks in Spotify playlists
* slowest method is adding/queueing in Headphones, needs research.

Open to any suggestions. First real GitHub project for me.
Forgive the sloppy code, still learning.

Thanks for reading!

#### REQUIREMENTS:
* [Requests](http://docs.python-requests.org/en/latest/user/install/)
* [Spotipy](http://spotipy.readthedocs.org/en/latest/#installation)
* [Pyen](https://github.com/plamere/pyen)
* Spotify developer account
* Echonest developer account
* Works best with Headphones VIP Musicbrainz Mirror

#### Setup Instructions
1. clone repo
2. rename **config.ini.example** to **config.ini** and edit
	* SPOTIFY
	  * user
			  * (Spotify username)
		  * scope
			  * (already set, allows SpotToPhones to access your playlists and their data)
		  * client_id
			  * (Spotify client id, provided at Spotify developer portal)
		  * client_secret
			  * (Spotify client secret, provided at Spotify developer portal)
		  * redirect_uri
			  * (Spotify redirect uri, provided at Spotify developer portal)
			    * (can be localhost:8000 or whatever, it does not have to be visited, only pasted into terminal)
		  * wanted_playlist
			  * (name of playlist which contains tracks desired)
		  * error_playlist
			  * (name of playlist where tracks will be moved to on failed attempt to add to Headphones)
		  * success_playlist
			  * (name of playlist where tracks will be moved to on successful attempt to add to Headphones)
	* HEADPHONES
		* ip
		* port
		* webroot
		* api_key
	* ECHONEST
		* api_key
3. Run `python SpotToPhones.py`
4. Report bugs :D
