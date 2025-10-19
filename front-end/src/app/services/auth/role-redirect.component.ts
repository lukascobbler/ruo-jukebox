import {Component, inject, OnInit} from '@angular/core';
import {Router} from '@angular/router';
import {AuthService} from './auth.service';
import {Role} from '../../models/Role';

@Component({
  selector: 'app-role-redirect',
  template: '',
  standalone: true
})
export class RoleRedirectComponent implements OnInit {
  authService = inject(AuthService);
  router = inject(Router);

  ngOnInit() {
    const role: Role | null = this.authService.getCurrentRole();

    if (role === 'Admin')
      this.router.navigate(['/all-artists']);
    else if (role === 'User')
      this.router.navigate(['/home']);
    else
      this.router.navigate(['/login']);
  }
}

