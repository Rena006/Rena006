import os
import requests

API_KEY = os.getenv("LASTFM_API_KEY")  
USERNAME = "shadow-420"  
ENDPOINT = "http://ws.audioscrobbler.com/2.0/"

def get_recent_scrobbles():
    params = {
        "method": "user.getrecenttracks",
        "user": USERNAME,
        "api_key": API_KEY,
        "format": "json",
        "limit": 5
    }
    response = requests.get(ENDPOINT, params=params)
    data = response.json()

    # Construir el contenido del README con los scrobbles reales
    scrobbles_text = "# 👋 Hi\n\n"
    scrobbles_text += "Rena Here\nSoftware Engineer | AI and Quantum Computing Enthusiast | Currently working at IBM and one of the founding members of Proto AI 🤖💪\n\n"
    scrobbles_text += "# 🎶 Last.fm Scrobbles\n\n"
    if "recenttracks" in data and "track" in data["recenttracks"]:
        scrobbles = data["recenttracks"]["track"]
        for track in scrobbles:
            artist = track["artist"]["#text"]
            song = track["name"]
            url = track["url"]
            now_playing = track.get("@attr", {}).get("nowplaying", False)
            if now_playing:
                scrobbles_text += f"- **🎵 {artist}** - *[{song}]({url})* (Now Playing)\n"
            else:
                scrobbles_text += f"- **{artist}** - *[{song}]({url})*\n"
    else:
        scrobbles_text += "No scrobbles available."

    with open("README.md", "w") as file:
        file.write(scrobbles_text)

get_recent_scrobbles()
