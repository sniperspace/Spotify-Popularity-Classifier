
import os
import requests


API_BASE = "https://api.spotify.com/v1"


def extract_track_id(url):
    if not url:
        return None

    url = url.strip()

    if "track/" not in url:
        return None

    return (
        url.split("track/")[1]
        .split("?")[0]
        .strip()
    )


def get_track(url, access_token):
    track_id = extract_track_id(url)

    if not track_id:
        return {
            "status": "error",
            "message": "Invalid Spotify track URL."
        }

    response = requests.get(
        f"{API_BASE}/tracks/{track_id}",
        headers={
            "Authorization":
                f"Bearer {access_token}"
        },
        timeout=15
    )

    if response.status_code != 200:
        return {
            "status": "error",
            "message": (
                f"Spotify API returned "
                f"{response.status_code}."
            )
        }

    data = response.json()

    images = (
        data.get("album", {})
        .get("images", [])
    )

    return {
        "status": "success",
        "track_id": data.get("id"),
        "name": data.get("name"),
        "artists": [
            artist.get("name")
            for artist in data.get(
                "artists", []
            )
        ],
        "album": (
            data.get("album", {})
            .get("name")
        ),
        "release_date": (
            data.get("album", {})
            .get("release_date")
        ),
        "duration_ms": data.get(
            "duration_ms"
        ),
        "image": (
            images[0]["url"]
            if images
            else None
        )
    }
