from dataclasses import dataclass
from typing import List, Optional

@dataclass
class GenreItem:
    id: str
    name: str

@dataclass
class Artist:
    id: str
    name: str
    biography: str
    genres: List[GenreItem]
    pictureKey: Optional[str] = None
    pictureUrl: Optional[str] = None
