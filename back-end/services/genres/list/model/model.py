from dataclasses import dataclass


@dataclass
class GenreItem:
    id: str
    name: str
    isSubscribed: bool | None
