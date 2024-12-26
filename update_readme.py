import os
import requests

API_KEY = os.getenv('LASTFM_API_KEY')
USERNAME = 'shadow-420'
ENDPOINT = 'http://ws.audioscrobbler.com/2.0/'

def get_recent_scrobbles():
    params = {
        'method': 'user.getrecenttracks',
        'user': USERNAME,
        'api_key': API_KEY,
        'format': 'json',
        'limit': 5
    }
    response = requests.get(ENDPOINT, params=params)
    data = response.json()
    scrobbles_text = "# 🎶 Last.fm Scrobbles\n\n"
    if 'recenttracks' in data:
        scrobbles = data['recenttracks']['track']
        for track in scrobbles:
            scrobbles_text += f"- **{track['artist']['#text']}** - *{track['name']}*\n"
    else:
        scrobbles_text += "No scrobbles available."
    with open("README.md", "w") as file:
        file.write(scrobbles_text)

get_recent_scrobbles()
