import sys

from decouple import config
from tswift import Artist, Song
import requests as r


class Scraper(object):
    """Utility class for scraping artist information and song lyrics."""
    def __init__(self):
        self.API_KEY = config('LASTFM_API_KEY', cast=str)
        
    def set_artist(self, name: str) -> Artist:
        """Given an artist's name, return an Artist object."""
        try:
            artist = Artist(name)
            if len(artist.songs) == 0:
                raise ValueError('No songs for this artist.')
        except Exception as e:
            print(f'Exception occured: {e}')
        else:
            print(f'Your artist has been chosen: {artist}')
            return artist
        
    def get_all_songs(self, artist: Artist) -> list:
        """Given an Artist object, return a List of Song objects."""
        return [song for song in artist.songs]
    
    def get_song_lyrics(self, song: Song) -> str:
        """Given a Song object, return it's lyrics."""
        return song.lyrics
    
    def get_all_lyrics(self, artist: Artist) -> list:
        """Given an Artist object, return a list of all song lyrics."""
        return [song.lyrics for song in artist.songs]
    
    def get_artist_info(self, artist: Artist) -> dict:
        """Given an artist object, query LastFM for artist metadata.
           Return a dictionary of similar artists, artist's top tags,
           and other artists sharing the top 3 tags."""
        artist_name = str(artist.name).replace('-', '')
        artist_info = {}
        
        # Get similar artists
        response = r.get(f'http://ws.audioscrobbler.com/2.0/?method=artist.getsimilar&artist={artist_name}&api_key={self.API_KEY}&format=json')
        if response.status_code != 200:
            raise IOError(f'IOError: {r.status_codes._codes[response.status_code]}')
        resp_json = response.json()['similarartists']['artist']
        artist_info['similar_artists'] = [similar_artist['name'] for similar_artist in resp_json]
        
        # Get top tags
        response = r.get(f'http://ws.audioscrobbler.com/2.0/?method=artist.getTopTags&artist={artist_name}&api_key={self.API_KEY}&format=json')
        resp_json = response.json()['toptags']['tag']
        artist_info['top_tags'] = [tag['name'] for tag in resp_json]
        
        # Get tags top artists
        tag_top_artists = []
        for tag in artist_info['top_tags'][:3]:
            response = r.get(f'http://ws.audioscrobbler.com/2.0/?method=tag.gettopartists&tag={tag}&api_key={self.API_KEY}&format=json')
            resp_json = response.json()['topartists']['artist']
            tag_top_artists.extend([artist['name'] for artist in resp_json])
        artist_info['tag_top_artists'] = tag_top_artists
            
        return artist_info
        
if __name__ == "__main__":
    sys.exit('Please import as a module to use this class.')
