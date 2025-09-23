import {Component, inject, OnInit} from '@angular/core';
import {NgClass, NgFor, NgIf, NgOptimizedImage} from '@angular/common';
import {Router, RouterLink, RouterLinkActive} from '@angular/router';
import {Role} from '../../../models/Role';
import {MatDialog, MatDialogRef} from '@angular/material/dialog';
import {CreatePlaylistDialogComponent} from '../../user/dialogs/create-playlist/create-playlist-dialog.component';
import {Playlist} from '../../../models/Playlist';

interface NavItem {
  label: string;
  icon: string;
  link?: string;
  roles: Role[];
  class?: string;
  action?: () => void;
}

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [
    NgIf,
    RouterLink,
    RouterLinkActive,
    NgOptimizedImage,
    NgClass,
    NgFor
  ],
  templateUrl: './navbar.component.html',
  styleUrl: './navbar.component.scss'
})
export class NavbarComponent implements OnInit {
  private router = inject(Router);
  currentUserRole: Role | null = "User";

  constructor(private dialog: MatDialog) {
  }

  sidebarItems: NavItem[] = [
    {label: 'Home', icon: 'home', link: '/home', roles: ['User']},
    {label: 'Discovery', icon: 'explore', link: '/discovery', roles: ['User']},
    {label: 'Subscriptions', icon: 'subscriptions', link: '/subscriptions', roles: ['User']},
    {label: 'Create playlist', icon: 'playlist_add', action: () => this.createPlaylist(), roles: ['User']},
    {label: 'Artists', icon: 'artist', link: '/artists', roles: ['Admin']},
    {label: 'Albums', icon: 'album', link: '/albums', roles: ['Admin']},
    {label: 'Singles', icon: 'music_note', link: '/singles', roles: ['Admin']},
    {label: 'Logout', icon: 'logout', roles: ['Admin'], class: 'logout', action: () => this.logout()},
  ];

  userPlaylists: Playlist[] = [
    {name: 'Awesome playlist 1', id: '1'},
    {name: 'Awesome playlist 2', id: '2'},
    {name: 'Awesome playlist 3', id: '3'},
    {name: 'Awesome playlist 4', id: '4'},
    {name: 'Awesome playlist 5', id: '5'},
    {name: 'Awesome playlist 6', id: '6'},
    {name: 'Awesome playlist 7', id: '7'},
    {name: 'Awesome playlist 8', id: '8'},
    {name: 'Awesome playlist 9', id: '9'},
    {name: 'Awesome playlist 10', id: '10'},
    {name: 'Awesome playlist 11', id: '11'},
    {name: 'Awesome playlist 12', id: '12'}
  ];

  ngOnInit() {

  }

  logout() {
    // logout
  }

  createPlaylist() {
    const dialogRef: MatDialogRef<CreatePlaylistDialogComponent, null> = this.dialog.open(CreatePlaylistDialogComponent, {
      width: '30rem'
    });
  }
}
