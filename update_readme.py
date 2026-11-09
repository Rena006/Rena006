"""Update the Last.fm section of README.md.

Only the content between the LASTFM:START / LASTFM:END markers is replaced,
so the rest of the README can be edited freely by hand.
"""

from __future__ import annotations

import json
import os
import re
import sys
from html import escape
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ENDPOINT = "https://ws.audioscrobbler.com/2.0/"
LIMIT = 5
README = Path(__file__).parent / "README.md"

START = "<!-- LASTFM:START -->"
END = "<!-- LASTFM:END -->"
SECTION_RE = re.compile(rf"{re.escape(START)}.*?{re.escape(END)}", re.DOTALL)


def lastfm(method: str, user: str, api_key: str) -> dict:
    query = urlencode(
        {
            "method": method,
            "user": user,
            "api_key": api_key,
            "format": "json",
            "limit": LIMIT,
        }
    )
    request = Request(f"{ENDPOINT}?{query}", headers={"User-Agent": "readme-lastfm-updater"})
    with urlopen(request, timeout=15) as response:
        data = json.load(response)
    if "error" in data:
        raise RuntimeError(f"Last.fm error {data['error']}: {data.get('message')}")
    return data


def md_link_text(text: str) -> str:
    """Escape characters that would break Markdown link text."""
    return re.sub(r"([\\\[\]*_])", r"\\\1", text)


def render_scrobbles(data: dict) -> str:
    tracks = data.get("recenttracks", {}).get("track", [])[:LIMIT]
    if not tracks:
        return "No scrobbles available.\n"

    lines = []
    for track in tracks:
        artist = md_link_text(track["artist"]["#text"])
        song = md_link_text(track["name"])
        url = track["url"]
        if track.get("@attr", {}).get("nowplaying") == "true":
            lines.append(f"- **🎵 {artist}** - *[{song}]({url})* (Now Playing)")
        else:
            lines.append(f"- **{artist}** - *[{song}]({url})*")
    return "\n".join(lines) + "\n"


def render_albums(data: dict) -> str:
    albums = data.get("topalbums", {}).get("album", [])
    covers = []
    for album in albums:
        images = album.get("image") or []
        image_url = images[-1].get("#text") if images else ""
        if not image_url:
            continue
        name = escape(album["name"])
        artist = escape(album["artist"]["name"])
        covers.append(
            f'<a href="{escape(album["url"])}">'
            f'<img src="{escape(image_url)}" alt="{name}" title="{artist} - {name}" width="100">'
            f"</a>"
        )
    return "".join(covers) + "\n" if covers else "No top albums available.\n"


def build_section(user: str, api_key: str) -> str:
    scrobbles = render_scrobbles(lastfm("user.getrecenttracks", user, api_key))
    albums = render_albums(lastfm("user.gettopalbums", user, api_key))
    return (
        f"{START}\n"
        "# 🎶 Last.fm Scrobbles\n\n"
        f"{scrobbles}\n"
        "# 📀 Top Albums\n\n"
        f"{albums}"
        f"{END}"
    )


def main() -> int:
    api_key = os.environ.get("LASTFM_API_KEY")
    user = os.environ.get("LASTFM_USER")
    if not api_key or not user:
        print("LASTFM_API_KEY and LASTFM_USER must be set", file=sys.stderr)
        return 1

    readme = README.read_text(encoding="utf-8")
    if not SECTION_RE.search(readme):
        print(f"Markers {START} / {END} not found in {README.name}", file=sys.stderr)
        return 1

    try:
        section = build_section(user, api_key)
    except (URLError, RuntimeError, KeyError, ValueError) as exc:
        # Leave the README untouched rather than wiping it on API failure.
        print(f"Could not fetch Last.fm data: {exc}", file=sys.stderr)
        return 1

    updated = SECTION_RE.sub(lambda _: section, readme, count=1)
    if updated != readme:
        README.write_text(updated, encoding="utf-8")
        print("README.md updated")
    else:
        print("README.md already up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main())
