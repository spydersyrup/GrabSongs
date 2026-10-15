"""Manual smoke check: resolve a real track from every provider.

This hits the live network and asserts nothing, so it is not part of the test
suite (see tests/). Its job is the thing unit tests cannot do: notice when a
provider stops answering. Spotify is scraped rather than called, so a change to
that page's shape shows up here first and nowhere else.

Run from the repo root:  python scripts/smoke_providers.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.metadata import MetadataResolver

print("1. Testing YouTube query...")
res_yt = MetadataResolver.resolve("Mo City Flexologist", "youtube")
tracks_yt = res_yt.get("tracks", [])
print(f"YouTube tracks found: {len(tracks_yt)}")
if tracks_yt:
    print(f"Top YouTube track: {tracks_yt[0].get('title')} by {tracks_yt[0].get('artist')}")

print("\n2. Testing Spotify query...")
res_sp = MetadataResolver.resolve("Mo City Flexologist", "spotify")
tracks_sp = res_sp.get("tracks", [])
print(f"Spotify tracks found: {len(tracks_sp)}")
if tracks_sp:
    print(f"Top Spotify track: {tracks_sp[0].get('title')} by {tracks_sp[0].get('artist')}")

print("\n3. Testing Apple Music query...")
res_ap = MetadataResolver.resolve("Mo City Flexologist", "apple")
tracks_ap = res_ap.get("tracks", [])
print(f"Apple tracks found: {len(tracks_ap)}")
if tracks_ap:
    print(f"Top Apple track: {tracks_ap[0].get('title')} by {tracks_ap[0].get('artist')}")

print("\n4. Testing Deezer query...")
res_dz = MetadataResolver.resolve("Mo City Flexologist", "deezer")
tracks_dz = res_dz.get("tracks", [])
print(f"Deezer tracks found: {len(tracks_dz)}")
if tracks_dz:
    print(f"Top Deezer track: {tracks_dz[0].get('title')} by {tracks_dz[0].get('artist')}")

print("\n5. Testing Spotify Playlist URL extraction...")
sp_url = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M" # Today's Top Hits
res_sp_url = MetadataResolver.resolve(sp_url)
print(f"Spotify playlist tracks found: {len(res_sp_url.get('tracks', []))}")

print("\n6. Testing Apple Music URL extraction...")
ap_url = "https://music.apple.com/us/album/starboy/1440871441"
res_ap_url = MetadataResolver.resolve(ap_url)
print(f"Apple album tracks found: {len(res_ap_url.get('tracks', []))}")
