import re
from urllib.parse import urlparse

class ServiceDetector:
    SPOTIFY_TRACK = re.compile(r"open\.spotify\.com\/(?:intl-[a-z]+\/)?track\/([a-zA-Z0-9]+)")
    SPOTIFY_ALBUM = re.compile(r"open\.spotify\.com\/(?:intl-[a-z]+\/)?album\/([a-zA-Z0-9]+)")
    SPOTIFY_PLAYLIST = re.compile(r"open\.spotify\.com\/(?:intl-[a-z]+\/)?playlist\/([a-zA-Z0-9]+)")
    SPOTIFY_ARTIST = re.compile(r"open\.spotify\.com\/(?:intl-[a-z]+\/)?artist\/([a-zA-Z0-9]+)")

    APPLE_MUSIC = re.compile(r"music\.apple\.com\/([a-z]{2}\/)?(album|playlist|song|artist)\/([^/?]+)(?:\/(\d+))?(?:\?i=(\d+))?")

    DEEZER_TRACK = re.compile(r"deezer\.com\/(?:[a-z]{2}\/)?track\/(\d+)")
    DEEZER_ALBUM = re.compile(r"deezer\.com\/(?:[a-z]{2}\/)?album\/(\d+)")
    DEEZER_PLAYLIST = re.compile(r"deezer\.com\/(?:[a-z]{2}\/)?playlist\/(\d+)")

    YOUTUBE_WATCH = re.compile(r"(?:youtube\.com\/(?:watch\?.*v=|embed\/|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})")
    YOUTUBE_PLAYLIST = re.compile(r"(?:youtube\.com\/(?:playlist\?.*list=|watch\?.*list=))([a-zA-Z0-9_-]+)")
    YOUTUBE_MUSIC = re.compile(r"music\.youtube\.com\/(?:watch\?.*v=|playlist\?.*list=)([a-zA-Z0-9_-]+)")

    @classmethod
    def detect(cls, query: str):
        query = query.strip()
        if not query:
            return {"service": "empty", "type": "empty", "id": ""}

        # Spotify detection
        m = cls.SPOTIFY_TRACK.search(query)
        if m:
            return {"service": "spotify", "type": "track", "id": m.group(1), "url": query}
        m = cls.SPOTIFY_ALBUM.search(query)
        if m:
            return {"service": "spotify", "type": "album", "id": m.group(1), "url": query}
        m = cls.SPOTIFY_PLAYLIST.search(query)
        if m:
            return {"service": "spotify", "type": "playlist", "id": m.group(1), "url": query}
        m = cls.SPOTIFY_ARTIST.search(query)
        if m:
            return {"service": "spotify", "type": "artist", "id": m.group(1), "url": query}

        # Apple Music detection
        m = cls.APPLE_MUSIC.search(query)
        if m:
            country = m.group(1).replace('/', '') if m.group(1) else 'us'
            kind = m.group(2)
            name = m.group(3)
            album_id = m.group(4)
            song_id = m.group(5)
            # If ?i=ID is present, it's a specific song inside an album
            target_id = song_id if song_id else (album_id if album_id else name)
            item_type = "track" if song_id or kind == "song" else kind
            return {"service": "apple_music", "type": item_type, "id": target_id, "url": query, "country": country}

        # Deezer detection
        m = cls.DEEZER_TRACK.search(query)
        if m:
            return {"service": "deezer", "type": "track", "id": m.group(1), "url": query}
        m = cls.DEEZER_ALBUM.search(query)
        if m:
            return {"service": "deezer", "type": "album", "id": m.group(1), "url": query}
        m = cls.DEEZER_PLAYLIST.search(query)
        if m:
            return {"service": "deezer", "type": "playlist", "id": m.group(1), "url": query}

        # YouTube / YouTube Music detection
        m_list = cls.YOUTUBE_PLAYLIST.search(query)
        if m_list:
            return {"service": "youtube", "type": "playlist", "id": m_list.group(1), "url": query}
        m_vid = cls.YOUTUBE_WATCH.search(query)
        if m_vid:
            return {"service": "youtube", "type": "track", "id": m_vid.group(1), "url": query}
        if "music.youtube.com" in query:
            return {"service": "youtube", "type": "track", "id": query, "url": query}

        # If it starts with http/https but didn't match known music services
        if query.startswith("http://") or query.startswith("https://"):
            return {"service": "generic_url", "type": "unknown", "id": query, "url": query}

        # Otherwise treated as a search query
        return {"service": "search", "type": "query", "id": query, "query": query}
