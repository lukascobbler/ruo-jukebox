export interface GenreItem {
  genre_id: string;
  name: string;
  isSubscribed?: boolean; // this field should be missing when the admin requests a genre
}
