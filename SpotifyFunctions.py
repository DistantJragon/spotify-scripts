import json
import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

from .Track import Track

SCRIPT_DATA = Path("./script-data").resolve()
SPOTIFY_ACCESS_TOKEN_DATA = SCRIPT_DATA / "Spotify-Access-Token.json"

SCRIPT_DATA.mkdir(exist_ok=True)


def refresh_access_token() -> str | None:
    load_dotenv()
    spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
    spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    if not spotify_client_id or not spotify_client_secret:
        print("SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET are not set.")
        return None
    url = "https://accounts.spotify.com/api/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": spotify_client_id,
        "client_secret": spotify_client_secret,
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        response_data = response.json()
        response_data["expires_at"] = response_data["expires_in"] + \
            int(time.time())
        with open(SPOTIFY_ACCESS_TOKEN_DATA, "w") as outfile:
            json.dump(response_data, outfile)
        print("Access token refreshed successfully.")
        return response_data["access_token"]
    else:
        print("Error refreshing access token: " + str(response.status_code))
        return None


def get_access_token() -> str | None:
    spotify_access_token = {}

    if not os.path.exists(SPOTIFY_ACCESS_TOKEN_DATA):
        print("Spotify-Access-Token.json file does not exist. Getting an access token.")
        return refresh_access_token()
    else:
        # Read the Spotify-Access-Token.json file
        with open(SPOTIFY_ACCESS_TOKEN_DATA, "r") as file:
            spotify_access_token = json.load(file)

        # Check if the access token is expired
        if spotify_access_token["expires_at"] < time.time():
            print(
                "Spotify-Access-Token.json file has expired"
                + "\nAttempting to refresh the access token."
            )
            return refresh_access_token()

        return spotify_access_token["access_token"]


# Function to get tracks from a playlist
def get_playlist_tracks(access_token: str, playlist_id: str) -> dict[str, Track] | None:
    if "spotify:playlist:" in playlist_id:
        playlist_id = playlist_id.split(":")[2]
    next_page_url = "https://api.spotify.com/v1/playlists/{}/tracks?fields={}".format(
        playlist_id, "next,items(is_local,track(artists.name,name,id))"
    )

    track_list: dict[str, Track] = {}

    while next_page_url:
        request = requests.get(
            next_page_url,
            headers={"Authorization": "Bearer {}".format(access_token)},
        )

        if request.status_code != 200:
            print("The request returned an error")
            print(request.text)
            print(request.status_code)
            return None
        request_items = request.json()
        next_page_url = request_items["next"]
        for i, item in enumerate(request_items["items"], start=1):
            track_list[item["track"]["id"]] = Track(
                item["track"]["name"],
                item["track"]["artists"][0]["name"],
                i,
                item["track"]["id"],
            )

    return track_list
