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
import {authGuard, noAuthGuard, roleGuard} from './services/auth/auth.guard';
import {RoleRedirectComponent} from './services/auth/role-redirect.component';
import {Role} from './models/Role';
import {SingleComponent} from './components/user/entity-pages/single/single.component';

export const routes: Routes = [
  // Anonymous
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  { path: 'register', component: RegistrationComponent, canActivate: [noAuthGuard] },
  { path: 'login', component: LoginComponent, canActivate: [noAuthGuard] },

  // User
  { path: 'home', component: HomeComponent, canActivate: [authGuard, roleGuard], data: { roles: ['User'] as Role[] } },
  { path: 'discovery', component: GenresComponent, canActivate: [authGuard, roleGuard], data: { roles: ['User'] as Role[] } },
  { path: 'genre/:id', component: MusicContentComponent, canActivate: [authGuard, roleGuard], data: { roles: ['User'] as Role[] } },
  { path: 'album/:id', component: AlbumComponent, canActivate: [authGuard, roleGuard], data: { roles: ['User'] as Role[] } },
  { path: 'single/:id', component: SingleComponent, canActivate: [authGuard, roleGuard], data: { roles: ['User'] as Role[] } },
  { path: 'artist/:id', component: ArtistComponent, canActivate: [authGuard, roleGuard], data: { roles: ['User'] as Role[] } },
  { path: 'playlist/:id', component: PlaylistComponent, canActivate: [authGuard, roleGuard], data: { roles: ['User'] as Role[] } },
  { path: 'search/:query', component: SearchResultsComponent, canActivate: [authGuard, roleGuard], data: { roles: ['User'] as Role[] } },
  { path: 'subscriptions', component: SubscriptionsComponent, canActivate: [authGuard, roleGuard], data: { roles: ['User'] as Role[] } },

  // Admin
  { path: 'all-artists', component: AllArtistsComponent, canActivate: [authGuard, roleGuard], data: { roles: ['Admin'] as Role[] } },
  { path: 'all-albums', component: AllAlbumsComponent, canActivate: [authGuard, roleGuard], data: { roles: ['Admin'] as Role[] }  },
  { path: 'album-details', component: AlbumDetailsComponent, canActivate: [authGuard, roleGuard], data: { roles: ['Admin'] as Role[] }  },
  { path: 'all-singles', component: AllSinglesComponent, canActivate: [authGuard, roleGuard], data: { roles: ['Admin'] as Role[] }  },

  // misc
  { path: '**', component: RoleRedirectComponent, canActivate: [authGuard] },
];
