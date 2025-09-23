import { Routes } from '@angular/router';
import {HomeComponent} from './components/user/home/home.component';
import {GenresComponent} from './components/user/discovery/genres/genres.component';
import {MusicContentComponent} from './components/user/discovery/music-content/music-content.component';
import {SubscriptionsComponent} from './components/user/subscriptions/subscriptions.component';
import {AlbumComponent} from './components/user/entity-pages/album/album.component';
import {ArtistComponent} from './components/user/entity-pages/artist/artist.component';
import {PlaylistComponent} from './components/user/playlist/playlist.component';
import {SearchResultsComponent} from './components/user/search-results-page/search-results.component';

export const routes: Routes = [
  {path: "home", component: HomeComponent},
  {path: "discovery", component: GenresComponent},
  {path: "genre/:id", component: MusicContentComponent},
  {path: "album/:id", component: AlbumComponent},
  {path: "single/:id", component: AlbumComponent},
  {path: "artist/:id", component: ArtistComponent},
  {path: "playlist/:id", component: PlaylistComponent},
  {path: "search/:query", component: SearchResultsComponent},
  {path: "subscriptions", component: SubscriptionsComponent}
];
