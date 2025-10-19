interface AlbumFromGenre {
  id: string;
  name: string;
  picture: File | null;
  artist: string;
}

interface ArtistFromGenre {
  id: string;
  name: string;
  picture: File | null;
}

export interface Genre {
  id: string;
  name: string;
  albums: AlbumFromGenre[];
  artists: ArtistFromGenre[];
}
