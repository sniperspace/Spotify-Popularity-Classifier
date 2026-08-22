import time
import base64
import requests


API_BASE = "https://api.spotify.com/v1"
TOKEN_URL = "https://accounts.spotify.com/api/token"

_cached_token = None
_token_expires_at = 0


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


def get_access_token(client_id, client_secret):

    global _cached_token
    global _token_expires_at

    if (
        _cached_token is not None
        and time.time() < _token_expires_at
    ):
        return _cached_token

    credentials = f"{client_id}:{client_secret}"

    encoded_credentials = base64.b64encode(
        credentials.encode("utf-8")
    ).decode("utf-8")

    response = requests.post(
        TOKEN_URL,
        headers={
            "Authorization":
                f"Basic {encoded_credentials}",
            "Content-Type":
                "application/x-www-form-urlencoded"
        },
        data={
            "grant_type": "client_credentials"
        },
        timeout=15
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Spotify authentication failed: "
            f"{response.status_code}"
        )

    data = response.json()

    _cached_token = data["access_token"]

    expires_in = int(
        data.get("expires_in", 3600)
    )

    _token_expires_at = (
        time.time() + expires_in - 60
    )

    return _cached_token


def get_track(
    url,
    client_id,
    client_secret
):

    track_id = extract_track_id(url)

    if not track_id:
        return {
            "status": "error",
            "message": "Invalid Spotify track URL."
        }

    token = get_access_token(
        client_id,
        client_secret
    )

    response = requests.get(
        f"{API_BASE}/tracks/{track_id}",
        headers={
            "Authorization":
                f"Bearer {token}"
        },
        timeout=15
    )

    if response.status_code != 200:
        return {
            "status": "error",
            "message": (
                f"Spotify API returned "
                f"{response.status_code}"
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
        "duration_ms": data.get("duration_ms"),
        "image": (
            images[0]["url"]
            if images
            else None
        )
    }
