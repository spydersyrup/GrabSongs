import requests
from typing import List, Dict, Any, Optional

ITUNES_LOOKUP_URL = "https://itunes.apple.com/lookup"
ITUNES_SEARCH_URL = "https://itunes.apple.com/search"

def get_highres_artwork(url: str, size: int = 1400) -> str:
    if not url:
        return ""
    return url.replace("100x100bb", f"{size}x{size}bb").replace("60x60bb", f"{size}x{size}bb")

class AppleMusicMetadata:
    @classmethod
    def get_track(cls, track_id: str, country: str = "us") -> Optional[Dict[str, Any]]:
        params = {"id": track_id, "country": country, "entity": "song"}
        try:
            resp = requests.get(ITUNES_LOOKUP_URL, params=params, timeout=10)
            if not resp.ok:
                return None
            results = resp.json().get("results", [])
            if not results:
                return None
            
            # The item can be the song itself
            song = results[0]
            if song.get("wrapperType") == "collection" and len(results) > 1:
                song = results[1]

            title = song.get("trackName") or song.get("collectionName", "Unknown Song")
            artist = song.get("artistName", "Unknown Artist")
            album = song.get("collectionName", title)
            cover_url = get_highres_artwork(song.get("artworkUrl100", ""))
            duration_s = int(song.get("trackTimeMillis", 0) / 1000)
            track_num = song.get("trackNumber", 1)
            disc_num = song.get("discNumber", 1)
            release_date = song.get("releaseDate", "")[:10]
            genre = song.get("primaryGenreName", "")

            return {
                "id": str(song.get("trackId") or track_id),
                "service": "apple_music",
                "type": "track",
                "title": title,
                "artist": artist,
                "artists": [artist],
                "album": album,
                "cover_url": cover_url,
                "duration": duration_s,
                "track_number": track_num,
                "disc_number": disc_num,
                "release_date": release_date,
                "genre": genre,
                "source_url": song.get("trackViewUrl", ""),
                "preview_url": song.get("previewUrl", ""),
                "search_query": f"{artist} - {title} audio"
            }
        except Exception as e:
            print(f"[AppleMusic] Error fetching track {track_id}: {e}")
            return None

    @classmethod
    def get_album(cls, album_id: str, country: str = "us") -> Optional[Dict[str, Any]]:
        params = {"id": album_id, "country": country, "entity": "song"}
        try:
            resp = requests.get(ITUNES_LOOKUP_URL, params=params, timeout=10)
            if not resp.ok:
                return None
            results = resp.json().get("results", [])
            if not results:
                return None

            collection = results[0]
            album_title = collection.get("collectionName", "Unknown Album")
            artist_name = collection.get("artistName", "Unknown Artist")
            cover_url = get_highres_artwork(collection.get("artworkUrl100", ""))
            release_date = collection.get("releaseDate", "")[:10]
            genre = collection.get("primaryGenreName", "")

            tracks: List[Dict[str, Any]] = []
            for item in results[1:]:
                if item.get("wrapperType") == "track":
                    t_title = item.get("trackName", "Track")
                    t_artist = item.get("artistName", artist_name)
                    t_duration = int(item.get("trackTimeMillis", 0) / 1000)
                    t_id = str(item.get("trackId", len(tracks) + 1))
                    tracks.append({
                        "id": t_id,
                        "service": "apple_music",
                        "type": "track",
                        "title": t_title,
                        "artist": t_artist,
                        "artists": [t_artist],
                        "album": album_title,
                        "cover_url": cover_url,
                        "duration": t_duration,
                        "track_number": item.get("trackNumber", len(tracks) + 1),
                        "disc_number": item.get("discNumber", 1),
                        "release_date": release_date,
                        "genre": genre,
                        "source_url": item.get("trackViewUrl", ""),
                        "preview_url": item.get("previewUrl", ""),
                        "search_query": f"{t_artist} - {t_title} audio"
                    })

            return {
                "id": str(album_id),
                "service": "apple_music",
                "type": "album",
                "title": album_title,
                "artist": artist_name,
                "cover_url": cover_url,
                "release_date": release_date,
                "genre": genre,
                "track_count": len(tracks),
                "tracks": tracks,
                "source_url": collection.get("collectionViewUrl", "")
            }
        except Exception as e:
            print(f"[AppleMusic] Error fetching album {album_id}: {e}")
            return None

    @classmethod
    def search(cls, term: str, limit: int = 20, country: str = "us") -> List[Dict[str, Any]]:
        params = {"term": term, "media": "music", "entity": "song", "limit": limit, "country": country}
        tracks: List[Dict[str, Any]] = []
        try:
            resp = requests.get(ITUNES_SEARCH_URL, params=params, timeout=10)
            if not resp.ok:
                return []
            for item in resp.json().get("results", []):
                title = item.get("trackName", "")
                artist = item.get("artistName", "")
                tracks.append({
                    "id": str(item.get("trackId", "")),
                    "service": "apple_music",
                    "type": "track",
                    "title": title,
                    "artist": artist,
                    "album": item.get("collectionName", ""),
                    "cover_url": get_highres_artwork(item.get("artworkUrl100", "")),
                    "duration": int(item.get("trackTimeMillis", 0) / 1000),
                    "track_number": item.get("trackNumber", 1),
                    "disc_number": item.get("discNumber", 1),
                    "release_date": (item.get("releaseDate") or "")[:10],
                    "genre": item.get("primaryGenreName", ""),
                    "source_url": item.get("trackViewUrl", ""),
                    "preview_url": item.get("previewUrl", ""),
                    "search_query": f"{artist} - {title} audio"
                })
        except Exception as e:
            print(f"[AppleMusic] Error searching for '{term}': {e}")
        return tracks
