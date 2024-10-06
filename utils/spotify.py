import spotipy
import spotipy.util as util
from utils.config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET
from spotipy.oauth2 import SpotifyClientCredentials
import requests
import os


class Spotify:
    def __init__(self):
        username = "c12325"
        scope = "user-read-currently-playing"
        redirect_uri = "http://google.com/"
        cache_path = os.path.expanduser("~\\Documents\\spotify_token_cache")
        # Get the token
        token = util.prompt_for_user_token(username, scope, SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, redirect_uri, cache_path)
        self.sp = spotipy.Spotify(auth=token)
        self.last_song_id = None  # Track the last song's ID

    def getinfo(self):

        # Get the currently playing song
        currentsong = self.sp.currently_playing()
        
        # Check if there is a song playing
        if not currentsong or not currentsong['is_playing']:
            print("No song is currently playing.")
            return None
        
        song_name = currentsong['item']['name']
        song_artist = currentsong['item']['artists'][0]['name']
        song_id = currentsong['item']['id']  # Track the song by its unique ID

        # Check if it's a new song
        if self.last_song_id == song_id:
            # Same song still playing, no need to refresh info
            return None
        
        self.last_song_id = song_id  # Update the last song ID

        # Extract the album image URL
        album_image_url = currentsong['item']['album']['images'][0]['url']  # Get the largest image (0 index)

        # Download the album image
        image_response = requests.get(album_image_url)
        print(image_response.status_code)

        # Define the full path where the image will be saved
        save_path = r'C:\\Users\\Clarence\\Documents\\GitHub\\LED-controller\\assets\\album.png'

        # Ensure the directory exists
        directory = os.path.dirname(save_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Save the image if the response is valid
        if image_response.status_code == 200:
            with open(save_path, "wb") as file:
                file.write(image_response.content)
            print(f"Album image downloaded to '{save_path}'")
        else:
            print(f"Failed to download image. Status code: {image_response.status_code}")

        print(f"Now playing {song_name} by {song_artist}")

        return [song_name, song_artist, save_path]
    

    '''
    
    def track_changes(self, interval=10):
        """Continuously check for song changes and run getinfo when a new song plays"""
        while True:
            self.getinfo()
            time.sleep(interval)  # Check every `interval` seconds
    '''


# Usage:
#spotify = Spotify()
#spotify.track_changes(interval=10)  # Checks every 10 seconds for song changes


