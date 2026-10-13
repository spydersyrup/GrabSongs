import yt_dlp
from typing import List, Dict, Any, Optional

class YouTubeMetadata:
    @classmethod
    def get_track(cls, url_or_id: str) -> Optional[Dict[str, Any]]:
        ydl_opts = {
            'extract_flat': True,
            'skip_download': True,
            'quiet': True,
            'no_warnings': True,
        }
        url = url_or_id if url_or_id.startswith("http") else f"https://www.youtube.com/watch?v=url_or_id"
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info:
                    return None
                title = info.get("title", "Unknown Title")
                uploader = info.get("uploader") or info.get("channel") or "Unknown Artist"
                thumbnail = info.get("thumbnail", "")
                duration = info.get("duration", 0)

                # Try to clean artist and title if formatted like "Artist - Title"
                artist = uploader
                track_title = title
                if " - " in title:
                    parts = title.split(" - ", 1)
                    artist = parts[0].strip()
                    track_title = parts[1].strip()

                return {
                    "id": info.get("id", ""),
                    "service": "youtube",
                    "type": "track",
                    "title": track_title,
                    "artist": artist,
                    "artists": [artist],
                    "album": info.get("album") or "YouTube",
                    "cover_url": thumbnail,
                    "duration": duration,
                    "track_number": 1,
                    "disc_number": 1,
                    "source_url": info.get("webpage_url") or url,
                    "search_query": f"{artist} - {track_title}"
                }
        except Exception as e:
            print(f"[YouTube] Error extracting track: {e}")
            return None

    @classmethod
    def get_playlist(cls, url: str) -> Optional[Dict[str, Any]]:
        ydl_opts = {
            'extract_flat': True,
            'skip_download': True,
            'quiet': True,
            'no_warnings': True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info:
                    return None

                playlist_title = info.get("title", "YouTube Playlist")
                uploader = info.get("uploader") or "YouTube"
                entries = info.get("entries", [])
                tracks: List[Dict[str, Any]] = []

                for idx, entry in enumerate(entries, start=1):
                    if not entry:
                        continue
                    e_title = entry.get("title", "Track")
                    e_uploader = entry.get("uploader") or uploader
                    e_id = entry.get("id", f"yt_{idx}")
                    e_thumb = entry.get("thumbnail") or (entry.get("thumbnails", [{}])[-1].get("url") if entry.get("thumbnails") else "")
                    
                    e_artist = e_uploader
                    if " - " in e_title:
                        parts = e_title.split(" - ", 1)
                        e_artist = parts[0].strip()
                        e_title = parts[1].strip()

                    tracks.append({
                        "id": e_id,
                        "service": "youtube",
                        "type": "track",
                        "title": e_title,
                        "artist": e_artist,
                        "artists": [e_artist],
                        "album": playlist_title,
                        "cover_url": e_thumb,
                        "duration": entry.get("duration", 0),
                        "track_number": idx,
                        "disc_number": 1,
                        "source_url": entry.get("url") or f"https://www.youtube.com/watch?v={e_id}",
                        "search_query": f"{e_artist} - {e_title}"
                    })

                return {
                    "id": info.get("id", ""),
                    "service": "youtube",
                    "type": "playlist",
                    "title": playlist_title,
                    "artist": uploader,
                    "cover_url": info.get("thumbnails", [{}])[-1].get("url") if info.get("thumbnails") else "",
                    "track_count": len(tracks),
                    "tracks": tracks,
                    "source_url": url
                }
        except Exception as e:
            print(f"[YouTube] Error extracting playlist: {e}")
            return None
