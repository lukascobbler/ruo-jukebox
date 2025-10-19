from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ArtistFromGenre:
    id: str
    name: str
    picture: Optional[str] = None


@dataclass
class AlbumFromGenre:
    id: str
    name: str
    artist: str
    picture: Optional[str] = None


@dataclass
class Genre:
    id: str
    name: str
    albums: List[AlbumFromGenre]
    artists: List[ArtistFromGenre]
