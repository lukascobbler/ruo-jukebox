export interface Subscription {
  artists: { id: string; name: string; pictureUrl?: string }[];
  genres:  { id: string; name: string }[];
}
