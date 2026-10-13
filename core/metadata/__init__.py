from typing import Dict, Any, List
from .detector import ServiceDetector
from .spotify import SpotifyMetadata
from .apple_music import AppleMusicMetadata
from .deezer import DeezerMetadata
from .youtube import YouTubeMetadata
from .lyrics import LyricsFetcher

class MetadataResolver:
    @classmethod
    def resolve(cls, query_or_url: str) -> Dict[str, Any]:
        detected = ServiceDetector.detect(query_or_url)
        service = detected.get("service")
        item_type = detected.get("type")
        item_id = detected.get("id")

        if service == "empty":
            return {"success": False, "error": "Query or URL cannot be empty."}

        # 1. Spotify
        if service == "spotify":
            if item_type == "track":
                track = SpotifyMetadata.get_track(item_id)
                if track:
                    return {"success": True, "service": service, "type": "track", "item": track, "tracks": [track]}
            elif item_type == "album":
                album = SpotifyMetadata.get_album(item_id)
                if album:
                    return {"success": True, "service": service, "type": "album", "item": album, "tracks": album.get("tracks", [])}
            elif item_type == "playlist":
                playlist = SpotifyMetadata.get_playlist(item_id)
                if playlist:
                    return {"success": True, "service": service, "type": "playlist", "item": playlist, "tracks": playlist.get("tracks", [])}

        # 2. Apple Music
        elif service == "apple_music":
            country = detected.get("country", "us")
            if item_type == "track":
                track = AppleMusicMetadata.get_track(item_id, country=country)
                if track:
                    return {"success": True, "service": service, "type": "track", "item": track, "tracks": [track]}
            elif item_type in ("album", "playlist"):
                album = AppleMusicMetadata.get_album(item_id, country=country)
                if album:
                    return {"success": True, "service": service, "type": "album", "item": album, "tracks": album.get("tracks", [])}

        # 3. Deezer
        elif service == "deezer":
            if item_type == "track":
                track = DeezerMetadata.get_track(item_id)
                if track:
                    return {"success": True, "service": service, "type": "track", "item": track, "tracks": [track]}
            elif item_type == "album":
                album = DeezerMetadata.get_album(item_id)
                if album:
                    return {"success": True, "service": service, "type": "album", "item": album, "tracks": album.get("tracks", [])}
            elif item_type == "playlist":
                playlist = DeezerMetadata.get_playlist(item_id)
                if playlist:
                    return {"success": True, "service": service, "type": "playlist", "item": playlist, "tracks": playlist.get("tracks", [])}

        # 4. YouTube
        elif service == "youtube":
            if item_type == "track":
                track = YouTubeMetadata.get_track(detected.get("url") or item_id)
                if track:
                    return {"success": True, "service": service, "type": "track", "item": track, "tracks": [track]}
            elif item_type == "playlist":
                playlist = YouTubeMetadata.get_playlist(detected.get("url"))
                if playlist:
                    return {"success": True, "service": service, "type": "playlist", "item": playlist, "tracks": playlist.get("tracks", [])}

        # 5. Search query (fallback / direct text search)
        # Search via iTunes and Deezer for best metadata results
        search_query = detected.get("query") or query_or_url
        tracks = AppleMusicMetadata.search(search_query, limit=15)
        if not tracks:
            tracks = DeezerMetadata.search(search_query, limit=15)

        if tracks:
            return {
                "success": True,
                "service": "search",
                "type": "search_results",
                "query": search_query,
                "tracks": tracks
            }

        return {"success": False, "error": f"Could not find or resolve: {query_or_url}"}
