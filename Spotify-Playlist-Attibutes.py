import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import requests
from plotly.subplots import make_subplots

from .FeatureValues import AUDIO_FEATURES
from .SpotifyFunctions import get_access_token, get_playlist_tracks
from .Track import Track

SCRIPT_DATA = Path("./script-data")
SPOTIFY_ACCESS_TOKEN_DATA = SCRIPT_DATA / "Spotify-Access-Token.json"
SPOTIFY_PLAYLIST_ATTRIBUTES_DATA = SCRIPT_DATA / \
    "Spotify-Playlist-Attributes.json"


def truncate_string(input_str: str, max_length: int):
    if len(input_str) > max_length:
        return input_str[: max_length - 3] + "..."
    else:
        return input_str


# Check if the Spotify-Access-Token.json file exists
SCRIPT_DATA.mkdir(exist_ok=True)

# Get the access token
access_token = get_access_token()
if access_token is None:
    print("Error: Could not get access token")
    exit(1)

playlist_uri = input("Playlist URI: ")
playlist_id = playlist_uri.split(":")[2]

# Track list of the playlist, in the format of {track_id: Track}
track_list = get_playlist_tracks(access_token, playlist_id)
if track_list is None:
    print("Error: Could not get playlist tracks")
    exit(1)

# Get the track ids
id_list = list(track_list.keys())

# Get the audio features for the tracks
# Spotify only allows 100 tracks per request, so we need to request in batches
id_list_100s: list[list[str]] = []
for i in range(0, len(id_list), 100):
    id_list_100s.append(id_list[i: i + 100])

id_100_strings: list[str] = []
for id_list_100 in id_list_100s:
    id_100_strings.append(",".join(id_list_100))

# Get the audio features for the tracks
for id_string in id_100_strings:
    request = requests.get(
        "https://api.spotify.com/v1/audio-features?ids={}".format(id_string),
        headers={"Authorization": "Bearer {}".format(access_token)},
    )
    if request.status_code != 200:
        print("The request returned an error")
        print(request.text)
        print(request.status_code)
        exit(1)
    request_items = request.json()
    for item in request_items["audio_features"]:
        track_id = item["uri"].split(":")[2]
        track_list[track_id].set_audio_features(item)

# Write the track list to a file to debug
with open(SPOTIFY_PLAYLIST_ATTRIBUTES_DATA, "w") as f:
    track_dict_list = [track.to_dict() for track in track_list.values()]
    json.dump(track_dict_list, f, indent=4)

# Plot the data
playlist_data = {
    "Song Name": [],
    "Truncated Song Name": [],
    "Artist": [],
}

for feature in AUDIO_FEATURES.values():
    playlist_data[feature] = []

for track in track_list.values():
    playlist_data["Song Name"].append(track.track_name)
    playlist_data["Truncated Song Name"].append(
        truncate_string(track.track_name, 20))
    playlist_data["Artist"].append(track.artist_name)
    for feature_index, feature in AUDIO_FEATURES.items():
        playlist_data[feature].append(track.audio_features[feature])

df = pd.DataFrame(playlist_data)

fig = go.Figure()
dropdown_buttons = []

dropdown_buttons.append(
    dict(
        label="All",
        method="update",
        args=[{"visible": [True for _ in range(len(df))]}, {"title": "All"}],
    )
)

for feature in AUDIO_FEATURES.values():
    fig.add_trace(go.Scatter(
        x=df["Truncated Song Name"], y=df[feature], name=feature))
    dropdown_buttons.append(
        dict(
            label=feature,
            method="update",
            args=[
                {
                    "visible": [
                        feature == visible_feature
                        for visible_feature in AUDIO_FEATURES.values()
                    ]
                }
            ],
        )
    )

fig.update_layout(
    updatemenus=[
        dict(
            active=0,
            buttons=dropdown_buttons,
        )
    ]
)

# Show the figure
fig.show()
