"""
Deprecated
"""
import getpass
import json
import sys
import time
from pathlib import Path

import requests

spotify_client_id = ""
spotify_client_secret = ""

# Need two arguments, client_id and client_secret
if len(sys.argv) != 3:
    spotify_client_id = getpass.getpass("Spotify Client ID: ")
    spotify_client_secret = getpass.getpass("Spotify Client Secret: ")
else:
    spotify_client_id = sys.argv[1]
    spotify_client_secret = sys.argv[2]

SCRIPT_DATA = Path("./script-data")
SPOTIFY_ACCESS_TOKEN_DATA = SCRIPT_DATA / "Spotify-Access-Token.json"

url = "https://accounts.spotify.com/api/token"
headers = {"Content-Type": "application/x-www-form-urlencoded"}
data = {
    "grant_type": "client_credentials",
    "client_id": spotify_client_id,
    "client_secret": spotify_client_secret,
}

response = requests.post(url, headers=headers, data=data)

# The response variable now contains the data returned by the API
# Check the status code to see if the request was successful
if response.status_code == 200:
    # Response has an expiry time of 3600 seconds. Save the response data to a file, adding a "expires_at" key with the current time + 3600 seconds"
    response_data = response.json()
    response_data["expires_at"] = response_data["expires_in"] + \
        int(time.time())
    # Save the response data to a file
    with open(SPOTIFY_ACCESS_TOKEN_DATA, "w") as outfile:
        json.dump(response_data, outfile)
    print("Success: " + str(response.status_code))
else:
    print("Error: " + str(response.status_code))
    sys.exit(1)
