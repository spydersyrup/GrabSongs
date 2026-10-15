import yt_dlp
from typing import Dict, Any, List

class GenericMetadata:
    @classmethod
    def resolve_url(cls, url: str) -> Dict[str, Any]:
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'extract_flat': True,
            'no_warnings': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info:
                    return {"success": False, "error": "Could not extract stream info from URL."}

                # Check if it's a playlist or multiple entries
                if 'entries' in info and info['entries']:
                    tracks = []
                    for entry in info['entries']:
                        if not entry:
                            continue
                        tracks.append(cls._normalize_entry(entry, url))
                    return {
                        "success": True,
                        "service": "generic",
                        "type": "playlist",
                        "item": {
                            "title": info.get("title") or "Generic Playlist",
                            "artist": info.get("uploader") or info.get("channel") or "Various Artists",
                            "cover_url": info.get("thumbnail") or "",
                            "track_count": len(tracks)
                        },
                        "tracks": tracks
                    }
                else:
                    track = cls._normalize_entry(info, url)
                    return {
                        "success": True,
                        "service": "generic",
                        "type": "track",
                        "item": track,
                        "tracks": [track]
                    }
        except Exception as e:
            return {"success": False, "error": f"Generic extraction failed: {str(e)}"}

    @staticmethod
    def _normalize_entry(entry: Dict[str, Any], source_url: str) -> Dict[str, Any]:
        duration = int(entry.get("duration") or 0)
        mins = duration // 60
        secs = duration % 60
        duration_str = f"{mins}:{secs:02d}"

        title = entry.get("track") or entry.get("title") or "Unknown Title"
        artist = entry.get("artist") or entry.get("uploader") or entry.get("channel") or "Unknown Artist"

        return {
            "id": str(entry.get("id") or ""),
            "title": title,
            "artist": artist,
            "album": entry.get("album") or title,
            "duration": duration,
            "duration_str": duration_str,
            "cover_url": entry.get("thumbnail") or "",
            "service": "generic",
            "source_url": entry.get("webpage_url") or entry.get("url") or source_url,
            "has_lyrics": False
        }
