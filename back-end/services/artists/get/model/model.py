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
    pictureKey: Optional[str]
    pictureUrl: Optional[str]
    genres: List[GenreItem]
