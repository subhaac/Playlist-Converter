from secrets import spotify_user_id, spotify_user_secret
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pytube
import youtube_dl


class Create_Playlist:
    list_of_songs = []

    def __init__(self, url):
        self.user_id = spotify_user_id
        self.youtube_playlist = pytube.Playlist(url)
        self.spotify_client = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=spotify_user_id,
                client_secret=spotify_user_secret,
                redirect_uri="https://localhost/callback/",
                scope="user-library-read playlist-modify-public playlist-modify-private",
            )
        )
        self.song_dict = {}
        self.spotify_uri_list = []
        self.spotify_playlist_id = None

    def create_new_spotify_playlist(self, playlist_name, playlist_description):
        created_playlist = self.spotify_client.user_playlist_create(
            "subhaac",
            playlist_name,
            public=True,
            collaborative=False,
            description=playlist_description,
        )
        self.spotify_playlist_id = created_playlist["id"]

    def get_youtube_songs(self):
        for song in self.youtube_playlist.video_urls:
            try:
                self.list_of_songs.append(song)
            except Exception:
                pass
        return self.list_of_songs

    def get_youtube_artist_and_track(self):
        for songs in self.list_of_songs:
            download = False
            ydl_opts = {
                "outtmpl": "fileName",
                "writethumbnail": True,
            }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ie_result = ydl.extract_info(songs, download)

            try:
                self.song_dict[ie_result["track"]] = ie_result["artist"]
            except Exception as e:
                print("Exception: ", e)
                continue
        return self.song_dict

    def find_spotify_song_url(self):
        for song in self.song_dict:
            results = self.spotify_client.search(
                q=str(song + " " + self.song_dict[song]), limit=1
            )
            for idx, track in enumerate(results["tracks"]["items"]):
                self.spotify_uri_list.append(results["tracks"]["items"][0]["uri"])
        return self.spotify_uri_list

    def add_songs_to_spotify_playlist(self):
        self.spotify_client.user_playlist_add_tracks(
            user=self.user_id,
            playlist_id=self.spotify_playlist_id,
            tracks=self.spotify_uri_list,
        )