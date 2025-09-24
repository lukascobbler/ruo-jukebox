export interface Genre {
  id: string;
  name: string;
  isSubscribed?: boolean; // this field should be missing when the admin requests a genre
}
