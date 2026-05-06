import shutil

import pandas as pd
import requests

from .SpotifyFunctions import get_access_token, get_playlist_tracks
from .Track import Track

# Get access token and playlist data
access_token = get_access_token()
if access_token is None:
    print("Access token is not valid")
    exit()

# Get tracks from the first playlist
playlist1_uri = input("First Playlist URI: ")
playlist1_tracks = get_playlist_tracks(access_token, playlist1_uri)
if playlist1_tracks is None:
    print("Playlist 1 tracks are not valid")
    exit()

# Get tracks from the second playlist
playlist2_uri = input("Second Playlist URI: ")
playlist2_tracks = get_playlist_tracks(access_token, playlist2_uri)
if playlist2_tracks is None:
    print("Playlist 2 tracks are not valid")
    exit()

# Find common tracks in both playlists
common_tracks = {
    track_id: track
    for track_id, track in playlist1_tracks.items()
    if track_id in playlist2_tracks
}

for track_id, track in common_tracks.items():
    print(track.track_name, "by", track.artist_name)

# How big is the terminal window?
terminal_line_length, terminal_height = shutil.get_terminal_size()

# Print the common tracks in both playlists, with the track name and artist name,
# in a sort of grid pattern to the terminal, with the artist name below the track name

# Get the max of track and artist name lengths for each track
track_max_lengths = {
    track_id: max(len(track.track_name), len(track.artist_name))
    for track_id, track in common_tracks.items()
}

# Sorted list of track ids by track name length
track_ids = sorted(
    track_max_lengths, key=lambda track_id: track_max_lengths[track_id], reverse=True
)

print(track_ids)
