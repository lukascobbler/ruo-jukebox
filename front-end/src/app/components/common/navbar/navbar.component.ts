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
    {label: 'Signed certificates', icon: 'library_books', link: '/signed-certificates', roles: ['User']},
    {label: 'Certificate requests', icon: 'stacks', link: '/certificate-requests', roles: ['User']},
    {label: 'All certificates', icon: 'library_books', link: '/all-certificates', roles: ['User']},
    {label: 'Issue a certificate', icon: 'add_notes', link: '/issue-certificate', roles: ['User']},
    {label: 'My certificates', icon: 'library_books', link: '/my-certificates', roles: ['User']},
    {label: 'Request Certificate', icon: 'add_notes', link: '/request-certificate', roles: ['User']},
    {label: 'Manage CA users', icon: 'group', link: '/manage-ca-users', roles: ['User']},
    {label: 'Logout', icon: 'logout', roles: ['Admin'], class: 'logout', action: () => this.logout()},
  ];

  ngOnInit() {

  }

  logout() {
    // logout
  }
}
