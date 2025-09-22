import {Component, inject, OnInit} from '@angular/core';
import {NgClass, NgFor, NgIf, NgOptimizedImage} from '@angular/common';
import {Router, RouterLink, RouterLinkActive} from '@angular/router';
import {Role} from '../../../models/Role';

interface NavItem {
  label: string;
  icon: string;
  link?: string;
  roles: Role[];
  class?: string;
  action?: () => void;
}

interface UserPlaylist {
  id: string;
  name: string;
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

  sidebarItems: NavItem[] = [
    {label: 'Home', icon: 'home', link: '/home', roles: ['User']},
    {label: 'Discovery', icon: 'explore', link: '/discovery', roles: ['User']},
    {label: 'Subscriptions', icon: 'subscriptions', link: '/subscriptions', roles: ['User']},
    {label: 'Create playlist', icon: 'playlist_add', link: '/create-playlist', roles: ['User']},
    {label: 'Artists', icon: 'artist', link: '/artists', roles: ['Admin']},
    {label: 'Albums', icon: 'album', link: '/albums', roles: ['Admin']},
    {label: 'Singles', icon: 'music_note', link: '/singles', roles: ['Admin']},
    {label: 'Logout', icon: 'logout', roles: ['Admin'], class: 'logout', action: () => this.logout()},
  ];

  userPlaylists: UserPlaylist[] = [
    {name: 'Awesome playlist 1', id: 'noid'},
    {name: 'Awesome playlist 2', id: 'noid'},
    {name: 'Awesome playlist 3', id: 'noid'},
    {name: 'Awesome playlist 4', id: 'noid'},
    {name: 'Awesome playlist 1', id: 'noid'},
    {name: 'Awesome playlist 2', id: 'noid'},
    {name: 'Awesome playlist 3', id: 'noid'},
    {name: 'Awesome playlist 4', id: 'noid'},
    {name: 'Awesome playlist 1', id: 'noid'},
    {name: 'Awesome playlist 2', id: 'noid'},
    {name: 'Awesome playlist 3', id: 'noid'},
    {name: 'Awesome playlist 4', id: 'noid'}
  ];

  ngOnInit() {

  }

  logout() {
    // logout
  }
}
