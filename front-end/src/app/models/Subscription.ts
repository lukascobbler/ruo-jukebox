export interface Subscription {
  artists: { id: string; name: string; pictureKey?: string; pictureUrl?: string }[];
  genres:  { id: string; name: string }[];
}
