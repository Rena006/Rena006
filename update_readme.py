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

    scrobbles_text = "# 🎶 Last.fm Scrobbles\n\n"
    if "recenttracks" in data and "track" in data["recenttracks"]:
        tracks = data["recenttracks"]["track"]
        for track in tracks:
            artist = track["artist"]["#text"]
            song = track["name"]
            url = track["url"]
            now_playing = track.get("@attr", {}).get("nowplaying", False)
            if now_playing:
                scrobbles_text += f"- **🎵 {artist}** - *[{song}]({url})* (Now Playing)\n"
            else:
                scrobbles_text += f"- **{artist}** - *[{song}]({url})*\n"
    else:
        scrobbles_text += "No scrobbles available.\n"

    return scrobbles_text

def get_top_albums():
    params = {
        "method": "user.gettopalbums",
        "user": USERNAME,
        "api_key": API_KEY,
        "format": "json",
        "limit": 5
    }
    response = requests.get(ENDPOINT, params=params)
    data = response.json()

    albums_text = "# 📀 Top Albums\n\n"
    if "topalbums" in data and "album" in data["topalbums"]:
        albums = data["topalbums"]["album"]
        for album in albums:
            artist = album["artist"]["name"]
            album_name = album["name"]
            playcount = album["playcount"]
            url = album["url"]
            albums_text += f"- **{artist}** - *[{album_name}]({url})* (Playcount: {playcount})\n"
    else:
        albums_text += "No top albums available.\n"

    return albums_text

def update_readme():
    readme_content = "# 👋 Hi\n\n"
    readme_content += "Rena Here\nSoftware Engineer | AI and Quantum Computing Enthusiast | Currently working at IBM and one of the founding members of Proto AI 🤖💪\n\n"
    readme_content += get_recent_scrobbles()
    readme_content += "\n"
    readme_content += get_top_albums()

    with open("README.md", "w", encoding="utf-8") as file:
        file.write(readme_content)

update_readme()
