from bs4 import BeautifulSoup as BS
import requests as rq
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from secrets import your_id, your_secret

print("Initializing...")
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri="http://example.com",
        client_id=your_id,
        client_secret=your_secret,
        show_dialog=True,
        cache_path="token.txt"
    )
)
user_id = sp.current_user()["id"]


date = input("Enter the date for the playlist yyyy-mm-dd:\n")

print(f"Finding top songs for {date}")

response = rq.get(f"https://www.billboard.com/charts/hot-100/{date}")
response.raise_for_status()

soup = BS(response.text, "html.parser")

print("Parsing data...")

song_names = [ele.getText() for ele in soup.find_all(name="span", class_="chart-element__information__song")]
artist_names = [ele.getText() for ele in soup.find_all(name="span", class_="chart-element__information__artist")]

track_raw = [sp.search(q=f'artist: {track[1]} track: {track[0]}', type='track')
             for track in zip(song_names, artist_names)]
print("Data parsed.")
track_ids = []
print("Finding Tracks on Spotify")
for track in track_raw:
    uri = None
    try:
        uri = (track["tracks"]["items"][0]["uri"])
    except IndexError:
        print(f"Track not available")
        continue
    finally:
        if uri not in track_ids and uri is not None:
            track_ids.append(uri)

print("Available tracks Found")


def create_playlist():

    print("Creating playlist")
    playlist_name = f"Nostalgia Playlist for {date}"
    playlist = sp.user_playlist_create(user_id, playlist_name, False)
    print(f'{playlist_name} successfully created')
    return playlist


sp.playlist_add_items(create_playlist()["id"], track_ids)
print("Playlist updated")