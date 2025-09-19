import {Component, inject, OnInit} from '@angular/core';
import { Router } from '@angular/router';
import { NgOptimizedImage } from '@angular/common';
import { FormBuilder, Validators, ReactiveFormsModule, FormGroup } from '@angular/forms';
import { MatFormField, MatLabel } from '@angular/material/form-field';
import { MatInput } from '@angular/material/input';
import {ToastrService} from '../../../services/toastr/toastr.service';


@Component({
  selector: 'app-login',
  standalone: true,
  imports: [NgOptimizedImage, MatFormField, MatInput, MatLabel, ReactiveFormsModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss'
})
export class LoginComponent implements OnInit {
  toast = inject(ToastrService);
  fb = inject(FormBuilder);
  router = inject(Router);
  loading = false;
  form!: FormGroup;

  ngOnInit(): void {
    this.form = this.fb.group({
      email: ['', [Validators.required]],
      password: ['', [Validators.required]],
    });
  }

  submit() {
    if (this.form.invalid) {
      this.toast.info('Check fields', 'Please enter a valid email and password.');
      return;
    }

    const { email, password } = this.form.value as { email: string; password: string };
  }

  goRegister() {
    this.router.navigate(['/register']);
  }

  private extractError(err: any): string {
    const msg =
      err?.error?.error ||
      err?.error?.message ||
      err?.message ||
      'Unexpected error. Please try again.';
    return typeof msg === 'string' ? msg : 'Unexpected error. Please try again.';
  }
}
