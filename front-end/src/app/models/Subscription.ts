export interface Subscription {
  artists: { artist_id: string; name: string; pictureKey?: string; pictureUrl?: string }[];
  genres:  { genre_id: string; name: string }[];
}
