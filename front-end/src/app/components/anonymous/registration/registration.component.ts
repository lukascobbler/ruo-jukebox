import {Component, inject, OnInit} from '@angular/core';
import {MatFormField, MatLabel} from "@angular/material/form-field";
import {MatInput} from "@angular/material/input";
import {NgIf, NgOptimizedImage} from "@angular/common";
import {AbstractControl, FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, ValidatorFn, Validators} from '@angular/forms';
import {Router, RouterLink} from '@angular/router';
import {MatDatepicker, MatDatepickerInput, MatDatepickerToggle} from '@angular/material/datepicker';
import {ToastrService} from '../../../services/toastr/toastr.service';
import {MatFormFieldModule} from "@angular/material/form-field";
import {MatInputModule} from "@angular/material/input";
import {MatDatepickerModule} from "@angular/material/datepicker";
import {MatNativeDateModule} from "@angular/material/core";
import {MatButtonModule} from "@angular/material/button";
import {MatIconModule} from '@angular/material/icon';
import {AuthService} from '../../../services/auth/auth.service';

const passwordsMatch = (): ValidatorFn => {
  return (group: AbstractControl) => {
    const p = group.get('password')?.value ?? '';
    const r = group.get('repeatPassword')?.value ?? '';
    return p === r ? null : {passwordsMismatch: true};
  };
};

@Component({
  selector: 'app-registration',
  standalone: true,
  imports: [
    MatFormField,
    MatInput,
    MatLabel,
    NgOptimizedImage,
    NgIf,
    MatIconModule,
    FormsModule,
    ReactiveFormsModule,
    RouterLink,
    MatDatepickerInput,
    MatDatepickerToggle,
    MatDatepicker,
    MatFormFieldModule,
    MatInputModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatButtonModule,
  ],
  templateUrl: './registration.component.html',
  styleUrl: './registration.component.scss'
})
export class RegistrationComponent implements OnInit {
  toast = inject(ToastrService);
  fb = inject(FormBuilder);
  auth = inject(AuthService);
  router = inject(Router);
  submitted = false;
  loading = false;
  form!: FormGroup;

  ngOnInit(): void {
    this.form = this.fb.group({
      name: ['', Validators.required],
      surname: ['', Validators.required],
      username: ['', Validators.required],
      dateOfBirth: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6), Validators.maxLength(64)]],
    });
  }

  get emailCtrl() {
    return this.form.get('email')!;
  }

  get passwordCtrl() {
    return this.form.get('password')!;
  }

  get someRequiredMissing(): boolean {
    const v = this.form.value as Record<string, string>;
    console.log(v);
    return ['name', 'surname', 'username', 'email', 'password', 'dateOfBirth']
      .some(k => !v[k] || v[k].trim().length === 0);
  }

  get invalidEmailFormat(): boolean {
    const ctrl = this.emailCtrl;
    return !!ctrl.value && ctrl.hasError('email');
  }

  get badPasswordLength(): boolean {
    return this.passwordCtrl.hasError('minlength') || this.passwordCtrl.hasError('maxlength');
  }

  get passwordsDontMatch(): boolean {
    return this.form.hasError('passwordsMismatch');
  }

  async submit() {
    this.submitted = true;

    if (this.form.invalid) {
      this.toast.info('Fix form', 'Please resolve the issues listed below.');
      return;
    }

    const {name, surname, username, email, password, dateOfBirth} = this.form.value as {
      name: string; surname: string; username: string; email: string; password: string;
      dateOfBirth: string;
    };

    this.loading = true;
    this.auth.register({
      name, surname, username, email,
      password, dateOfBirth
    } as any).subscribe({
      next: () => {
        this.toast.success('Registered', 'Successfully registered.');
        this.router.navigate(['/login']);
        this.loading = false;
      },
      error: (err) => {
        const msg = err?.error?.error || err?.error?.message || err?.message || 'Unexpected error.';
        this.toast.error('Registration failed', msg);
        this.loading = false;
      },
      complete: () => this.loading = false
    });
  }

  goLogin() {
    this.router.navigate(['/login']);
  }
}
