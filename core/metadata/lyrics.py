import requests
from urllib.parse import quote
from typing import Optional, Dict, Any

LRCLIB_GET_URL = "https://lrclib.net/api/get"
LRCLIB_SEARCH_URL = "https://lrclib.net/api/search"

HEADERS = {
    "User-Agent": "HarmonixDownloader/1.0 (https://github.com/freyr-apmyx-unified)"
}

class LyricsFetcher:
    @classmethod
    def get_lyrics(cls, track_name: str, artist_name: str, album_name: str = "", duration: int = 0) -> Optional[Dict[str, Any]]:
        # 1. Try exact match with duration
        params = {
            "track_name": track_name,
            "artist_name": artist_name,
        }
        if album_name:
            params["album_name"] = album_name
        if duration > 0:
            params["duration"] = duration

        try:
            resp = requests.get(LRCLIB_GET_URL, params=params, headers=HEADERS, timeout=8)
            if resp.ok:
                data = resp.json()
                return {
                    "synced": data.get("syncedLyrics"),
                    "plain": data.get("plainLyrics"),
                    "instrumental": data.get("instrumental", False)
                }
        except Exception:
            pass

        # 2. Try search if exact match didn't return
        try:
            search_query = f"{artist_name} {track_name}".strip()
            resp = requests.get(LRCLIB_SEARCH_URL, params={"q": search_query}, headers=HEADERS, timeout=8)
            if resp.ok:
                results = resp.json()
                if results and isinstance(results, list):
                    best = results[0]
                    return {
                        "synced": best.get("syncedLyrics"),
                        "plain": best.get("plainLyrics"),
                        "instrumental": best.get("instrumental", False)
                    }
        except Exception as e:
            print(f"[Lyrics] Search failed for {track_name}: {e}")

        return None
