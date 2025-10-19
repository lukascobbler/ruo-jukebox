import { Routes } from '@angular/router';
import { HomeComponent } from './components/user/home/home.component';
import { GenresComponent } from './components/user/discovery/genres/genres.component';
import { MusicContentComponent } from './components/user/discovery/music-content/music-content.component';
import { SubscriptionsComponent } from './components/user/subscriptions/subscriptions.component';
import { AlbumComponent } from './components/user/entity-pages/album/album.component';
import { ArtistComponent } from './components/user/entity-pages/artist/artist.component';
import { PlaylistComponent } from './components/user/playlist/playlist.component';
import { SearchResultsComponent } from './components/user/search-results-page/search-results.component';
import { AllArtistsComponent } from './components/admin/artists/all-artists.component';
import { AllAlbumsComponent } from './components/admin/albums/all-albums/all-albums.component';
import { AllSinglesComponent } from './components/admin/singles/all-singles.component';
import { AlbumDetailsComponent } from './components/admin/albums/album-details/album-details.component';
import { RegistrationComponent } from './components/anonymous/registration/registration.component';
import { LoginComponent } from './components/anonymous/login/login.component';
import {loggedInGuard} from './services/auth/logged-in.guard';
import {anonymousGuard} from './services/auth/anonymous-guard.guard';

export const routes: Routes = [
  { path: 'home', component: HomeComponent, canActivate: [loggedInGuard] },
  { path: 'discovery', component: GenresComponent, canActivate: [loggedInGuard] },
  { path: 'genre/:id', component: MusicContentComponent, canActivate: [loggedInGuard] },
  { path: 'album/:id', component: AlbumComponent, canActivate: [loggedInGuard] },
  { path: 'single/:id', component: AlbumComponent, canActivate: [loggedInGuard] },
  { path: 'artist/:id', component: ArtistComponent, canActivate: [loggedInGuard] },
  { path: 'playlist/:id', component: PlaylistComponent, canActivate: [loggedInGuard] },
  { path: 'search/:query', component: SearchResultsComponent, canActivate: [loggedInGuard] },
  { path: 'subscriptions', component: SubscriptionsComponent, canActivate: [loggedInGuard] },
  { path: 'all-artists', component: AllArtistsComponent, canActivate: [loggedInGuard] },
  { path: 'all-albums', component: AllAlbumsComponent, canActivate: [loggedInGuard] },
  { path: 'edit-album/:id', component: AlbumDetailsComponent, canActivate: [loggedInGuard] },
  { path: 'all-singles', component: AllSinglesComponent, canActivate: [loggedInGuard] },
  { path: 'register', component: RegistrationComponent, canActivate: [anonymousGuard] },
  { path: 'login', component: LoginComponent, canActivate: [anonymousGuard] },
  { path: '**', redirectTo: 'home' },
];
