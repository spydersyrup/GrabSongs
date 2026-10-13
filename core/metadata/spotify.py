import requests
import json
import re
from typing import List, Dict, Any, Optional

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

class SpotifyMetadata:
    @staticmethod
    def _fetch_embed_data(item_type: str, item_id: str) -> Optional[Dict[str, Any]]:
        url = f"https://open.spotify.com/embed/{item_type}/{item_id}"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=12)
            if not resp.ok:
                return None
            m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', resp.text)
            if not m:
                return None
            data = json.loads(m.group(1))
            return data.get("props", {}).get("pageProps", {}).get("state", {}).get("data", {}).get("entity", {})
        except Exception as e:
            print(f"[Spotify] Error fetching embed for {item_type}/{item_id}: {e}")
            return None

    @staticmethod
    def _fetch_oembed(url: str) -> Optional[Dict[str, Any]]:
        try:
            oembed_url = f"https://open.spotify.com/oembed?url={url}"
            resp = requests.get(oembed_url, headers=HEADERS, timeout=8)
            if resp.ok:
                return resp.json()
        except Exception:
            pass
        return None

    @classmethod
    def get_track(cls, track_id: str) -> Optional[Dict[str, Any]]:
        entity = cls._fetch_embed_data("track", track_id)
        oembed = cls._fetch_oembed(f"https://open.spotify.com/track/{track_id}")

        title = ""
        artists = []
        album = ""
        cover_url = ""
        duration_ms = 0
        track_number = 1

        if entity:
            title = entity.get("name") or entity.get("title", "")
            artists_list = entity.get("artists", [])
            if artists_list:
                artists = [a.get("name") for a in artists_list if a.get("name")]
            elif entity.get("subtitle"):
                artists = [entity.get("subtitle")]
            
            album_info = entity.get("album", {})
            album = album_info.get("name", "")
            cover_url = entity.get("visualIdentity", {}).get("image", [{}])[0].get("url", "")
            if not cover_url:
                cover_url = entity.get("coverArt", {}).get("sources", [{}])[0].get("url", "")
            duration_ms = entity.get("duration", 0)

        if not title and oembed:
            title = oembed.get("title", "")
            if not cover_url:
                cover_url = oembed.get("thumbnail_url", "")

        if not artists and " - " in title:
            # Often oEmbed titles are formatted as "Title by Artist" or just "Title"
            parts = title.split(" - ", 1)
            title = parts[0].strip()
            artists = [parts[1].strip()]

        artist_str = ", ".join(artists) if artists else "Unknown Artist"

        return {
            "id": track_id,
            "service": "spotify",
            "type": "track",
            "title": title or "Unknown Title",
            "artist": artist_str,
            "artists": artists,
            "album": album or title,
            "cover_url": cover_url,
            "duration": int(duration_ms / 1000) if duration_ms else 0,
            "track_number": track_number,
            "disc_number": 1,
            "source_url": f"https://open.spotify.com/track/{track_id}",
            "search_query": f"{artist_str} - {title} audio"
        }

    @classmethod
    def get_album(cls, album_id: str) -> Optional[Dict[str, Any]]:
        entity = cls._fetch_embed_data("album", album_id)
        if not entity:
            return None

        album_title = entity.get("title") or entity.get("name", "")
        artist_name = entity.get("subtitle") or "Unknown Artist"
        cover_url = ""
        visual = entity.get("visualIdentity", {}).get("image", [])
        if visual:
            cover_url = visual[0].get("url", "")
        if not cover_url:
            covers = entity.get("coverArt", {}).get("sources", [])
            if covers:
                cover_url = covers[0].get("url", "")

        tracks: List[Dict[str, Any]] = []
        raw_tracks = entity.get("trackList", [])
        for idx, t in enumerate(raw_tracks, start=1):
            t_uri = t.get("uri", "")
            t_id = t_uri.split(":")[-1] if ":" in t_uri else f"album_t_{idx}"
            t_title = t.get("title", "")
            t_subtitle = t.get("subtitle") or artist_name
            t_duration_ms = t.get("duration", 0)

            tracks.append({
                "id": t_id,
                "service": "spotify",
                "type": "track",
                "title": t_title,
                "artist": t_subtitle,
                "artists": [a.strip() for a in t_subtitle.split(",")],
                "album": album_title,
                "cover_url": cover_url,
                "duration": int(t_duration_ms / 1000) if t_duration_ms else 0,
                "track_number": idx,
                "disc_number": 1,
                "source_url": f"https://open.spotify.com/track/{t_id}" if ":" in t_uri else f"https://open.spotify.com/album/{album_id}",
                "search_query": f"{t_subtitle} - {t_title} audio"
            })

        return {
            "id": album_id,
            "service": "spotify",
            "type": "album",
            "title": album_title,
            "artist": artist_name,
            "cover_url": cover_url,
            "track_count": len(tracks),
            "tracks": tracks,
            "source_url": f"https://open.spotify.com/album/{album_id}"
        }

    @classmethod
    def get_playlist(cls, playlist_id: str) -> Optional[Dict[str, Any]]:
        entity = cls._fetch_embed_data("playlist", playlist_id)
        if not entity:
            return None

        playlist_title = entity.get("title") or entity.get("name", "Spotify Playlist")
        author = entity.get("subtitle", "Spotify")
        cover_url = ""
        visual = entity.get("visualIdentity", {}).get("image", [])
        if visual:
            cover_url = visual[0].get("url", "")
        if not cover_url:
            covers = entity.get("coverArt", {}).get("sources", [])
            if covers:
                cover_url = covers[0].get("url", "")

        tracks: List[Dict[str, Any]] = []
        raw_tracks = entity.get("trackList", [])
        for idx, t in enumerate(raw_tracks, start=1):
            t_uri = t.get("uri", "")
            t_id = t_uri.split(":")[-1] if ":" in t_uri else f"playlist_t_{idx}"
            t_title = t.get("title", "")
            t_artist = t.get("subtitle", "Unknown Artist")
            t_duration_ms = t.get("duration", 0)

            tracks.append({
                "id": t_id,
                "service": "spotify",
                "type": "track",
                "title": t_title,
                "artist": t_artist,
                "artists": [a.strip() for a in t_artist.split(",")],
                "album": playlist_title,
                "cover_url": cover_url,
                "duration": int(t_duration_ms / 1000) if t_duration_ms else 0,
                "track_number": idx,
                "disc_number": 1,
                "source_url": f"https://open.spotify.com/track/{t_id}" if ":" in t_uri else f"https://open.spotify.com/playlist/{playlist_id}",
                "search_query": f"{t_artist} - {t_title} audio"
            })

        return {
            "id": playlist_id,
            "service": "spotify",
            "type": "playlist",
            "title": playlist_title,
            "artist": author,
            "cover_url": cover_url,
            "track_count": len(tracks),
            "tracks": tracks,
            "source_url": f"https://open.spotify.com/playlist/{playlist_id}"
        }

    @classmethod
    def search(cls, query: str, limit: int = 15) -> List[Dict[str, Any]]:
        # Searches metadata catalog and tags as Spotify format
        from .apple_music import AppleMusicMetadata
        raw_tracks = AppleMusicMetadata.search(query, limit=limit)
        spotify_tracks = []
        for t in raw_tracks:
            st = dict(t)
            st["service"] = "spotify"
            st["source_url"] = f"https://open.spotify.com/search/{query}"
            spotify_tracks.append(st)
        return spotify_tracks

