# SpotToPhones

<b>Goal:</b>
<br>
  A program that will connect to Spotify and read tracks in a playlist of your choice.
  The program will then connect to your Headphones server and see if you already have that artist and album.
  If not, will download album and remove track from Spotify playlist.
  
  If it cannot, it will place the track on a playlist you designate.
<br><br>
<b>Status:</b> WIP:<b>NOT WORKING</b>
<ul>
  <li>Method to queue track is not working, WIP.</li>
  <li>In process of rewriting.</li>
</ul>  
<br>
<b>Todo:</b>
<ul>
    <li>Fix queue_album_in_hp class method</li>
    <li>Move tracks that cannot be found on MBz to another playlist for cases in which manual download will be required.</li>
</ul>
<br>
Open to any suggestions. First real GitHub project for me.
Forgive the sloppy code, still learning.

Thanks for reading!

<b>REQUIREMENTS:</b>
<ol>
  <li><a href="http://docs.python-requests.org/en/latest/user/install/">Requests</a></li>
  <li><a href="http://spotipy.readthedocs.org/en/latest/#installation">Spotipy</a></li>
  <li><a href="https://github.com/plamere/pyen">Pyen</a></li>
</ol>
