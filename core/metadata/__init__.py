from typing import Dict, Any, List
from .detector import ServiceDetector
from .spotify import SpotifyMetadata
from .apple_music import AppleMusicMetadata
from .deezer import DeezerMetadata
from .youtube import YouTubeMetadata
from .generic import GenericMetadata
from .lyrics import LyricsFetcher

class MetadataResolver:
    @classmethod
    def resolve(cls, query_or_url: str, target_service: str = "all") -> Dict[str, Any]:
        detected = ServiceDetector.detect(query_or_url)
        service = detected.get("service")
        item_type = detected.get("type")
        item_id = detected.get("id")

        if service == "empty":
            return {"success": False, "error": "Query or URL cannot be empty."}

        # 1. Spotify URL
        if service == "spotify":
            if item_type == "track":
                track = SpotifyMetadata.get_track(item_id)
                if track:
                    return {"success": True, "service": service, "type": "track", "item": track, "tracks": [track]}
            elif item_type == "album":
                album = SpotifyMetadata.get_album(item_id)
                if album:
                    return {"success": True, "service": service, "type": "album", "item": album, "tracks": album.get("tracks", [])}
            elif item_type in ("playlist", "artist"):
                playlist = SpotifyMetadata.get_playlist(item_id)
                if playlist:
                    return {"success": True, "service": service, "type": "playlist", "item": playlist, "tracks": playlist.get("tracks", [])}

        # 2. Apple Music URL
        elif service == "apple_music":
            country = detected.get("country", "us")
            if item_type == "track":
                track = AppleMusicMetadata.get_track(item_id, country=country)
                if track:
                    return {"success": True, "service": service, "type": "track", "item": track, "tracks": [track]}
            elif item_type in ("album", "playlist", "artist"):
                album = AppleMusicMetadata.get_album(item_id, country=country)
                if album:
                    return {"success": True, "service": service, "type": "album", "item": album, "tracks": album.get("tracks", [])}

        # 3. Deezer URL
        elif service == "deezer":
            if item_type == "track":
                track = DeezerMetadata.get_track(item_id)
                if track:
                    return {"success": True, "service": service, "type": "track", "item": track, "tracks": [track]}
            elif item_type == "album":
                album = DeezerMetadata.get_album(item_id)
                if album:
                    return {"success": True, "service": service, "type": "album", "item": album, "tracks": album.get("tracks", [])}
            elif item_type in ("playlist", "artist"):
                playlist = DeezerMetadata.get_playlist(item_id)
                if playlist:
                    return {"success": True, "service": service, "type": "playlist", "item": playlist, "tracks": playlist.get("tracks", [])}

        # 4. YouTube URL
        elif service == "youtube":
            if item_type == "track":
                track = YouTubeMetadata.get_track(detected.get("url") or item_id)
                if track:
                    return {"success": True, "service": service, "type": "track", "item": track, "tracks": [track]}
            elif item_type == "playlist":
                playlist = YouTubeMetadata.get_playlist(detected.get("url"))
                if playlist:
                    return {"success": True, "service": service, "type": "playlist", "item": playlist, "tracks": playlist.get("tracks", [])}

        # 5. Generic URL (SoundCloud, Bandcamp, TikTok, direct stream, etc.)
        elif service in ("generic_url", "generic"):
            gen_res = GenericMetadata.resolve_url(detected.get("url") or query_or_url)
            if gen_res.get("success"):
                return gen_res

        # 5. Fall back to a text search, but only when the input actually was
        # one. A recognised provider link that produced nothing means that
        # provider failed, not that the query was wrong - searching YouTube and
        # Apple Music for the literal URL text burns two requests on noise and
        # then reports "not found" for a track that does exist.
        if service != "search":
            label = {"apple_music": "Apple Music", "generic_url": "this link"}.get(service, service)
            return {
                "success": False,
                "error": f"Could not read {label}. The provider may have changed or be temporarily unreachable."
            }

        search_query = detected.get("query") or query_or_url
        tracks = []
        target = (target_service or "all").lower()

        if target in ("youtube", "yt"):
            tracks = YouTubeMetadata.search(search_query, limit=20)
        elif target in ("spotify", "sp"):
            tracks = SpotifyMetadata.search(search_query, limit=20)
        elif target in ("apple", "apple_music"):
            tracks = AppleMusicMetadata.search(search_query, limit=20)
        elif target in ("deezer", "dz"):
            tracks = DeezerMetadata.search(search_query, limit=20)
        else:
            # "all": Search Apple Music high-res catalog + YouTube and combine
            apple_tracks = AppleMusicMetadata.search(search_query, limit=12)
            yt_tracks = YouTubeMetadata.search(search_query, limit=10)
            tracks = apple_tracks + yt_tracks

        if tracks:
            return {
                "success": True,
                "service": target_service,
                "type": "search_results",
                "query": search_query,
                "tracks": tracks
            }

        return {"success": False, "error": f"Could not find or resolve: {query_or_url}"}
