import requests
from typing import List, Dict, Any, Optional

DEEZER_API_BASE = "https://api.deezer.com"

class DeezerMetadata:
    @classmethod
    def get_track(cls, track_id: str) -> Optional[Dict[str, Any]]:
        url = f"{DEEZER_API_BASE}/track/{track_id}"
        try:
            resp = requests.get(url, timeout=10)
            if not resp.ok:
                return None
            data = resp.json()
            if "error" in data:
                return None

            title = data.get("title", "")
            artist = data.get("artist", {}).get("name", "Unknown Artist")
            album = data.get("album", {}).get("title", "")
            cover_url = data.get("album", {}).get("cover_xl") or data.get("album", {}).get("cover_big") or ""
            duration = data.get("duration", 0)
            track_num = data.get("track_position", 1)
            disc_num = data.get("disk_number", 1)
            release_date = data.get("release_date", "")
            isrc = data.get("isrc", "")

            return {
                "id": str(track_id),
                "service": "deezer",
                "type": "track",
                "title": title,
                "artist": artist,
                "artists": [artist],
                "album": album,
                "cover_url": cover_url,
                "duration": duration,
                "track_number": track_num,
                "disc_number": disc_num,
                "release_date": release_date,
                "isrc": isrc,
                "source_url": data.get("link", f"https://www.deezer.com/track/{track_id}"),
                "search_query": f"{artist} - {title} audio"
            }
        except Exception as e:
            print(f"[Deezer] Error fetching track {track_id}: {e}")
            return None

    @classmethod
    def get_album(cls, album_id: str) -> Optional[Dict[str, Any]]:
        url = f"{DEEZER_API_BASE}/album/{album_id}"
        try:
            resp = requests.get(url, timeout=10)
            if not resp.ok:
                return None
            data = resp.json()
            if "error" in data:
                return None

            album_title = data.get("title", "Unknown Album")
            artist_name = data.get("artist", {}).get("name", "Unknown Artist")
            cover_url = data.get("cover_xl") or data.get("cover_big") or ""
            release_date = data.get("release_date", "")
            genres = [g.get("name") for g in data.get("genres", {}).get("data", [])]
            genre = genres[0] if genres else ""

            raw_tracks = data.get("tracks", {}).get("data", [])
            tracks: List[Dict[str, Any]] = []
            for t in raw_tracks:
                t_title = t.get("title", "")
                t_artist = t.get("artist", {}).get("name", artist_name)
                tracks.append({
                    "id": str(t.get("id")),
                    "service": "deezer",
                    "type": "track",
                    "title": t_title,
                    "artist": t_artist,
                    "artists": [t_artist],
                    "album": album_title,
                    "cover_url": cover_url,
                    "duration": t.get("duration", 0),
                    "track_number": t.get("track_position", len(tracks) + 1),
                    "disc_number": t.get("disk_number", 1),
                    "release_date": release_date,
                    "genre": genre,
                    "source_url": t.get("link", ""),
                    "search_query": f"{t_artist} - {t_title} audio"
                })

            return {
                "id": str(album_id),
                "service": "deezer",
                "type": "album",
                "title": album_title,
                "artist": artist_name,
                "cover_url": cover_url,
                "release_date": release_date,
                "genre": genre,
                "track_count": len(tracks),
                "tracks": tracks,
                "source_url": data.get("link", f"https://www.deezer.com/album/{album_id}")
            }
        except Exception as e:
            print(f"[Deezer] Error fetching album {album_id}: {e}")
            return None

    @classmethod
    def get_playlist(cls, playlist_id: str) -> Optional[Dict[str, Any]]:
        url = f"{DEEZER_API_BASE}/playlist/{playlist_id}"
        try:
            resp = requests.get(url, timeout=10)
            if not resp.ok:
                return None
            data = resp.json()
            if "error" in data:
                return None

            title = data.get("title", "Deezer Playlist")
            creator = data.get("creator", {}).get("name", "Deezer")
            cover_url = data.get("picture_xl") or data.get("picture_big") or ""

            raw_tracks = data.get("tracks", {}).get("data", [])
            tracks: List[Dict[str, Any]] = []
            for idx, t in enumerate(raw_tracks, start=1):
                t_title = t.get("title", "")
                t_artist = t.get("artist", {}).get("name", "Unknown Artist")
                t_cover = t.get("album", {}).get("cover_xl") or cover_url
                tracks.append({
                    "id": str(t.get("id")),
                    "service": "deezer",
                    "type": "track",
                    "title": t_title,
                    "artist": t_artist,
                    "artists": [t_artist],
                    "album": t.get("album", {}).get("title", title),
                    "cover_url": t_cover,
                    "duration": t.get("duration", 0),
                    "track_number": idx,
                    "disc_number": 1,
                    "source_url": t.get("link", ""),
                    "search_query": f"{t_artist} - {t_title} audio"
                })

            return {
                "id": str(playlist_id),
                "service": "deezer",
                "type": "playlist",
                "title": title,
                "artist": creator,
                "cover_url": cover_url,
                "track_count": len(tracks),
                "tracks": tracks,
                "source_url": data.get("link", f"https://www.deezer.com/playlist/{playlist_id}")
            }
        except Exception as e:
            print(f"[Deezer] Error fetching playlist {playlist_id}: {e}")
            return None

    @classmethod
    def search(cls, query: str, limit: int = 25) -> List[Dict[str, Any]]:
        url = f"{DEEZER_API_BASE}/search"
        tracks: List[Dict[str, Any]] = []
        try:
            resp = requests.get(url, params={"q": query, "limit": limit}, timeout=10)
            if not resp.ok:
                return []
            for t in resp.json().get("data", []):
                t_title = t.get("title", "")
                t_artist = t.get("artist", {}).get("name", "")
                t_album = t.get("album", {}).get("title", "")
                t_cover = t.get("album", {}).get("cover_xl") or t.get("album", {}).get("cover_big") or ""
                tracks.append({
                    "id": str(t.get("id")),
                    "service": "deezer",
                    "type": "track",
                    "title": t_title,
                    "artist": t_artist,
                    "artists": [t_artist],
                    "album": t_album,
                    "cover_url": t_cover,
                    "duration": t.get("duration", 0),
                    "track_number": t.get("track_position", 1),
                    "disc_number": t.get("disk_number", 1),
                    "source_url": t.get("link", ""),
                    "search_query": f"{t_artist} - {t_title} audio"
                })
        except Exception as e:
            print(f"[Deezer] Search error for '{query}': {e}")

        # If Deezer public API returned no results (e.g. region-restricted), fall back to metadata catalog
        if not tracks:
            from .apple_music import AppleMusicMetadata
            raw = AppleMusicMetadata.search(query, limit=limit)
            for t in raw:
                dt = dict(t)
                dt["service"] = "deezer"
                tracks.append(dt)

        return tracks
